# Supplier Management Web App (SvelteKit)

This is a Supplier Management Web Application built with SvelteKit, TypeScript, and Tailwind CSS. The application allows suppliers to manage their catalog, orders, team members, and link requests from buyers.

## Features

- **Authentication**: Login and registration system with role-based access (Owner/Manager)
- **Dashboard**: Overview of key metrics and recent activity
- **Catalog Management**: Manage product categories and inventory
- **Order Management**: View and manage orders from buyers
- **Link Requests**: Approve or reject buyer connection requests
- **Team Management**: Manage team members (Owner only)
- **Settings**: Update supplier information (Owner only)

## Tech Stack

- **SvelteKit**: Framework for building the application
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Lucide Svelte**: Icons
- **Vite**: Build tool

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## Demo Credentials

- **Owner**: `owner@supplier.com` (any password)
- **Manager**: `manager@supplier.com` (any password)

## Project Structure

```
src/
├── lib/
│   ├── components/        # Reusable Svelte components
│   │   ├── ui/            # UI component library
│   │   └── ...            # Feature components
│   ├── stores/            # Svelte stores (state management)
│   ├── types/             # TypeScript type definitions
│   └── mockData.ts        # Mock data for development
├── routes/                # SvelteKit routes (pages)
│   ├── +layout.svelte    # Root layout
│   ├── +page.svelte       # Home page
│   ├── login/             # Login page
│   ├── dashboard/         # Dashboard page
│   └── ...                # Other routes
└── app.css                # Global styles
```

## Building for Production

```bash
npm run build
```

The built application will be in the `build` directory.

## Development

- Run `npm run dev` to start the development server
- Run `npm run check` to type-check the application
- Run `npm run preview` to preview the production build locally

## Notes

- This application uses mock data stored in localStorage for demonstration purposes
- In a production environment, you would connect to a backend API
- Authentication is currently mocked - replace with real authentication in production
