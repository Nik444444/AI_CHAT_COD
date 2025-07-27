import React, { useState, useEffect } from 'react'
import { X, File, Folder, Download, ExternalLink, RefreshCw } from 'lucide-react'
import { getSessionFiles } from '../utils/api'

function ProjectPreview({ sessionId, onClose }) {
  const [files, setFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    fetchFiles()
  }, [sessionId])
  
  const fetchFiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getSessionFiles(sessionId)
      setFiles(response.files || [])
      
      // Auto-select main.py or index.html if exists
      const mainFile = response.files?.find(f => 
        f.name === 'main.py' || f.name === 'index.html' || f.name === 'app.py'
      )
      if (mainFile) {
        setSelectedFile(mainFile)
      } else if (response.files?.length > 0) {
        setSelectedFile(response.files[0])
      }
    } catch (err) {
      setError('Ошибка загрузки файлов')
      console.error('Error fetching files:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'py':
        return '🐍'
      case 'js':
      case 'jsx':
        return '⚡'
      case 'html':
        return '🌐'
      case 'css':
        return '🎨'
      case 'json':
        return '📦'
      case 'md':
        return '📝'
      case 'txt':
        return '📄'
      default:
        return '📄'
    }
  }
  
  const formatFileSize = (size) => {
    if (size < 1024) return `${size} B`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  }
  
  const handleDownload = () => {
    if (!selectedFile) return
    
    const blob = new Blob([selectedFile.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = selectedFile.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  const handleDownloadAll = () => {
    // TODO: Implement download all as ZIP
    alert('Функция скачивания всех файлов будет добавлена в следующей версии')
  }
  
  if (loading) {
    return (
      <div className="bg-background-secondary rounded-xl border border-border-primary h-full">
        <div className="flex items-center justify-center h-full">
          <RefreshCw className="w-8 h-8 text-accent-primary animate-spin" />
        </div>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="bg-background-secondary rounded-xl border border-border-primary h-full">
        <div className="flex items-center justify-center h-full flex-col space-y-4">
          <div className="text-accent-error">{error}</div>
          <button onClick={fetchFiles} className="btn-primary">
            Попробовать снова
          </button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-background-secondary rounded-xl border border-border-primary h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-primary">
        <h3 className="text-lg font-semibold text-text-primary">
          Файлы проекта
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownloadAll}
            className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-tertiary transition-colors duration-200"
            title="Скачать все файлы"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-tertiary transition-colors duration-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="flex flex-1 min-h-0">
        {/* File Tree */}
        <div className="w-40 border-r border-border-primary p-4 overflow-y-auto scrollbar-thin">
          <div className="space-y-1">
            {files.map((file, index) => (
              <button
                key={index}
                onClick={() => setSelectedFile(file)}
                className={`w-full text-left p-2 rounded-lg text-sm transition-colors duration-200 ${
                  selectedFile?.name === file.name
                    ? 'bg-accent-primary/10 text-accent-primary border border-accent-primary/20'
                    : 'text-text-secondary hover:text-text-primary hover:bg-background-tertiary'
                }`}
                title={file.path}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-xs">{getFileIcon(file.name)}</span>
                  <span className="truncate">{file.name}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
        
        {/* File Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {selectedFile ? (
            <>
              {/* File Header */}
              <div className="flex items-center justify-between p-4 border-b border-border-primary">
                <div className="flex items-center space-x-2 min-w-0">
                  <span className="text-lg">{getFileIcon(selectedFile.name)}</span>
                  <div className="min-w-0">
                    <div className="font-medium text-text-primary truncate">
                      {selectedFile.name}
                    </div>
                    <div className="text-xs text-text-muted">
                      {formatFileSize(selectedFile.size)}
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={handleDownload}
                  className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-background-tertiary transition-colors duration-200"
                  title="Скачать файл"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
              
              {/* File Content */}
              <div className="flex-1 overflow-auto p-4">
                <pre className="code-block text-xs leading-relaxed">
                  <code>{selectedFile.content}</code>
                </pre>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-text-secondary">
              Выберите файл для просмотра
            </div>
          )}
        </div>
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-border-primary">
        <div className="text-xs text-text-muted">
          Всего файлов: {files.length} • 
          Размер: {files.reduce((acc, file) => acc + file.size, 0) > 0 && 
            formatFileSize(files.reduce((acc, file) => acc + file.size, 0))}
        </div>
      </div>
    </div>
  )
}

export default ProjectPreview