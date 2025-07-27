import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AppProvider } from './context/AppContext'
import Header from './components/Header'
import ChatInterface from './pages/ChatInterface'
import ProjectList from './pages/ProjectList'
import './App.css'

function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-background-primary">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<ChatInterface />} />
            <Route path="/projects" element={<ProjectList />} />
          </Routes>
        </main>
      </div>
    </AppProvider>
  )
}

export default App