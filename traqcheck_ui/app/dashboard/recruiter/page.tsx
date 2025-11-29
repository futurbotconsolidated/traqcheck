'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { USER_ROLES } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import BGVUpload from '@/components/BGVUpload';
import BGVTable from '@/components/BGVTable';

export default function RecruiterDashboard() {
  const { user, logout } = useAuth();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadSuccess = () => {
    // Trigger refresh of BGV table
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <ProtectedRoute allowedRoles={[USER_ROLES.RECRUITER]}>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold">TraqCheck</h1>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  {user?.full_name} ({user?.email})
                </span>
                <Button variant="outline" onClick={logout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Recruiter Dashboard
            </h2>
            <p className="mt-2 text-gray-600">
              Welcome back, {user?.full_name}! Manage your background verification requests here.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <BGVUpload onUploadSuccess={handleUploadSuccess} />
          </div>

          <div className="mt-8">
            <BGVTable refreshTrigger={refreshTrigger} />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

