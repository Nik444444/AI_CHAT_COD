import React from 'react'
import { User, Cpu, AlertCircle, CheckCircle, Info } from 'lucide-react'

function ChatMessage({ message }) {
  const getMessageIcon = () => {
    switch (message.type) {
      case 'user':
        return <User className="w-5 h-5" />
      case 'agent':
        return <Cpu className="w-5 h-5" />
      case 'system':
        return <Info className="w-5 h-5" />
      case 'error':
        return <AlertCircle className="w-5 h-5" />
      default:
        return <Cpu className="w-5 h-5" />
    }
  }
  
  const getMessageStyle = () => {
    switch (message.type) {
      case 'user':
        return 'message-user border-l-4 border-l-accent-primary'
      case 'agent':
        return 'message-agent border-l-4 border-l-accent-secondary'
      case 'system':
        return 'message-agent border-l-4 border-l-accent-success'
      case 'error':
        return 'message-agent border-l-4 border-l-accent-error'
      default:
        return 'message-agent'
    }
  }
  
  const getHeaderText = () => {
    switch (message.type) {
      case 'user':
        return 'Вы'
      case 'agent':
        return message.role || 'AI Agent'
      case 'system':
        return 'Система'
      case 'error':
        return 'Ошибка'
      default:
        return 'AI Agent'
    }
  }
  
  const getHeaderColor = () => {
    switch (message.type) {
      case 'user':
        return 'text-accent-primary'
      case 'agent':
        return 'text-accent-secondary'
      case 'system':
        return 'text-accent-success'
      case 'error':
        return 'text-accent-error'
      default:
        return 'text-text-primary'
    }
  }
  
  return (
    <div className={`chat-message ${getMessageStyle()}`}>
      <div className="flex items-start space-x-3">
        <div className={`p-2 rounded-lg ${
          message.type === 'user' 
            ? 'bg-accent-primary/10 text-accent-primary' 
            : message.type === 'error'
            ? 'bg-accent-error/10 text-accent-error'
            : message.type === 'system'
            ? 'bg-accent-success/10 text-accent-success'
            : 'bg-accent-secondary/10 text-accent-secondary'
        }`}>
          {getMessageIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h4 className={`font-semibold ${getHeaderColor()}`}>
              {getHeaderText()}
            </h4>
            <span className="text-xs text-text-muted">
              {new Date(message.timestamp).toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
          
          {message.projectName && (
            <div className="mb-2 text-sm text-text-secondary">
              <span className="font-medium">Проект:</span> {message.projectName}
            </div>
          )}
          
          <div className="text-text-primary whitespace-pre-wrap">
            {message.content}
          </div>
          
          {message.status && (
            <div className="mt-2 flex items-center space-x-2">
              {message.status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-accent-success" />
              ) : (
                <div className="w-4 h-4 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
              )}
              <span className="text-sm text-text-secondary">
                Статус: {message.status}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage