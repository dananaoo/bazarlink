export type UserRole = 'owner' | 'manager';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  supplierId: string;
  createdAt: string;
}

export interface Supplier {
  id: string;
  name: string;
  description: string;
  ownerId: string;
  contactEmail: string;
  contactPhone: string;
  address: string;
  createdAt: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  supplierId: string;
  imageUrl?: string;
  imageUrl?: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  categoryId: string;
  price: number;
  unit: string;
  stock: number;
  discount: number;
  supplierId: string;
  imageUrl?: string;
  leadTime: string;
  deliveryAvailable: boolean;
  pickupAvailable: boolean;
}

export interface LinkRequest {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  supplierId: string;
  status: 'pending' | 'approved' | 'rejected' | 'blocked';
  requestedAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
}

export interface Order {
  id: string;
  consumerId: string;
  consumerName: string;
  supplierId: string;
  items: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'accepted' | 'rejected' | 'completed';
  createdAt: string;
}

export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  price: number;
}