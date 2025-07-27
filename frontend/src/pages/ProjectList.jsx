import React, { useEffect, useState } from 'react'
import { Folder, Calendar, Cpu, Trash2, Download, Eye, MoreVertical } from 'lucide-react'
import { useApp } from '../context/AppContext'
import { getSessions, deleteSession, getSessionFiles } from '../utils/api'

function ProjectList() {
  const { state, actions } = useApp()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showActions, setShowActions] = useState(null)
  
  useEffect(() => {
    fetchSessions()
  }, [])
  
  const fetchSessions = async () => {
    try {
      setLoading(true)
      const response = await getSessions()
      actions.setSessions(response.sessions)
    } catch (err) {
      setError('Ошибка загрузки проектов')
      console.error('Error fetching sessions:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleDeleteProject = async (sessionId) => {
    if (!confirm('Вы уверены, что хотите удалить этот проект?')) return
    
    try {
      await deleteSession(sessionId)
      actions.removeSession(sessionId)
      if (selectedProject?.session_id === sessionId) {
        setSelectedProject(null)
      }
    } catch (err) {
      console.error('Error deleting session:', err)
      alert('Ошибка удаления проекта')
    }
  }
  
  const handleViewProject = async (session) => {
    try {
      const files = await getSessionFiles(session.session_id)
      setSelectedProject({ ...session, files: files.files })
    } catch (err) {
      console.error('Error fetching project files:', err)
      alert('Ошибка загрузки файлов проекта')
    }
  }
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-accent-success bg-accent-success/10 border-accent-success/20'
      case 'running':
        return 'text-accent-primary bg-accent-primary/10 border-accent-primary/20'
      case 'error':
        return 'text-accent-error bg-accent-error/10 border-accent-error/20'
      default:
        return 'text-text-secondary bg-background-primary border-border-primary'
    }
  }
  
  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Завершен'
      case 'running': return 'В процессе'
      case 'error': return 'Ошибка'
      case 'created': return 'Создан'
      default: return status
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary"></div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-accent-error text-lg mb-2">{error}</div>
        <button onClick={fetchSessions} className="btn-primary">
          Попробовать снова
        </button>
      </div>
    )
  }
  
  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gradient mb-2">
          Мои проекты
        </h1>
        <p className="text-text-secondary">
          Управляйте созданными проектами и просматривайте их содержимое
        </p>
      </div>
      
      <div className="flex flex-1 gap-6 min-h-0">
        {/* Projects List */}
        <div className="flex-1 bg-background-secondary rounded-xl border border-border-primary">
          <div className="p-6 border-b border-border-primary">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-text-primary">
                Проекты ({state.sessions.length})
              </h2>
              <button
                onClick={fetchSessions}
                className="btn-secondary text-sm"
              >
                Обновить
              </button>
            </div>
          </div>
          
          <div className="p-6">
            {state.sessions.length === 0 ? (
              <div className="text-center py-12">
                <Folder className="w-12 h-12 text-text-muted mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Пока нет проектов
                </h3>
                <p className="text-text-secondary mb-4">
                  Создайте ваш первый проект в чате
                </p>
                <button
                  onClick={() => window.location.href = '/'}
                  className="btn-primary"
                >
                  Создать проект
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {state.sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`project-card p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                      selectedProject?.session_id === session.session_id
                        ? 'border-accent-primary bg-accent-primary/5'
                        : 'border-border-primary bg-background-primary hover:border-border-secondary'
                    }`}
                    onClick={() => handleViewProject(session)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <div className="w-10 h-10 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                          <Folder className="w-5 h-5 text-white" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-semibold text-text-primary mb-1 truncate">
                            {session.project_name}
                          </h3>
                          <p className="text-text-secondary text-sm mb-2 line-clamp-2">
                            {session.task}
                          </p>
                          
                          <div className="flex items-center space-x-4 text-sm">
                            <div className="flex items-center space-x-1 text-text-muted">
                              <Calendar className="w-4 h-4" />
                              <span>
                                {new Date(session.created_at).toLocaleDateString('ru-RU')}
                              </span>
                            </div>
                            
                            <div className="flex items-center space-x-1 text-text-muted">
                              <Cpu className="w-4 h-4" />
                              <span>{session.model_type}</span>
                            </div>
                            
                            <div className={`px-2 py-1 rounded text-xs border ${getStatusColor(session.status)}`}>
                              {getStatusText(session.status)}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="relative">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setShowActions(showActions === session.session_id ? null : session.session_id)
                          }}
                          className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-secondary transition-colors duration-200"
                        >
                          <MoreVertical className="w-4 h-4" />
                        </button>
                        
                        {showActions === session.session_id && (
                          <div className="absolute right-0 top-full mt-2 w-48 bg-background-secondary border border-border-primary rounded-lg shadow-lg z-10">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleViewProject(session)
                                setShowActions(null)
                              }}
                              className="w-full px-4 py-2 text-left text-text-primary hover:bg-background-tertiary flex items-center space-x-2"
                            >
                              <Eye className="w-4 h-4" />
                              <span>Просмотреть</span>
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                // TODO: Implement download
                                setShowActions(null)
                              }}
                              className="w-full px-4 py-2 text-left text-text-primary hover:bg-background-tertiary flex items-center space-x-2"
                            >
                              <Download className="w-4 h-4" />
                              <span>Скачать</span>
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDeleteProject(session.session_id)
                                setShowActions(null)
                              }}
                              className="w-full px-4 py-2 text-left text-accent-error hover:bg-accent-error/10 flex items-center space-x-2"
                            >
                              <Trash2 className="w-4 h-4" />
                              <span>Удалить</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Project Details */}
        {selectedProject && (
          <div className="w-96 bg-background-secondary rounded-xl border border-border-primary">
            <div className="p-6 border-b border-border-primary">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                {selectedProject.project_name}
              </h3>
              <p className="text-text-secondary text-sm">
                {selectedProject.task}
              </p>
            </div>
            
            <div className="p-6">
              <h4 className="text-md font-semibold text-text-primary mb-4">
                Файлы проекта ({selectedProject.files?.length || 0})
              </h4>
              
              {selectedProject.files && selectedProject.files.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
                  {selectedProject.files.map((file, index) => (
                    <div
                      key={index}
                      className="p-3 bg-background-primary rounded-lg border border-border-primary"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-text-primary font-medium text-sm">
                          {file.name}
                        </span>
                        <span className="text-text-muted text-xs">
                          {(file.size / 1024).toFixed(1)} KB
                        </span>
                      </div>
                      <div className="text-text-secondary text-xs">
                        {file.path}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-text-secondary">
                  Файлы не найдены
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Click outside to close actions */}
      {showActions && (
        <div
          className="fixed inset-0 z-5"
          onClick={() => setShowActions(null)}
        />
      )}
    </div>
  )
}

export default ProjectList