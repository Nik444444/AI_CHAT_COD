import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Settings, Cpu, Key, Palette } from 'lucide-react'
import { useApp } from '../context/AppContext'
import ModelSelector from './ModelSelector'
import ApiKeyModal from './ApiKeyModal'

function Header() {
  const location = useLocation()
  const { state } = useApp()
  const [showSettings, setShowSettings] = useState(false)
  const [showApiModal, setShowApiModal] = useState(false)
  
  const hasApiKey = state.apiKeys[state.selectedProvider]
  
  return (
    <>
      <header className="bg-background-secondary border-b border-border-primary">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-lg flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gradient">ChatDev Web</span>
              </Link>
              
              <nav className="hidden md:flex space-x-4">
                <Link 
                  to="/" 
                  className={`px-3 py-2 rounded-lg transition-colors duration-200 ${
                    location.pathname === '/' 
                      ? 'bg-accent-primary/10 text-accent-primary' 
                      : 'text-text-secondary hover:text-text-primary hover:bg-background-primary'
                  }`}
                >
                  Создать проект
                </Link>
                <Link 
                  to="/projects" 
                  className={`px-3 py-2 rounded-lg transition-colors duration-200 ${
                    location.pathname === '/projects' 
                      ? 'bg-accent-primary/10 text-accent-primary' 
                      : 'text-text-secondary hover:text-text-primary hover:bg-background-primary'
                  }`}
                >
                  Мои проекты
                </Link>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  state.isConnected ? 'bg-accent-success' : 'bg-accent-error'
                }`} />
                <span className="text-sm text-text-secondary">
                  {state.isConnected ? 'Подключено' : 'Отключено'}
                </span>
              </div>
              
              {/* API Key Status */}
              <button
                onClick={() => setShowApiModal(true)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                  hasApiKey 
                    ? 'text-accent-success hover:bg-accent-success/10' 
                    : 'text-accent-warning hover:bg-accent-warning/10'
                }`}
              >
                <Key className="w-4 h-4" />
                <span className="text-sm">
                  {hasApiKey ? 'API ключ установлен' : 'Нужен API ключ'}
                </span>
              </button>
              
              {/* Model Selector */}
              <ModelSelector />
              
              {/* Settings */}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-primary transition-colors duration-200"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Mobile Navigation */}
          <nav className="md:hidden mt-4 flex space-x-4">
            <Link 
              to="/" 
              className={`px-3 py-2 rounded-lg transition-colors duration-200 ${
                location.pathname === '/' 
                  ? 'bg-accent-primary/10 text-accent-primary' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-primary'
              }`}
            >
              Создать проект
            </Link>
            <Link 
              to="/projects" 
              className={`px-3 py-2 rounded-lg transition-colors duration-200 ${
                location.pathname === '/projects' 
                  ? 'bg-accent-primary/10 text-accent-primary' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-primary'
              }`}
            >
              Мои проекты
            </Link>
          </nav>
        </div>
        
        {/* Settings Dropdown */}
        {showSettings && (
          <div className="absolute right-4 top-16 w-64 bg-background-secondary border border-border-primary rounded-lg shadow-lg z-50">
            <div className="p-4 space-y-4">
              <h3 className="text-lg font-semibold text-text-primary">Настройки</h3>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-text-secondary">
                  Текущая модель
                </label>
                <div className="text-sm text-text-primary">
                  {state.selectedProvider.toUpperCase()} - {state.selectedModel}
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-text-secondary">
                  Активных сессий
                </label>
                <div className="text-sm text-text-primary">
                  {state.sessions.length}
                </div>
              </div>
              
              <button
                onClick={() => setShowApiModal(true)}
                className="w-full btn-secondary text-left"
              >
                <Key className="w-4 h-4 inline mr-2" />
                Управление API ключами
              </button>
            </div>
          </div>
        )}
      </header>
      
      <ApiKeyModal 
        isOpen={showApiModal} 
        onClose={() => setShowApiModal(false)} 
      />
    </>
  )
}

export default Header