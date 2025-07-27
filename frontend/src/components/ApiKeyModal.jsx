import React, { useState } from 'react'
import { X, Eye, EyeOff, Key, ExternalLink } from 'lucide-react'
import { useApp } from '../context/AppContext'

function ApiKeyModal({ isOpen, onClose }) {
  const { state, actions } = useApp()
  const [showKeys, setShowKeys] = useState({})
  const [tempKeys, setTempKeys] = useState({
    openai: state.apiKeys.openai || '',
    gemini: state.apiKeys.gemini || ''
  })
  
  if (!isOpen) return null
  
  const toggleKeyVisibility = (provider) => {
    setShowKeys(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }
  
  const handleKeyChange = (provider, value) => {
    setTempKeys(prev => ({
      ...prev,
      [provider]: value
    }))
  }
  
  const handleSave = () => {
    Object.entries(tempKeys).forEach(([provider, key]) => {
      if (key !== state.apiKeys[provider]) {
        actions.setApiKey(provider, key)
      }
    })
    onClose()
  }
  
  const providers = [
    {
      id: 'openai',
      name: 'OpenAI',
      description: 'Для использования GPT моделей',
      helpUrl: 'https://platform.openai.com/api-keys',
      placeholder: 'sk-proj-...'
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Для использования Gemini моделей (легкий вариант)',
      helpUrl: 'https://aistudio.google.com/app/apikey',
      placeholder: 'AIza...'
    }
  ]
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background-secondary border border-border-primary rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border-primary">
          <div className="flex items-center space-x-3">
            <Key className="w-6 h-6 text-accent-primary" />
            <h2 className="text-xl font-semibold text-text-primary">
              Управление API ключами
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-tertiary transition-colors duration-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          <div className="bg-accent-primary/10 border border-accent-primary/20 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-accent-primary mb-2">
              Важная информация
            </h3>
            <p className="text-sm text-text-secondary">
              API ключи хранятся локально в вашем браузере и не передаются на сервер. 
              Для безопасности используйте ключи с ограниченными правами.
            </p>
          </div>
          
          {providers.map((provider) => (
            <div key={provider.id} className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    {provider.name}
                  </h3>
                  <p className="text-sm text-text-secondary">
                    {provider.description}
                  </p>
                </div>
                <a
                  href={provider.helpUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-accent-primary hover:text-accent-primary/80 text-sm transition-colors duration-200"
                >
                  <span>Получить ключ</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              
              <div className="relative">
                <input
                  type={showKeys[provider.id] ? 'text' : 'password'}
                  value={tempKeys[provider.id]}
                  onChange={(e) => handleKeyChange(provider.id, e.target.value)}
                  placeholder={provider.placeholder}
                  className="input-field w-full pr-12 font-mono text-sm"
                />
                <button
                  onClick={() => toggleKeyVisibility(provider.id)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors duration-200"
                >
                  {showKeys[provider.id] ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              
              {state.apiKeys[provider.id] && (
                <div className="flex items-center space-x-2 text-sm text-accent-success">
                  <div className="w-2 h-2 bg-accent-success rounded-full" />
                  <span>API ключ сохранен</span>
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="flex items-center justify-end gap-3 p-6 border-t border-border-primary">
          <button
            onClick={onClose}
            className="btn-secondary"
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            className="btn-primary"
          >
            Сохранить ключи
          </button>
        </div>
      </div>
    </div>
  )
}

export default ApiKeyModal