import React from 'react';
import { Bot, ArrowRightLeft, Trash2, Plus } from 'lucide-react';

interface MappingSettingsProps {
  mapping: any;
  handleSuggestMappings: () => void;
  suggesting: boolean;
  aiSuggestions: any[];
  applySuggestion: (s: any) => void;
  hoveredSuggestion: number | null;
  setHoveredSuggestion: (idx: number | null) => void;
  setMapping: (mapping: any) => void;
  setMappingJson: (json: string) => void;
}

const MappingSettings: React.FC<MappingSettingsProps> = ({
  mapping, handleSuggestMappings, suggesting, aiSuggestions, applySuggestion,
  hoveredSuggestion, setHoveredSuggestion, setMapping, setMappingJson
}) => {
  return (
    <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="card" style={{ border: '1px solid var(--primary)', background: 'rgba(59, 130, 246, 0.05)' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ color: 'var(--primary)' }}><Bot size={20} /> AI マッピング提案</h3>
          <button 
            className="btn-primary" 
            onClick={handleSuggestMappings} 
            disabled={suggesting}
            style={{ padding: '4px 12px', fontSize: '0.85rem' }}
          >
            {suggesting ? '考え中...' : 'AIにマッピングを相談する'}
          </button>
        </div>
        <div className="card-body">
          <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
            DB内の未分類項目をスキャンし、予算設定に基づいた最適なマッピングをAIが提案します。
          </p>
          {aiSuggestions.length > 0 ? (
            <div className="flex flex-col gap-3">
              {aiSuggestions.map((s, idx) => (
                <div 
                  key={idx} 
                  className="suggestion-item" 
                  style={{ position: 'relative', background: 'var(--bg-color)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                  onMouseEnter={() => setHoveredSuggestion(idx)}
                  onMouseLeave={() => setHoveredSuggestion(null)}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {s.raw_category} {s.raw_genre ? `> ${s.raw_genre}` : ''}
                    </div>
                    <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ArrowRightLeft size={14} className="text-primary" />
                      {s.suggested_category} {s.suggested_genre ? `> ${s.suggested_genre}` : ''}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--success)', marginTop: '4px' }}>
                      理由: {s.reason}
                    </div>
                  </div>
                  <button className="btn-outline" onClick={() => applySuggestion(s)} style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
                    採用
                  </button>

                  {hoveredSuggestion === idx && s.examples && s.examples.length > 0 && (
                    <div className="card glass" style={{ 
                      position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100, 
                      marginTop: '4px', padding: '12px', fontSize: '0.75rem', 
                      background: 'var(--card-bg)', border: '1px solid var(--primary)' 
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '8px', color: 'var(--primary)' }}>該当する直近の明細:</div>
                      {s.examples.map((ex: any, eidx: number) => (
                        <div key={eidx} style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ color: 'var(--text-muted)' }}>{ex.transaction_date}</span>
                          <span style={{ flex: 1 }}>{ex.comment}</span>
                          <span style={{ fontWeight: 'bold' }}>{ex.amount.toLocaleString()}円</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : !suggesting && (
            <div className="text-center py-4 text-muted" style={{ fontSize: '0.85rem' }}>
              「相談する」ボタンを押すと、新しい提案が表示されます。
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3><ArrowRightLeft size={20} /> 大項目の変換ルール (Category Mapping)</h3>
        </div>
        <div className="card-body">
          <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
            MoneyForwardやZaimの「大項目」を、独自のカテゴリ名に変換します。
          </p>
          <table className="table">
            <thead>
              <tr>
                <th>元のカテゴリ名 (Raw)</th>
                <th style={{ width: '40px' }}></th>
                <th>変換後のカテゴリ名 (Mapped)</th>
                <th style={{ width: '60px' }}></th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(mapping?.category_mappings || {}).map(([raw, mapped]) => (
                <tr key={raw}>
                  <td>{raw}</td>
                  <td style={{ textAlign: 'center' }}>→</td>
                  <td>
                    <input 
                      type="text" className="form-control form-control-sm" 
                      value={mapped as string} 
                      onChange={(e) => {
                        const newMapping = { ...mapping };
                        newMapping.category_mappings[raw] = e.target.value;
                        setMapping(newMapping);
                        setMappingJson(JSON.stringify(newMapping, null, 2));
                      }}
                    />
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button 
                      className="btn-icon text-danger" 
                      onClick={() => {
                        const newMapping = { ...mapping };
                        delete newMapping.category_mappings[raw];
                        setMapping(newMapping);
                        setMappingJson(JSON.stringify(newMapping, null, 2));
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              <tr>
                <td>
                  <input type="text" id="new-cat-raw" className="form-control form-control-sm" placeholder="未分類" />
                </td>
                <td style={{ textAlign: 'center' }}>→</td>
                <td>
                  <input type="text" id="new-cat-mapped" className="form-control form-control-sm" placeholder="その他" />
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button 
                    className="btn-icon text-primary"
                    onClick={() => {
                      const raw = (document.getElementById('new-cat-raw') as HTMLInputElement).value;
                      const mapped = (document.getElementById('new-cat-mapped') as HTMLInputElement).value;
                      if (raw && mapped) {
                        const newMapping = { ...mapping };
                        if (!newMapping.category_mappings) newMapping.category_mappings = {};
                        newMapping.category_mappings[raw] = mapped;
                        setMapping(newMapping);
                        setMappingJson(JSON.stringify(newMapping, null, 2));
                        (document.getElementById('new-cat-raw') as HTMLInputElement).value = '';
                        (document.getElementById('new-cat-mapped') as HTMLInputElement).value = '';
                      }
                    }}
                  >
                    <Plus size={18} />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3><ArrowRightLeft size={20} /> 中項目の変換・上書きルール (Genre Mapping)</h3>
        </div>
        <div className="card-body">
          <p className="text-muted mb-4" style={{ fontSize: '0.85rem' }}>
            「中項目」の名前に基づいて、中項目名のみ、または大項目も含めて変換します。<br/>
            例: 「コンビニ」という中項目を「日用品」という中項目に変更する、など。
          </p>
          <table className="table">
            <thead>
              <tr>
                <th>元の中項目名 (Raw)</th>
                <th style={{ width: '40px' }}></th>
                <th>変換後のカテゴリ/中項目</th>
                <th style={{ width: '60px' }}></th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(mapping?.genre_mappings || {}).map(([raw, rule]: [string, any]) => (
                <tr key={raw}>
                  <td>{raw}</td>
                  <td style={{ textAlign: 'center' }}>→</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <div style={{ flex: 1 }}>
                        <label style={{ fontSize: '0.7rem' }}>大項目(任意)</label>
                        <input 
                          type="text" className="form-control form-control-sm" 
                          placeholder="大項目"
                          value={typeof rule === 'object' ? rule.category : ''} 
                          onChange={(e) => {
                            const newMapping = { ...mapping };
                            if (typeof rule !== 'object') {
                              newMapping.genre_mappings[raw] = { category: e.target.value, genre: rule };
                            } else {
                              newMapping.genre_mappings[raw].category = e.target.value;
                            }
                            setMapping(newMapping);
                            setMappingJson(JSON.stringify(newMapping, null, 2));
                          }}
                        />
                      </div>
                      <div style={{ flex: 1 }}>
                        <label style={{ fontSize: '0.7rem' }}>中項目</label>
                        <input 
                          type="text" className="form-control form-control-sm" 
                          placeholder="中項目"
                          value={typeof rule === 'object' ? rule.genre : rule} 
                          onChange={(e) => {
                            const newMapping = { ...mapping };
                            if (typeof rule !== 'object') {
                              newMapping.genre_mappings[raw] = e.target.value;
                            } else {
                              newMapping.genre_mappings[raw].genre = e.target.value;
                            }
                            setMapping(newMapping);
                            setMappingJson(JSON.stringify(newMapping, null, 2));
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td style={{ textAlign: 'center', verticalAlign: 'bottom' }}>
                    <button 
                      className="btn-icon text-danger" 
                      onClick={() => {
                        const newMapping = { ...mapping };
                        delete newMapping.genre_mappings[raw];
                        setMapping(newMapping);
                        setMappingJson(JSON.stringify(newMapping, null, 2));
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              <tr>
                <td>
                  <input type="text" id="new-gen-raw" className="form-control form-control-sm" placeholder="ランチ" />
                </td>
                <td style={{ textAlign: 'center' }}>→</td>
                <td>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input type="text" id="new-gen-cat" className="form-control form-control-sm" placeholder="食費(任意)" />
                    <input type="text" id="new-gen-gen" className="form-control form-control-sm" placeholder="昼食" />
                  </div>
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button 
                    className="btn-icon text-primary"
                    onClick={() => {
                      const raw = (document.getElementById('new-gen-raw') as HTMLInputElement).value;
                      const cat = (document.getElementById('new-gen-cat') as HTMLInputElement).value;
                      const gen = (document.getElementById('new-gen-gen') as HTMLInputElement).value;
                      if (raw && gen) {
                        const newMapping = { ...mapping };
                        if (!newMapping.genre_mappings) newMapping.genre_mappings = {};
                        if (cat) {
                          newMapping.genre_mappings[raw] = { category: cat, genre: gen };
                        } else {
                          newMapping.genre_mappings[raw] = gen;
                        }
                        setMapping(newMapping);
                        setMappingJson(JSON.stringify(newMapping, null, 2));
                        (document.getElementById('new-gen-raw') as HTMLInputElement).value = '';
                        (document.getElementById('new-gen-cat') as HTMLInputElement).value = '';
                        (document.getElementById('new-gen-gen') as HTMLInputElement).value = '';
                      }
                    }}
                  >
                    <Plus size={18} />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MappingSettings;
