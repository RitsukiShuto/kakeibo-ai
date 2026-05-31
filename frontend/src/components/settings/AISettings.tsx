import React from 'react';
import { Bot, CheckCircle2 } from 'lucide-react';
import type { AISettings as AISettingsType } from '../../api/client';

interface AISettingsProps {
  aiSettings: AISettingsType | null;
  handleModelChange: (modelId: string) => void;
  handlePersonaChange: (personaId: string) => void;
}

const AISettings: React.FC<AISettingsProps> = ({ aiSettings, handleModelChange, handlePersonaChange }) => {
  return (
    <div className="flex flex-col gap-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="card">
        <div className="card-header">
          <h3><Bot size={20} /> AI モデルの選択</h3>
        </div>
        <div className="card-body">
          <div className="model-grid">
            {aiSettings?.available_models?.map((model) => (
              <div 
                key={model.id} 
                className={`model-card ${aiSettings?.active_model === model.id ? 'active' : ''}`}
                onClick={() => handleModelChange(model.id)}
              >
                <div className="model-header">
                  <div className="model-name">{model.name}</div>
                  {aiSettings?.active_model === model.id && <CheckCircle2 size={18} className="text-primary" />}
                </div>
                <div className="model-desc">{model.description}</div>
                <div className="model-id">{model.id}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3><Bot size={20} /> AI キャラクター（人格）の選択</h3>
        </div>
        <div className="card-body">
          <div className="model-grid">
            {aiSettings?.available_personas?.map((persona) => (
              <div 
                key={persona.id} 
                className={`model-card ${aiSettings.active_persona === persona.id ? 'active' : ''}`}
                onClick={() => handlePersonaChange(persona.id)}
                style={{ borderColor: aiSettings.active_persona === persona.id ? 'var(--success)' : '' }}
              >
                <div className="model-header">
                  <div className="model-name" style={{ color: aiSettings.active_persona === persona.id ? 'var(--success)' : '' }}>
                    {persona.name}
                  </div>
                  {aiSettings.active_persona === persona.id && <CheckCircle2 size={18} className="text-success" />}
                </div>
                <div className="model-desc">{persona.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISettings;
