'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { bgvApi, BGVRequest } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface BGVTableProps {
  refreshTrigger?: number;
}

export default function BGVTable({ refreshTrigger }: BGVTableProps) {
  const router = useRouter();
  const [bgvs, setBgvs] = useState<BGVRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBGVs = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await bgvApi.list();
      
      if (response.status === 'success' && response.data) {
        setBgvs(response.data);
      } else {
        setError(response.message || 'Failed to fetch BGVs');
      }
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
        'An error occurred while fetching BGVs'
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBGVs();
  }, [refreshTrigger]);

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'completed' || statusLower === 'success' || statusLower === 'verified') {
      return 'text-green-600 bg-green-50';
    }
    if (statusLower === 'pending' || statusLower === 'in_progress' || statusLower === 'documents_requested') {
      return 'text-yellow-600 bg-yellow-50';
    }
    if (statusLower === 'failed' || statusLower === 'rejected') {
      return 'text-red-600 bg-red-50';
    }
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Background Verification Requests</CardTitle>
            <CardDescription>
              View and manage all background verification requests
            </CardDescription>
          </div>
          <Button variant="outline" onClick={fetchBGVs} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Refresh'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading && bgvs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading BGVs...</p>
          </div>
        ) : error ? (
          <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        ) : bgvs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No background verification requests found</p>
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Candidate Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {bgvs.map((bgv) => (
                  <TableRow
                    key={bgv.id}
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => router.push(ROUTES.BGV_DETAIL(bgv.id))}
                  >
                    <TableCell className="font-medium">{bgv.id}</TableCell>
                    <TableCell>
                      {bgv.first_name} {bgv.last_name}
                    </TableCell>
                    <TableCell>{bgv.email || 'N/A'}</TableCell>
                    <TableCell>{bgv.phone_number || 'N/A'}</TableCell>
                    <TableCell>{bgv.role || 'N/A'}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(
                          bgv.status
                        )}`}
                      >
                        {bgv.status || 'Unknown'}
                      </span>
                    </TableCell>
                    <TableCell>{formatDate(bgv.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

