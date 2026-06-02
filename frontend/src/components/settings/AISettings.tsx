import React from 'react';
import { Bot, CheckCircle2, Cpu } from 'lucide-react';
import type { AISettings as AISettingsType } from '../../api/client';
import PersonaCard from './PersonaCard';

interface AISettingsProps {
  aiSettings: AISettingsType | null;
  handleModelChange: (modelId: string) => void;
  handlePersonaChange: (personaId: string) => void;
}

const AISettings: React.FC<AISettingsProps> = ({ aiSettings, handleModelChange, handlePersonaChange }) => {
  return (
    <div className="flex flex-col gap-8" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <div className="card-header">
          <h3><Cpu size={20} /> AI モデルの選択</h3>
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
            {aiSettings?.available_personas?.map((persona) => (
              <PersonaCard
                key={persona.id}
                id={persona.id}
                name={persona.name}
                description={persona.description || ''}
                isActive={aiSettings.active_persona === persona.id}
                onClick={() => handlePersonaChange(persona.id)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISettings;
