# 🚀 Инструкция по деплойменту ChatDev Web

## Обзор
- **Backend**: Render.com (бесплатный план)
- **Frontend**: Netlify (бесплатный план)
- **База данных**: В памяти (готова для MongoDB в будущем)

## 📋 Пошаговая инструкция

### 1. Подготовка репозитория

1. **Загрузите код на GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial ChatDev Web application"
   git branch -M main
   git remote add origin https://github.com/your-username/chatdev-web.git
   git push -u origin main
   ```

### 2. Деплоймент Backend на Render

1. **Перейдите на [render.com](https://render.com)**
2. **Создайте новый Web Service**
3. **Подключите ваш GitHub репозиторий**
4. **Настройте параметры**:

   **Basic Settings:**
   - **Name**: `chatdev-web-backend`
   - **Environment**: `Python 3`
   - **Region**: `Frankfurt (EU Central)` (или ближайший)
   - **Branch**: `main`
   - **Root Directory**: `backend`

   **Build & Deploy:**
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     python server.py
     ```

   **Advanced:**
   - **Health Check Path**: `/api/health`
   - **Port**: `8001` (автоматически будет использовать PORT из env)

5. **Environment Variables**:
   ```
   PYTHON_VERSION = 3.11.0
   PORT = 8001
   HOST = 0.0.0.0
   ALLOWED_ORIGINS = *
   ```

6. **Деплой**: Нажмите "Create Web Service"

7. **Получите URL**: После деплоя скопируйте URL (например: `https://chatdev-web-backend.onrender.com`)

### 3. Деплоймент Frontend на Netlify

1. **Перейдите на [netlify.com](https://netlify.com)**
2. **New site from Git**
3. **Выберите ваш GitHub репозиторий**
4. **Настройте параметры**:

   **Build settings:**
   - **Base directory**: `frontend`
   - **Build command**: `yarn build`
   - **Publish directory**: `frontend/dist`

5. **Environment variables** (Site settings → Environment variables):
   ```
   VITE_BACKEND_URL = https://your-render-backend-url.onrender.com
   REACT_APP_BACKEND_URL = https://your-render-backend-url.onrender.com
   ```
   
   **Замените** `your-render-backend-url` на ваш актуальный URL с Render!

6. **Deploy site**: Нажмите "Deploy site"

### 4. Обновление конфигурации

1. **Обновите CORS на backend** (если нужно):
   В файле `backend/server.py` проверьте, что CORS настроен правильно:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # В продакшене укажите конкретные домены
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Обновите netlify.toml**:
   ```toml
   [context.production.environment]
     VITE_BACKEND_URL = "https://your-actual-render-url.onrender.com"
     REACT_APP_BACKEND_URL = "https://your-actual-render-url.onrender.com"
   ```

### 5. Проверка деплоймента

1. **Backend Health Check**:
   ```bash
   curl https://your-render-app.onrender.com/api/health
   ```
   Должен вернуть:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-07-27T...",
     "emergent_available": true,
     "supported_providers": ["openai", "gemini", "anthropic"]
   }
   ```

2. **Frontend проверка**:
   - Откройте ваш Netlify URL
   - Проверьте, что интерфейс загружается
   - Добавьте API ключ в настройках
   - Попробуйте создать тестовый проект

### 6. Настройка домена (опционально)

**Для Render:**
1. Settings → Custom Domains
2. Добавьте ваш домен для backend (например: `api.yourdomain.com`)

**Для Netlify:**
1. Domain settings → Add custom domain
2. Добавьте ваш домен для frontend (например: `yourdomain.com`)

### 7. Мониторинг и логи

**Render:**
- Логи доступны в разделе "Logs"
- Метрики в разделе "Metrics"

**Netlify:**
- Build логи в разделе "Deploys"
- Function логи (если используются)

## 🔧 Troubleshooting

### Backend не запускается
1. Проверьте логи в Render
2. Убедитесь, что `requirements.txt` содержит все зависимости
3. Проверьте Python версию (должна быть 3.11+)

### Frontend не подключается к Backend
1. Проверьте environment variables в Netlify
2. Убедитесь, что URLs правильные (без / в конце)
3. Проверьте CORS настройки в backend

### WebSocket проблемы
1. Убедитесь, что Render поддерживает WebSocket (должен)
2. Проверьте, что используется `wss://` для HTTPS
3. Проверьте firewall настройки

### Медленный холодный старт Render
- Render free tier имеет "холодный старт" после 15 минут неактивности
- Первый запрос может занять 30-60 секунд
- Рассмотрите paid план для production

## 💡 Оптимизация

1. **Кэширование**: Добавьте кэширование статических файлов
2. **CDN**: Netlify автоматически использует CDN
3. **Мониторинг**: Добавьте Sentry или аналог для отслеживания ошибок
4. **База данных**: Подключите MongoDB Atlas для персистентного хранения

## 🔐 Безопасность в продакшене

1. **CORS**: Ограничьте `allow_origins` до конкретных доменов
2. **Rate limiting**: Добавьте лимиты запросов
3. **API ключи**: Убедитесь, что они не логируются
4. **HTTPS**: Обязательно используйте HTTPS (автоматически на Netlify/Render)

---

После успешного деплоймента ваше приложение будет доступно 24/7 и готово к использованию! 🎉