# CrisisGrid AI - Frontend Dashboard

Modern Next.js 14 TypeScript frontend for the CrisisGrid AI emergency response platform.

## 🚀 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (Strict Mode)
- **UI Library**: Ant Design 5
- **Styling**: Tailwind CSS
- **Data Fetching**: TanStack React Query (React Query v5)
- **HTTP Client**: Axios
- **Maps**: React Leaflet + Leaflet
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod
- **State Management**: Zustand (optional)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout with providers
│   │   ├── page.tsx           # Landing page
│   │   ├── providers.tsx      # React Query provider
│   │   ├── globals.css        # Global styles
│   │   ├── admin/             # Admin dashboard routes
│   │   │   └── page.tsx
│   │   └── citizen/           # Citizen portal routes
│   │       └── page.tsx
│   ├── components/            # Reusable UI components
│   │   ├── ui/               # Base UI components
│   │   ├── maps/             # Map components
│   │   ├── cards/            # Dashboard cards
│   │   └── forms/            # Form components
│   ├── lib/                  # Utilities and helpers
│   │   ├── api/              # API client configuration
│   │   │   └── client.ts     # Axios instance with interceptors
│   │   └── utils/            # Helper functions
│   │       └── index.ts      # Utility functions
│   ├── types/                # TypeScript type definitions
│   │   └── api.ts            # API response types
│   ├── contexts/             # React contexts
│   └── hooks/                # Custom React hooks
├── public/                   # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
├── postcss.config.js
└── .env.example
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+ and npm 9+
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd Buildproject/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and configure:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
   NEXT_PUBLIC_DEFAULT_LAT=51.5074
   NEXT_PUBLIC_DEFAULT_LNG=-0.1278
   NEXT_PUBLIC_DEFAULT_ZOOM=10
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

5. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📜 Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build production bundle
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🔌 API Integration

The frontend connects to the FastAPI backend via the configured API client:

- **Base URL**: `http://localhost:8000/api/v1`
- **Client**: `src/lib/api/client.ts`
- **Interceptors**: Automatic auth token injection, error handling
- **Types**: Full TypeScript types in `src/types/api.ts`

### Example API Usage

```typescript
import apiClient from '@/lib/api/client';
import { Alert } from '@/types/api';

// Fetch alerts
const response = await apiClient.get<Alert[]>('/alerts');
const alerts = response.data;

// Create report
const newReport = await apiClient.post('/reports', {
  type: 'fire',
  description: 'Building fire',
  location: { latitude: 51.5074, longitude: -0.1278 }
});
```

## 🗺️ Routes

### Public Routes
- `/` - Landing page with portal selection

### Admin Dashboard (`/admin`)
- Alert monitoring and verification
- Resource dispatch management
- Incident mapping
- Analytics and reporting
- Advisory system management

### Citizen Portal (`/citizen`)
- Emergency report submission
- Safety advisory viewing
- Incident map
- Report tracking

## 🎨 Styling

### Tailwind CSS
- Configured with custom color palette
- Utility-first approach
- Responsive design utilities

### Ant Design Theme
- Primary color: `#0ea5e9` (Sky Blue)
- Error color: `#ef4444` (Red)
- Warning color: `#f59e0b` (Amber)
- Success color: `#22c55e` (Green)

### Custom Utilities
Use the `cn()` utility for merging Tailwind classes:
```typescript
import { cn } from '@/lib/utils';

<div className={cn('base-class', isActive && 'active-class')} />
```

## 🔧 Configuration Files

### `tsconfig.json`
- Strict mode enabled
- Path aliases: `@/*` → `./src/*`
- ES2020 target

### `next.config.js`
- API proxy to backend
- Image optimization
- Environment variable configuration

### `tailwind.config.js`
- Custom color palette
- Component paths
- Preflight disabled (for Ant Design compatibility)

## 📦 Key Dependencies

### Core
- `next@^14.2.0` - React framework
- `react@^18.3.0` - UI library
- `typescript@^5.4.0` - Type safety

### UI & Styling
- `antd@^5.16.0` - Component library
- `tailwindcss@^3.4.0` - Utility CSS
- `@ant-design/icons` - Icon set

### Data & State
- `@tanstack/react-query@^5.28.0` - Server state
- `axios@^1.6.8` - HTTP client
- `zustand@^4.5.2` - Client state (optional)

### Maps & Charts
- `react-leaflet@^4.2.1` - Map components
- `leaflet@^1.9.4` - Map library
- `recharts@^2.12.0` - Charts

### Forms
- `react-hook-form@^7.51.0` - Form management
- `zod@^3.22.4` - Schema validation

## 🚧 Development Notes

### Phase 8 & 9 Implementation
This is the initial project setup. The following features will be implemented:

**Phase 8 - Admin Dashboard**:
- Real-time alert monitoring
- Alert verification interface
- Resource dispatch UI
- Interactive incident map
- Analytics dashboard
- Advisory management

**Phase 9 - Citizen Portal**:
- Emergency report form
- Media upload (photos/videos)
- Safety advisory display
- Incident map view
- Report status tracking

### Type Safety
All API responses are fully typed. Import types from `@/types/api`:
```typescript
import { Alert, Report, DispatchLog } from '@/types/api';
```

### Error Handling
The API client includes automatic error handling:
- 401: Clears auth token
- Network errors: Logged to console
- API errors: Extracted and formatted

### Performance
- React Query caching (1 minute stale time)
- Image optimization via Next.js
- Code splitting via App Router
- Lazy loading for maps

## 🔐 Security

- Environment variables for sensitive config
- HTTPS in production
- CORS configured on backend
- Input validation with Zod
- XSS protection via React

## 📱 Responsive Design

- Mobile-first approach
- Ant Design Grid system
- Tailwind responsive utilities
- Touch-friendly UI elements

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill process on port 3000
npx kill-port 3000
# Or use different port
PORT=3001 npm run dev
```

### TypeScript errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### Map not loading
- Check Leaflet CSS import in `globals.css`
- Verify map tile URL in `.env.local`
- Ensure component is client-side (`'use client'`)

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Ant Design Components](https://ant.design/components/overview/)
- [React Query Guide](https://tanstack.com/query/latest/docs/react/overview)
- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contributing

1. Follow TypeScript strict mode
2. Use Ant Design components
3. Implement responsive design
4. Add proper error handling
5. Write meaningful commit messages

## 📄 License

Part of the CrisisGrid AI project for IBM Call for Code 2024 Hackathon.