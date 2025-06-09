'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { contractsAPI } from '@/lib/api';
import { Upload, FileText, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ContractUpload() {
  const router = useRouter();
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [summaryType, setSummaryType] = useState<'brief' | 'standard' | 'detailed'>('standard');
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
        setError(null);
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        setError(null);
      }
    }
  };

  const validateFile = (file: File): boolean => {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF or DOCX file');
      return false;
    }

    if (file.size > maxSize) {
      setError('File size must be less than 10MB');
      return false;
    }

    return true;
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await contractsAPI.upload(file);
      setUploadResult(result);
      
      // Redirect to contract view after successful upload
      setTimeout(() => {
        router.push(`/contract/${result.contract_id}`);
      }, 2000);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
    setUploadResult(null);
  };

  if (uploadResult) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-6 w-6 text-green-600" />
                Upload Successful
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-medium text-green-900 mb-2">Contract Processed Successfully</h3>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>Contract ID: {uploadResult.contract_id}</li>
                    <li>Language: {uploadResult.language.toUpperCase()}</li>
                    <li>Entities Found: {uploadResult.entities_found}</li>
                  </ul>
                </div>
                <p className="text-gray-600">Redirecting to contract details...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/" className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Upload Employment Contract</h1>
          <p className="text-gray-600">Upload your employment contract for AI-powered summarization</p>
        </div>

        {/* Upload Area */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              
              <div className="space-y-4">
                <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Drop employment contract files here
                  </h3>
                  <p className="text-gray-600">or click to browse</p>
                </div>
                <div className="text-sm text-gray-500">
                  <p>Supported: PDF, DOCX, DOC</p>
                  <p>Max size: 10MB</p>
                </div>
              </div>
            </div>

            {/* File Preview */}
            {file && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-blue-600" />
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB • {file.type}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={removeFile}>
                    Remove
                  </Button>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Summary Options */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Summary Options</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-3 block">
                  Summary Length
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'brief', label: 'Brief', description: '100-150 words' },
                    { value: 'standard', label: 'Standard', description: '200-250 words' },
                    { value: 'detailed', label: 'Detailed', description: '300+ words' },
                  ].map((option) => (
                    <label key={option.value} className="cursor-pointer">
                      <input
                        type="radio"
                        name="summaryType"
                        value={option.value}
                        checked={summaryType === option.value}
                        onChange={(e) => setSummaryType(e.target.value as any)}
                        className="sr-only"
                      />
                      <div
                        className={`p-3 border rounded-lg text-center transition-colors ${
                          summaryType === option.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        <div className="font-medium">{option.label}</div>
                        <div className="text-xs text-gray-600">{option.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Focus Areas
                </label>
                <div className="flex flex-wrap gap-2">
                  {['Compensation', 'Responsibilities', 'Terms'].map((area) => (
                    <label key={area} className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      <span className="text-sm">{area}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Upload Button */}
        <div className="flex justify-end space-x-3">
          <Link href="/">
            <Button variant="outline">Cancel</Button>
          </Link>
          <Button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="min-w-[120px]"
          >
            {uploading ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Processing...
              </div>
            ) : (
              'Process Contract'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}