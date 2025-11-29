'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { ROUTES } from '@/lib/constants';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated && user) {
        // Redirect based on role
        if (user.role === 'recruiter') {
          router.push(ROUTES.RECRUITER_DASHBOARD);
        } else if (user.role === 'candidate') {
          router.push(ROUTES.CANDIDATE_DASHBOARD);
        }
      } else {
        router.push(ROUTES.LOGIN);
      }
    }
  }, [isAuthenticated, user, isLoading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <p className="text-lg">Loading...</p>
      </div>
    </div>
  );
}
