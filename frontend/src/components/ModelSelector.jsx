import React, { useState } from 'react'
import { ChevronDown, Cpu } from 'lucide-react'
import { useApp } from '../context/AppContext'

const MODELS = {
  openai: {
    name: 'OpenAI',
    models: [
      { id: 'GPT_4O', name: 'GPT-4o', description: 'Самая мощная модель' },
      { id: 'GPT_4O_MINI', name: 'GPT-4o Mini', description: 'Быстрая и экономичная' },
      { id: 'GPT_4_TURBO', name: 'GPT-4 Turbo', description: 'Быстрая GPT-4' },
      { id: 'GPT_4', name: 'GPT-4', description: 'Стандартная GPT-4' },
      { id: 'GPT_3_5_TURBO', name: 'GPT-3.5 Turbo', description: 'Быстрая и доступная' }
    ]
  },
  gemini: {
    name: 'Google Gemini',
    models: [
      { id: 'GEMINI_PRO', name: 'Gemini Pro', description: 'Легкий вариант для тестирования' }
    ]
  }
}

function ModelSelector() {
  const { state, actions } = useApp()
  const [isOpen, setIsOpen] = useState(false)
  
  const currentModel = MODELS[state.selectedProvider]?.models.find(
    m => m.id === state.selectedModel
  )
  
  const handleModelSelect = (provider, modelId) => {
    actions.setModel(modelId, provider)
    setIsOpen(false)
  }
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-background-tertiary hover:bg-background-secondary border border-border-primary rounded-lg transition-colors duration-200"
      >
        <Cpu className="w-4 h-4 text-accent-primary" />
        <span className="text-sm text-text-primary">
          {currentModel ? currentModel.name : 'Выберите модель'}
        </span>
        <ChevronDown className={`w-4 h-4 text-text-secondary transition-transform duration-200 ${
          isOpen ? 'rotate-180' : ''
        }`} />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-background-secondary border border-border-primary rounded-lg shadow-lg z-50">
          <div className="p-2">
            {Object.entries(MODELS).map(([provider, providerData]) => (
              <div key={provider} className="mb-4 last:mb-0">
                <div className="px-3 py-2 text-sm font-semibold text-text-secondary uppercase tracking-wide">
                  {providerData.name}
                </div>
                
                {providerData.models.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => handleModelSelect(provider, model.id)}
                    className={`w-full px-3 py-3 text-left rounded-lg transition-colors duration-200 ${
                      state.selectedProvider === provider && state.selectedModel === model.id
                        ? 'bg-accent-primary/10 border border-accent-primary/20'
                        : 'hover:bg-background-tertiary'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-medium text-text-primary">
                          {model.name}
                        </div>
                        <div className="text-xs text-text-secondary">
                          {model.description}
                        </div>
                      </div>
                      
                      {state.selectedProvider === provider && state.selectedModel === model.id && (
                        <div className="w-2 h-2 bg-accent-primary rounded-full" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            ))}
          </div>
          
          <div className="border-t border-border-primary p-3">
            <div className="text-xs text-text-muted">
              Для использования моделей необходимо добавить соответствующие API ключи
            </div>
          </div>
        </div>
      )}
      
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}

export default ModelSelector