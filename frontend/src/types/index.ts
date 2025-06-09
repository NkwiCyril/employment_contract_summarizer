export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Contract {
  id: number;
  file_name: string;
  file_size: number;
  language: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  uploaded_at: string;
  processed_at?: string;
}

export interface Summary {
  id: number;
  contract_id: number;
  content: string;
  confidence_score: number;
  summary_type: 'brief' | 'standard' | 'detailed';
  created_at: string;
  approved: boolean;
}

export interface Entity {
  id: number;
  entity_type: string;
  entity_value: string;
  confidence: number;
  section?: string;
}

export interface UploadResponse {
  message: string;
  contract_id: number;
  language: string;
  entities_found: number;
}