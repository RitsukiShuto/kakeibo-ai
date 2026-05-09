import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
});

export default client;

export interface Transaction {
  transaction_id: string;
  transaction_date: string;
  category: string;
  amount: number;
  comment: string;
  source: string;
  mode: string;
  is_reimbursement: number;
  self_amount: number | null;
  reimbursement_status: string | null;
}

export interface KPI {
  budget: number;
  actual: number;
  remaining: number;
  total_assets: number;
}

export interface BudgetActual {
  category: string;
  budget: number;
  actual: number;
}

export interface AssetTrend {
  acquired_date: string;
  asset_type: string;
  total_amount: number;
}

export interface AnalysisHistory {
  id: number;
  created_at: string;
  timeframe: string;
  score: number;
  summary: string;
  report_path: string;
}

export interface ReimbursementSuggestion {
  transaction_id: string;
  reason: string;
}
