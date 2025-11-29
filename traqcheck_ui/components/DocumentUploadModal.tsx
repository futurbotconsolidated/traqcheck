'use client';

import { useState, useRef } from 'react';
import { bgvApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Upload, X, FileImage } from 'lucide-react';

interface DocumentUploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  bgvId: number;
  onSuccess?: () => void;
}

export default function DocumentUploadModal({
  open,
  onOpenChange,
  bgvId,
  onSuccess,
}: DocumentUploadModalProps) {
  const [panFile, setPanFile] = useState<File | null>(null);
  const [aadhaarFile, setAadhaarFile] = useState<File | null>(null);
  const [isDraggingPan, setIsDraggingPan] = useState(false);
  const [isDraggingAadhaar, setIsDraggingAadhaar] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const panInputRef = useRef<HTMLInputElement>(null);
  const aadhaarInputRef = useRef<HTMLInputElement>(null);

  const validateImageFile = (file: File): boolean => {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    return validTypes.includes(file.type);
  };

  const handlePanFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!validateImageFile(selectedFile)) {
        setError('PAN: Please upload a valid image file (JPG, PNG, or WebP)');
        setPanFile(null);
        return;
      }
      setPanFile(selectedFile);
      setError(null);
    }
  };

  const handleAadhaarFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!validateImageFile(selectedFile)) {
        setError('Aadhaar: Please upload a valid image file (JPG, PNG, or WebP)');
        setAadhaarFile(null);
        return;
      }
      setAadhaarFile(selectedFile);
      setError(null);
    }
  };

  const handlePanDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingPan(true);
  };

  const handlePanDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingPan(false);
  };

  const handlePanDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingPan(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!validateImageFile(droppedFile)) {
        setError('PAN: Please upload a valid image file (JPG, PNG, or WebP)');
        return;
      }
      setPanFile(droppedFile);
      setError(null);
    }
  };

  const handleAadhaarDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingAadhaar(true);
  };

  const handleAadhaarDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingAadhaar(false);
  };

  const handleAadhaarDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingAadhaar(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!validateImageFile(droppedFile)) {
        setError('Aadhaar: Please upload a valid image file (JPG, PNG, or WebP)');
        return;
      }
      setAadhaarFile(droppedFile);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!panFile || !aadhaarFile) {
      setError('Please upload both PAN and Aadhaar documents');
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await bgvApi.submitDocuments(bgvId, panFile, aadhaarFile);
      
      if (response.status === 'success') {
        setSuccess('Documents uploaded successfully!');
        setPanFile(null);
        setAadhaarFile(null);
        if (panInputRef.current) panInputRef.current.value = '';
        if (aadhaarInputRef.current) aadhaarInputRef.current.value = '';
        
        setTimeout(() => {
          onOpenChange(false);
          if (onSuccess) {
            onSuccess();
          }
        }, 1500);
      } else {
        setError(response.message || 'Upload failed');
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string; errors?: Record<string, string[]> } } };
      const errorMessage = 
        error.response?.data?.message ||
        error.response?.data?.errors?.pan?.[0] ||
        error.response?.data?.errors?.aadhaar?.[0] ||
        'An error occurred during upload';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      setPanFile(null);
      setAadhaarFile(null);
      setError(null);
      setSuccess(null);
      if (panInputRef.current) panInputRef.current.value = '';
      if (aadhaarInputRef.current) aadhaarInputRef.current.value = '';
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Upload Documents</DialogTitle>
          <DialogDescription>
            Upload your PAN and Aadhaar documents for background verification
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* PAN Upload */}
          <div>
            <label className="text-sm font-medium mb-2 block">PAN Card *</label>
            <div
              onDragOver={handlePanDragOver}
              onDragLeave={handlePanDragLeave}
              onDrop={handlePanDrop}
              className={`
                relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
                ${isDraggingPan 
                  ? 'border-primary bg-primary/5' 
                  : 'border-gray-300 hover:border-gray-400'
                }
                ${isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
              `}
              onClick={() => !isUploading && panInputRef.current?.click()}
            >
              <input
                ref={panInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handlePanFileChange}
                disabled={isUploading}
                className="hidden"
              />
              
              {panFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <div className="rounded-full bg-primary/10 p-3">
                      <FileImage className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{panFile.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(panFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setPanFile(null);
                      if (panInputRef.current) panInputRef.current.value = '';
                    }}
                    className="mt-2"
                  >
                    <X className="h-4 w-4 mr-1" />
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <div className="rounded-full bg-gray-100 p-3">
                      <Upload className="h-6 w-6 text-gray-400" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {isDraggingPan ? 'Drop PAN file here' : 'Drag and drop PAN card'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      or click to browse
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      JPG, PNG, or WebP files only
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Aadhaar Upload */}
          <div>
            <label className="text-sm font-medium mb-2 block">Aadhaar Card *</label>
            <div
              onDragOver={handleAadhaarDragOver}
              onDragLeave={handleAadhaarDragLeave}
              onDrop={handleAadhaarDrop}
              className={`
                relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
                ${isDraggingAadhaar 
                  ? 'border-primary bg-primary/5' 
                  : 'border-gray-300 hover:border-gray-400'
                }
                ${isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
              `}
              onClick={() => !isUploading && aadhaarInputRef.current?.click()}
            >
              <input
                ref={aadhaarInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleAadhaarFileChange}
                disabled={isUploading}
                className="hidden"
              />
              
              {aadhaarFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <div className="rounded-full bg-primary/10 p-3">
                      <FileImage className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{aadhaarFile.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(aadhaarFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setAadhaarFile(null);
                      if (aadhaarInputRef.current) aadhaarInputRef.current.value = '';
                    }}
                    className="mt-2"
                  >
                    <X className="h-4 w-4 mr-1" />
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center justify-center">
                    <div className="rounded-full bg-gray-100 p-3">
                      <Upload className="h-6 w-6 text-gray-400" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {isDraggingAadhaar ? 'Drop Aadhaar file here' : 'Drag and drop Aadhaar card'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      or click to browse
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      JPG, PNG, or WebP files only
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="rounded-md bg-green-50 p-3 text-sm text-green-600">
              {success}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!panFile || !aadhaarFile || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Submit Documents'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

