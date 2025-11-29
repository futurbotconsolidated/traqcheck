'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { USER_ROLES } from '@/lib/constants';
import { bgvApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import CandidateBGVTable from '@/components/CandidateBGVTable';

export default function CandidateDashboard() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({
    total: 0,
    inProgress: 0,
    completed: 0,
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await bgvApi.list();
        if (response.status === 'success' && response.data) {
          const bgvs = response.data;
          const total = bgvs.length;
          const inProgress = bgvs.filter(
            (bgv) =>
              bgv.status === 'documents_requested' ||
              bgv.status === 'pending' ||
              bgv.status === 'in_progress'
          ).length;
          const completed = bgvs.filter(
            (bgv) =>
              bgv.status === 'completed' ||
              bgv.status === 'success' ||
              bgv.status === 'verified'
          ).length;

          setStats({ total, inProgress, completed });
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, [refreshTrigger]);

  return (
    <ProtectedRoute allowedRoles={[USER_ROLES.CANDIDATE]}>
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
              Candidate Dashboard
            </h2>
            <p className="mt-2 text-gray-600">
              Welcome, {user?.full_name}! Track your background verification status here.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>My Verifications</CardTitle>
                <CardDescription>
                  Background verification requests for you
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{stats.total}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>In Progress</CardTitle>
                <CardDescription>
                  Verifications currently being processed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{stats.inProgress}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Completed</CardTitle>
                <CardDescription>
                  Successfully completed verifications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{stats.completed}</p>
              </CardContent>
            </Card>
          </div>

          <div className="mt-8">
            <CandidateBGVTable 
              refreshTrigger={refreshTrigger} 
              onRefresh={() => setRefreshTrigger((prev) => prev + 1)}
            />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

