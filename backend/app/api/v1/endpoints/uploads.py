"""
File upload endpoints for chat attachments
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.config import settings
from app.models.user import UserRole
from app.models.link import Link, LinkStatus

router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create subdirectories for different file types
IMAGES_DIR = UPLOAD_DIR / "images"
DOCUMENTS_DIR = UPLOAD_DIR / "documents"
AUDIO_DIR = UPLOAD_DIR / "audio"
VIDEO_DIR = UPLOAD_DIR / "videos"

for directory in [IMAGES_DIR, DOCUMENTS_DIR, AUDIO_DIR, VIDEO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def get_file_category(content_type: str) -> str:
    """Determine file category based on content type"""
    if content_type.startswith("image/"):
        return "images"
    elif content_type.startswith("audio/"):
        return "audio"
    elif content_type.startswith("video/"):
        return "videos"
    else:
        return "documents"


def get_upload_directory(category: str) -> Path:
    """Get the upload directory for a file category"""
    directories = {
        "images": IMAGES_DIR,
        "audio": AUDIO_DIR,
        "videos": VIDEO_DIR,
        "documents": DOCUMENTS_DIR
    }
    return directories.get(category, DOCUMENTS_DIR)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    link_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Upload a file for chat attachment
    
    - **file**: The file to upload (image, document, or audio)
    - **link_id**: Optional link ID to verify access (if provided)
    
    Returns the file URL that can be used in messages.
    """
    # Verify user has permission to upload (consumers and sales reps)
    if current_user.role not in [UserRole.CONSUMER, UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers and supplier staff can upload files"
        )
    
    # If link_id is provided, verify access
    if link_id:
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        if current_user.role == UserRole.CONSUMER:
            if link.consumer_id != current_user.consumer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this link"
                )
        elif current_user.role in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
            if link.supplier_id != current_user.supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this link"
                )
        
        if link.status != LinkStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Link must be accepted before uploading files"
            )
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' is not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file size
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({settings.MAX_FILE_SIZE} bytes)"
        )
    
    # Determine file category and directory
    category = get_file_category(file.content_type)
    upload_dir = get_upload_directory(category)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Generate file URL (relative path for API)
    file_url = f"/api/v1/uploads/files/{category}/{unique_filename}"
    
    # Determine attachment type for message
    attachment_type = category  # images, audio, documents, videos
    
    return {
        "file_url": file_url,
        "attachment_type": attachment_type,
        "content_type": file.content_type,
        "file_size": file_size,
        "filename": file.filename
    }


@router.get("/files/{category}/{filename}")
async def get_file(
    category: str,
    filename: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve an uploaded file
    
    - **category**: File category (images, audio, documents, videos)
    - **filename**: The filename to retrieve
    """
    # Verify user is authenticated
    if current_user.role not in [UserRole.CONSUMER, UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Validate category
    valid_categories = ["images", "audio", "documents", "videos"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Get file path
    upload_dir = get_upload_directory(category)
    file_path = upload_dir / filename
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine media type
    media_type = "application/octet-stream"
    if category == "images":
        if filename.lower().endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        elif filename.lower().endswith(".png"):
            media_type = "image/png"
        elif filename.lower().endswith(".gif"):
            media_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            media_type = "image/webp"
    elif category == "audio":
        if filename.lower().endswith((".mp3", ".mpeg")):
            media_type = "audio/mpeg"
        elif filename.lower().endswith(".wav"):
            media_type = "audio/wav"
        elif filename.lower().endswith(".ogg"):
            media_type = "audio/ogg"
        elif filename.lower().endswith(".aac"):
            media_type = "audio/aac"
    elif category == "videos":
        if filename.lower().endswith(".mp4"):
            media_type = "video/mp4"
        elif filename.lower().endswith(".webm"):
            media_type = "video/webm"
    elif category == "documents":
        if filename.lower().endswith(".pdf"):
            media_type = "application/pdf"
        elif filename.lower().endswith(".doc"):
            media_type = "application/msword"
        elif filename.lower().endswith(".docx"):
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename
    )

