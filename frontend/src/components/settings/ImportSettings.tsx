import React from 'react';
import { Upload } from 'lucide-react';

interface ImportSettingsProps {
  importFiles: File[];
  setImportFiles: (files: File[]) => void;
  handleImportCsv: () => void;
  importing: boolean;
  importResult: { totalFiles: number; totalImported: number; details: any[] } | null;
}

const ImportSettings: React.FC<ImportSettingsProps> = ({
  importFiles, setImportFiles, handleImportCsv, importing, importResult
}) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3><Upload size={20} /> データインポート (MoneyForward CSV)</h3>
      </div>
      <div className="card-body">
        <div className="alert-info mb-6" style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--primary)', fontSize: '0.9rem' }}>
          マネーフォワードMEからエクスポートした「入出金詳細.csv」をアップロードして、一括インポートします。<br/>
          <strong>複数のファイルをまとめて選択できます。</strong>
        </div>
        
        <div className="form-group">
          <label>CSVファイルを選択（複数可）</label>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input 
              id="csv-file-input"
              type="file" 
              accept=".csv" 
              multiple
              className="form-control" 
              style={{ padding: '8px' }}
              onChange={(e) => setImportFiles(Array.from(e.target.files || []))} 
            />
            <button 
              className="btn-primary" 
              onClick={handleImportCsv} 
              disabled={importFiles.length === 0 || importing}
              style={{ whiteSpace: 'nowrap' }}
            >
              {importing ? 'インポート中...' : `インポート開始 (${importFiles.length}ファイル)`}
            </button>
          </div>
          {importFiles.length > 0 && (
            <div className="mt-2" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              選択中: {importFiles.map(f => f.name).join(', ')}
            </div>
          )}
        </div>

        {importResult && (
          <div className="mt-4" style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '12px', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
            <strong>✅ インポート結果</strong>
            <ul style={{ margin: '8px 0 0 20px', fontSize: '0.9rem' }}>
              <li>処理ファイル数: {importResult.totalFiles}件</li>
              <li>インポート件数: {importResult.totalImported}件</li>
            </ul>
            <details style={{ marginTop: '8px', fontSize: '0.85rem' }}>
              <summary>詳細を見る</summary>
              <ul style={{ marginTop: '4px', marginLeft: '20px' }}>
                {importResult.details.map((d: any, i: number) => (
                  <li key={i} style={{ color: d.status === 'success' ? '#10b981' : '#ef4444' }}>
                    {d.file}: {d.status === 'success' ? `${d.imported}件` : d.reason}
                  </li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportSettings;
