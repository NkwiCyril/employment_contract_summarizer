'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { contractsAPI, summariesAPI } from '@/lib/api';
import { Contract, Summary, Entity } from '@/types';
import { formatDate, formatFileSize, getStatusColor, getConfidenceColor } from '@/lib/utils';
import { 
  ArrowLeft, 
  FileText, 
  Download, 
  Star, 
  Clock, 
  AlertCircle,
  CheckCircle,
  Sparkles,
  User,
  Building,
  DollarSign,
  Calendar,
  MapPin,
  Info
} from 'lucide-react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ContractViewProps {
  contractId: number;
}

export default function ContractView({ contractId }: ContractViewProps) {
  const [contract, setContract] = useState<Contract | null>(null);
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedSummaryType, setSelectedSummaryType] = useState<'brief' | 'standard' | 'detailed'>('standard');
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    fetchContractData();
  }, [contractId]);

  const fetchContractData = async () => {
    try {
      const [contractResponse, summariesResponse] = await Promise.all([
        contractsAPI.getById(contractId),
        summariesAPI.getByContract(contractId)
      ]);

      setContract(contractResponse.contract);
      setEntities(contractResponse.entities || []);
      setSummaries(summariesResponse.summaries || []);
    } catch (error) {
      console.error('Error fetching contract data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async () => {
    if (!contract) return;

    setGenerating(true);
    try {
      const response = await summariesAPI.generate(contractId, selectedSummaryType);
      setSummaries(prev => [response.summary, ...prev.filter(s => s.summary_type !== selectedSummaryType)]);
      
      // Update contract status
      setContract(prev => prev ? { ...prev, status: 'completed' } : null);
    } catch (error) {
      console.error('Error generating summary:', error);
    } finally {
      setGenerating(false);
    }
  };

  const approveSummary = async (summaryId: number) => {
    try {
      await summariesAPI.approve(summaryId);
      setSummaries(prev => 
        prev.map(s => s.id === summaryId ? { ...s, approved: true } : s)
      );
    } catch (error) {
      console.error('Error approving summary:', error);
    }
  };

  const submitFeedback = async (summaryId: number) => {
    try {
      await summariesAPI.submitFeedback(summaryId, feedbackText, feedbackRating);
      setShowFeedback(false);
      setFeedbackText('');
      setFeedbackRating(5);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const getEntityIcon = (entityType: string) => {
    switch (entityType.toLowerCase()) {
      case 'person':
        return <User className="h-4 w-4" />;
      case 'org':
        return <Building className="h-4 w-4" />;
      case 'money':
      case 'salary':
        return <DollarSign className="h-4 w-4" />;
      case 'date':
        return <Calendar className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const downloadSummary = (summary: Summary) => {
    const element = document.createElement('a');
    const file = new Blob([summary.content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `contract_${contractId}_summary_${summary.summary_type}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="p-8 text-center">
              <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Contract Not Found</h2>
              <p className="text-gray-600 mb-4">The requested contract could not be found.</p>
              <Link href="/">
                <Button>Back to Dashboard</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const currentSummary = summaries.find(s => s.summary_type === selectedSummaryType);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/" className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{contract.file_name}</h1>
              <p className="text-gray-600">
                {formatFileSize(contract.file_size)} • {contract.language.toUpperCase()} • 
                Uploaded {formatDate(contract.uploaded_at)}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(contract.status)}`}>
                {contract.status}
              </span>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Summary Generation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Contract Summary
                  </span>
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedSummaryType}
                      onChange={(e) => setSelectedSummaryType(e.target.value as any)}
                      className="text-sm border rounded px-2 py-1"
                    >
                      <option value="brief">Brief</option>
                      <option value="standard">Standard</option>
                      <option value="detailed">Detailed</option>
                    </select>
                    <Button
                      onClick={generateSummary}
                      disabled={generating && contract.status === 'processing'}
                      size="sm"
                    >
                      {generating ? (
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                          Generating...
                        </div>
                      ) : (
                        'Generate Summary'
                      )}
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {currentSummary ? (
                  <div className="space-y-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            {selectedSummaryType.charAt(0).toUpperCase() + selectedSummaryType.slice(1)} Summary
                          </span>
                          <span className={`text-sm font-medium ${getConfidenceColor(currentSummary.confidence_score)}`}>
                            {Math.round(currentSummary.confidence_score * 100)}% confidence
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {currentSummary.approved ? (
                            <span className="flex items-center gap-1 text-green-600 text-sm">
                              <CheckCircle className="h-4 w-4" />
                              Approved
                            </span>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => approveSummary(currentSummary.id)}
                            >
                              <Star className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                          )}
                        </div>
                      </div>
                      <div className="prose prose-sm max-w-none text-gray-700 markdown">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{currentSummary.content}</ReactMarkdown>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm text-gray-500">
                      <span>Generated {formatDate(currentSummary.created_at)}</span>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadSummary(currentSummary)}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Export Summary
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowFeedback(!showFeedback)}
                        >
                          Feedback
                        </Button>
                      </div>
                    </div>

                    {/* Feedback Form */}
                    {showFeedback && (
                      <Card className="mt-4">
                        <CardHeader>
                          <CardTitle className="text-lg">Provide Feedback</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium mb-2">Rating (1-5)</label>
                              <select
                                value={feedbackRating}
                                onChange={(e) => setFeedbackRating(parseInt(e.target.value))}
                                className="w-full border rounded px-3 py-2"
                              >
                                {[1, 2, 3, 4, 5].map(rating => (
                                  <option key={rating} value={rating}>
                                    {rating} - {rating === 5 ? 'Excellent' : rating === 4 ? 'Good' : rating === 3 ? 'Average' : rating === 2 ? 'Poor' : 'Very Poor'}
                                  </option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-2">Comments</label>
                              <textarea
                                value={feedbackText}
                                onChange={(e) => setFeedbackText(e.target.value)}
                                className="w-full border rounded px-3 py-2 h-24"
                                placeholder="Please provide your feedback on the summary quality..."
                              />
                            </div>
                            <div className="flex gap-2">
                              <Button
                                onClick={() => submitFeedback(currentSummary.id)}
                                size="sm"
                              >
                                Submit Feedback
                              </Button>
                              <Button
                                variant="outline"
                                onClick={() => setShowFeedback(false)}
                                size="sm"
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                ) : contract.status === 'processing' ? (
                  <div className="text-center py-8">
                    <Clock className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Processing Contract</h3>
                    <p className="text-gray-600">Your contract is being analyzed. This may take a few minutes.</p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Summary Generated</h3>
                    <p className="text-gray-600 mb-4">Click "Generate Summary" to create an AI-powered summary of this contract</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* All Summaries */}
            {summaries.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Summary History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {summaries.map((summary) => (
                      <div key={summary.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium capitalize">{summary.summary_type}</span>
                            <span className={`text-sm ${getConfidenceColor(summary.confidence_score)}`}>
                              {Math.round(summary.confidence_score * 100)}%
                            </span>
                            {summary.approved && (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            )}
                          </div>
                          <span className="text-sm text-gray-500">
                            {formatDate(summary.created_at)}
                          </span>
                        </div>
                        <p className="text-gray-700 text-sm line-clamp-3">
                          {summary.content}
                        </p>
                        <div className="mt-2 flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadSummary(summary)}
                          >
                            <Download className="h-3 w-3 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contract Details */}
            <Card>
              <CardHeader>
                <CardTitle>Contract Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <p className={`text-sm font-medium ${getStatusColor(contract.status)}`}>
                    {contract.status}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Language</label>
                  <p className="text-sm">{contract.language.toUpperCase()}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">File Size</label>
                  <p className="text-sm">{formatFileSize(contract.file_size)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Uploaded</label>
                  <p className="text-sm">{formatDate(contract.uploaded_at)}</p>
                </div>
                {contract.processed_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Processed</label>
                    <p className="text-sm">{formatDate(contract.processed_at)}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Extracted Entities */}
            {entities.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Key Information</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {entities.slice(0, 8).map((entity) => (
                      <div key={entity.id} className="border-b pb-2 last:border-b-0">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {getEntityIcon(entity.entity_type)}
                            <span className="text-sm font-medium text-gray-500 capitalize">
                              {entity.entity_type.replace('_', ' ')}
                            </span>
                          </div>
                          <span className={`text-xs ${getConfidenceColor(entity.confidence)}`}>
                            {Math.round(entity.confidence * 100)}%
                          </span>
                        </div>
                        <p className="text-sm text-gray-900 mt-1 ml-6">{entity.entity_value}</p>
                      </div>
                    ))}
                    {entities.length > 8 && (
                      <p className="text-sm text-gray-500 text-center">
                        +{entities.length - 8} more entities
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="h-4 w-4 mr-2" />
                    Download Original
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <FileText className="h-4 w-4 mr-2" />
                    View Full Text
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Star className="h-4 w-4 mr-2" />
                    Add to Favorites
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}