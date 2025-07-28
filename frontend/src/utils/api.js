const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'https://ai-coding-51ss.onrender.com'

// FIXED: Add better error handling and logging
console.log('API_BASE_URL configured:', API_BASE_URL)

class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: response.statusText }
    }
    
    throw new APIError(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    )
  }
  
  return response.json()
}

export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`)
    return handleResponse(response)
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}

export async function createSession(sessionData) {
  try {
    console.log('Creating session with data:', sessionData)
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sessionData)
    })
    
    return handleResponse(response)
  } catch (error) {
    console.error('Create session failed:', error)
    throw error
  }
}

export async function getSessions() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions`)
    return handleResponse(response)
  } catch (error) {
    console.error('Get sessions failed:', error)
    throw error
  }
}

export async function deleteSession(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
      method: 'DELETE'
    })
    
    return handleResponse(response)
  } catch (error) {
    console.error('Delete session failed:', error)
    throw error
  }
}

export async function getSessionFiles(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/files`)
    return handleResponse(response)
  } catch (error) {
    console.error('Get session files failed:', error)
    throw error
  }
}

export function connectWebSocket(sessionId, onMessage, onError, onClose) {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/sessions/${sessionId}/ws`
  
  console.log('Connecting to WebSocket:', wsUrl)
  
  try {
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        onMessage(message)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
        onError?.(error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      onError?.(error)
    }
    
    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)
      onClose?.(event)
    }
    
    return ws
  } catch (error) {
    console.error('Failed to create WebSocket:', error)
    onError?.(error)
    return null
  }
}

export default {
  healthCheck,
  createSession,
  getSessions,
  deleteSession,
  getSessionFiles,
  connectWebSocket
}