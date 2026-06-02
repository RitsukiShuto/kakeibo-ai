import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : ''; // 本番環境ではルート相対パスを使用（Nginxが/apiをハンドルするため）

const client = axios.create({
  baseURL: API_BASE_URL,
});

export default client;

export interface Transaction {
  transaction_id: string;
  transaction_date: string;
  category: string;
  genre: string;
  amount: number;
  comment: string;
  source: string;
  mode: string;
  is_reimbursement: number;
  self_amount: number | null;
  reimbursement_status: string | null;
}

export interface CategoryMetadata {
  category: string;
  genre: string;
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
  pace_limit?: number;
}

export interface SankeyNode {
  id: number;
  name: string;
}

export interface SankeyLink {
  source: number;
  target: number;
  value: number;
}

export interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

export interface LatestSummary {
  summary: string;
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
  model_name?: string;
  prompt_tokens?: number;
  response_tokens?: number;
  total_tokens?: number;
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
}

export interface AIPersona {
  id: string;
  name: string;
  description?: string;
}

export interface AISettings {
  active_model: string;
  available_models: AIModel[];
  active_persona?: string;
  available_personas?: AIPersona[];
}

export interface ReimbursementSuggestion {
  transaction_id: string;
  reason: string;
}
