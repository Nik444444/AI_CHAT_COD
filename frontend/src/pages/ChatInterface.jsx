import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2, AlertCircle, CheckCircle, Cpu, User } from 'lucide-react'
import { useApp } from '../context/AppContext'
import { createSession, connectWebSocket } from '../utils/api'
import ChatMessage from '../components/ChatMessage'
import ProjectPreview from '../components/ProjectPreview'

function ChatInterface() {
  const { state, actions } = useApp()
  const [input, setInput] = useState('')
  const [projectName, setProjectName] = useState('')
  const [websocket, setWebsocket] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [state.chatMessages])
  
  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus()
  }, [])
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!input.trim() || !projectName.trim()) return
    
    const currentApiKey = state.apiKeys[state.selectedProvider]
    if (!currentApiKey) {
      actions.addChatMessage({
        type: 'error',
        content: 'Пожалуйста, добавьте API ключ в настройках',
        timestamp: new Date().toISOString()
      })
      return
    }
    
    try {
      actions.setGenerating(true)
      
      // Add user message
      actions.addChatMessage({
        type: 'user',
        content: input,
        timestamp: new Date().toISOString(),
        projectName
      })
      
      // Create session
      const response = await createSession({
        task: input,
        project_name: projectName,
        model_type: state.selectedModel,
        api_key: currentApiKey,
        provider: state.selectedProvider
      })
      
      if (response.session_id) {
        actions.setCurrentSession(response)
        actions.addSession(response)
        
        // Connect WebSocket
        const ws = connectWebSocket(response.session_id, (message) => {
          handleWebSocketMessage(message)
        })
        
        setWebsocket(ws)
        actions.setConnectionStatus(true)
      }
      
      // Clear inputs
      setInput('')
      setProjectName('')
      
    } catch (error) {
      console.error('Error creating session:', error)
      actions.addChatMessage({
        type: 'error',
        content: `Ошибка создания сессии: ${error.message}`,
        timestamp: new Date().toISOString()
      })
    } finally {
      actions.setGenerating(false)
    }
  }
  
  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'status':
        actions.addChatMessage({
          type: 'system',
          content: message.data.message,
          timestamp: new Date().toISOString(),
          status: message.data.status
        })
        
        if (message.data.status === 'completed') {
          actions.setGenerating(false)
          setShowPreview(true)
        }
        break
        
      case 'agent_message':
        actions.addChatMessage({
          type: 'agent',
          role: message.data.role,
          content: message.data.message,
          timestamp: message.data.timestamp
        })
        break
        
      case 'error':
        actions.addChatMessage({
          type: 'error',
          content: message.data.message,
          timestamp: new Date().toISOString()
        })
        actions.setGenerating(false)
        break
        
      default:
        console.log('Unknown message type:', message.type)
    }
  }
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }
  
  const hasApiKey = state.apiKeys[state.selectedProvider]
  
  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gradient mb-2">
          Создайте приложение с помощью ИИ
        </h1>
        <p className="text-text-secondary">
          Опишите ваше приложение на русском языке, и команда ИИ агентов создаст его для вас
        </p>
      </div>
      
      {/* Main Content */}
      <div className="flex flex-1 gap-6 min-h-0">
        {/* Chat Panel */}
        <div className="flex-1 flex flex-col bg-background-secondary rounded-xl border border-border-primary">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
            {state.chatMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full flex items-center justify-center mb-4">
                  <Cpu className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-text-primary mb-2">
                  Добро пожаловать в ChatDev!
                </h3>
                <p className="text-text-secondary mb-6 max-w-md">
                  Опишите приложение, которое хотите создать, и наши ИИ агенты начнут работу над ним
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
                  <div className="p-4 bg-background-primary rounded-lg border border-border-primary">
                    <h4 className="font-medium text-text-primary mb-2">Пример 1</h4>
                    <p className="text-sm text-text-secondary">
                      "Создай игру Тетрис с современным интерфейсом и подсчетом очков"
                    </p>
                  </div>
                  <div className="p-4 bg-background-primary rounded-lg border border-border-primary">
                    <h4 className="font-medium text-text-primary mb-2">Пример 2</h4>
                    <p className="text-sm text-text-secondary">
                      "Сделай приложение для заметок с поиском и категориями"
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              state.chatMessages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))
            )}
            
            {state.isGenerating && (
              <div className="flex items-center space-x-3 p-4 bg-background-primary rounded-lg border border-border-primary">
                <Loader2 className="w-5 h-5 text-accent-primary animate-spin" />
                <span className="text-text-secondary">Агенты работают над проектом...</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input Form */}
          <div className="border-t border-border-primary p-6">
            {!hasApiKey && (
              <div className="flex items-center space-x-2 mb-4 p-3 bg-accent-warning/10 border border-accent-warning/20 rounded-lg">
                <AlertCircle className="w-5 h-5 text-accent-warning" />
                <span className="text-sm text-accent-warning">
                  Необходимо добавить API ключ для {state.selectedProvider.toUpperCase()} в настройках
                </span>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Название проекта (например: TodoApp)"
                  className="input-field flex-1"
                  disabled={state.isGenerating}
                />
              </div>
              
              <div className="flex gap-4">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Опишите ваше приложение подробно..."
                  className="input-field flex-1 min-h-[100px] resize-none"
                  disabled={state.isGenerating || !hasApiKey}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || !projectName.trim() || state.isGenerating || !hasApiKey}
                  className="btn-primary px-6 h-fit disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {state.isGenerating ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              <div className="text-xs text-text-muted">
                Нажмите Enter для отправки • Shift+Enter для новой строки
              </div>
            </form>
          </div>
        </div>
        
        {/* Project Preview Panel */}
        {showPreview && state.currentSession && (
          <div className="w-96 flex-shrink-0">
            <ProjectPreview 
              sessionId={state.currentSession.session_id}
              onClose={() => setShowPreview(false)}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatInterface