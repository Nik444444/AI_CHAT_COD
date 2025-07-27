import React, { createContext, useContext, useReducer, useEffect } from 'react'

const AppContext = createContext()

const initialState = {
  currentSession: null,
  sessions: [],
  apiKeys: {
    openai: '',
    gemini: ''
  },
  selectedModel: 'GPT_4O_MINI',
  selectedProvider: 'openai',
  isConnected: false,
  chatMessages: [],
  isGenerating: false,
  projects: []
}

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_API_KEY':
      return {
        ...state,
        apiKeys: {
          ...state.apiKeys,
          [action.payload.provider]: action.payload.key
        }
      }
    
    case 'SET_MODEL':
      return {
        ...state,
        selectedModel: action.payload.model,
        selectedProvider: action.payload.provider
      }
    
    case 'SET_CURRENT_SESSION':
      return {
        ...state,
        currentSession: action.payload,
        chatMessages: []
      }
    
    case 'ADD_CHAT_MESSAGE':
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload]
      }
    
    case 'SET_GENERATING':
      return {
        ...state,
        isGenerating: action.payload
      }
    
    case 'SET_SESSIONS':
      return {
        ...state,
        sessions: action.payload
      }
    
    case 'ADD_SESSION':
      return {
        ...state,
        sessions: [...state.sessions, action.payload]
      }
    
    case 'REMOVE_SESSION':
      return {
        ...state,
        sessions: state.sessions.filter(s => s.session_id !== action.payload),
        currentSession: state.currentSession?.session_id === action.payload ? null : state.currentSession
      }
    
    case 'SET_CONNECTION_STATUS':
      return {
        ...state,
        isConnected: action.payload
      }
    
    case 'CLEAR_CHAT':
      return {
        ...state,
        chatMessages: []
      }
    
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)
  
  // Load saved data from localStorage
  useEffect(() => {
    const savedApiKeys = localStorage.getItem('chatdev_api_keys')
    const savedModel = localStorage.getItem('chatdev_selected_model')
    const savedProvider = localStorage.getItem('chatdev_selected_provider')
    
    if (savedApiKeys) {
      const keys = JSON.parse(savedApiKeys)
      Object.entries(keys).forEach(([provider, key]) => {
        if (key) {
          dispatch({ type: 'SET_API_KEY', payload: { provider, key } })
        }
      })
    }
    
    if (savedModel && savedProvider) {
      dispatch({ 
        type: 'SET_MODEL', 
        payload: { model: savedModel, provider: savedProvider }
      })
    }
  }, [])
  
  // Save API keys to localStorage
  useEffect(() => {
    localStorage.setItem('chatdev_api_keys', JSON.stringify(state.apiKeys))
  }, [state.apiKeys])
  
  // Save model selection to localStorage
  useEffect(() => {
    localStorage.setItem('chatdev_selected_model', state.selectedModel)
    localStorage.setItem('chatdev_selected_provider', state.selectedProvider)
  }, [state.selectedModel, state.selectedProvider])
  
  const actions = {
    setApiKey: (provider, key) => {
      dispatch({ type: 'SET_API_KEY', payload: { provider, key } })
    },
    
    setModel: (model, provider) => {
      dispatch({ type: 'SET_MODEL', payload: { model, provider } })
    },
    
    setCurrentSession: (session) => {
      dispatch({ type: 'SET_CURRENT_SESSION', payload: session })
    },
    
    addChatMessage: (message) => {
      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: message })
    },
    
    setGenerating: (isGenerating) => {
      dispatch({ type: 'SET_GENERATING', payload: isGenerating })
    },
    
    setSessions: (sessions) => {
      dispatch({ type: 'SET_SESSIONS', payload: sessions })
    },
    
    addSession: (session) => {
      dispatch({ type: 'ADD_SESSION', payload: session })
    },
    
    removeSession: (sessionId) => {
      dispatch({ type: 'REMOVE_SESSION', payload: sessionId })
    },
    
    setConnectionStatus: (isConnected) => {
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: isConnected })
    },
    
    clearChat: () => {
      dispatch({ type: 'CLEAR_CHAT' })
    }
  }
  
  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

export default AppContext