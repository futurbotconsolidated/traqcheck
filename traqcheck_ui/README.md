# TraqCheck UI

Next.js dashboard application for TraqCheck Background Verification System.

## Features

- **Authentication**: Login with email and password
- **Role-based Access**: Separate dashboards for recruiters and candidates
- **Route Protection**: Automatic redirection based on user role
- **Modern UI**: Built with Shadcn UI components

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
traqcheck_ui/
├── app/
│   ├── dashboard/
│   │   ├── recruiter/     # Recruiter dashboard
│   │   └── candidate/     # Candidate dashboard
│   ├── login/             # Login page
│   └── page.tsx           # Home page (redirects)
├── components/
│   ├── ui/                # Shadcn UI components
│   └── ProtectedRoute.tsx # Route protection component
├── contexts/
│   └── AuthContext.tsx   # Authentication context
└── lib/
    ├── api.ts            # API endpoints
    ├── api-config.ts     # API configuration
    └── constants.ts      # Constants and types
```

## Authentication Flow

1. User logs in via `/login`
2. On successful login, tokens and user data are stored in localStorage
3. User is redirected to their role-specific dashboard:
   - Recruiters → `/dashboard/recruiter`
   - Candidates → `/dashboard/candidate`
4. Protected routes automatically redirect unauthorized users

## API Integration

The application connects to the Django backend at `http://localhost:8000` by default.

### Login Endpoint

- **URL**: `/api/auth/login/`
- **Method**: POST
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```

## Role-Based Access

- **Recruiters** can only access `/dashboard/recruiter`
- **Candidates** can only access `/dashboard/candidate`
- Attempting to access the wrong dashboard redirects to the correct one
- Unauthenticated users are redirected to `/login`

## Development

### Build

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Lint

```bash
npm run lint
```
