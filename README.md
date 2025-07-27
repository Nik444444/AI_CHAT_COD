# ChatDev Web - AI-Powered Software Development Platform

Веб-приложение для создания программного обеспечения с помощью многоагентной ИИ системы, аналог Emergent.sh на базе open-source технологий.

## 🚀 Возможности

- **Мульти-агентная разработка**: 5 ИИ агентов работают вместе (CEO, CTO, Programmer, Code Reviewer, QA Tester)
- **Поддержка множественных моделей**: OpenAI GPT, Google Gemini, Anthropic Claude
- **Современный интерфейс**: Темная тема в стиле Emergent.sh
- **Реальное время**: WebSocket для live обновлений
- **Управление проектами**: Создание, просмотр, удаление проектов
- **Безопасность**: API ключи хранятся локально в браузере

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк
- **EmergentIntegrations** - интеграция с LLM моделями
- **WebSockets** - реальное время обновления
- **Python 3.11+**

### Frontend
- **React 18** с Vite
- **TailwindCSS** - стилизация
- **TanStack Query** - управление состоянием API
- **Context API** - глобальное состояние

## 📦 Деплоймент

### Backend на Render

1. **Подключите репозиторий к Render**
2. **Настройте переменные окружения**:
   ```
   PYTHON_VERSION=3.11.0
   PORT=8001
   HOST=0.0.0.0
   ALLOWED_ORIGINS=*
   ```
3. **Build Command**: `cd backend && pip install -r requirements.txt`
4. **Start Command**: `cd backend && python server.py`
5. **Health Check**: `/api/health`

### Frontend на Netlify

1. **Подключите репозиторий к Netlify**
2. **Build Settings**:
   - **Build command**: `cd frontend && yarn build`
   - **Publish directory**: `frontend/dist`
3. **Environment Variables**:
   ```
   VITE_BACKEND_URL=https://your-render-app.onrender.com
   REACT_APP_BACKEND_URL=https://your-render-app.onrender.com
   ```
4. **Redirects** настроены автоматически через `netlify.toml`

## 🔧 Локальная разработка

### Предварительные требования
- Python 3.11+
- Node.js 18+
- Yarn

### Запуск Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```
Backend будет доступен на `http://localhost:8001`

### Запуск Frontend
```bash
cd frontend
yarn install
yarn dev
```
Frontend будет доступен на `http://localhost:3000`

## 🤖 Поддерживаемые модели

### OpenAI
- gpt-4o, gpt-4o-mini
- gpt-4-turbo, gpt-4
- gpt-3.5-turbo
- o1, o1-mini, o1-pro

### Google Gemini
- gemini-2.0-flash
- gemini-1.5-pro, gemini-1.5-flash

### Anthropic Claude
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022

## 📝 Использование

1. **Добавьте API ключ** для выбранного провайдера (OpenAI, Gemini, Claude)
2. **Выберите модель** в селекторе
3. **Опишите проект** на естественном языке
4. **Наблюдайте** как агенты создают ваше приложение
5. **Просматривайте** и скачивайте сгенерированные файлы

## 🔒 Безопасность

- API ключи хранятся только в локальном хранилище браузера
- Ключи не передаются на сервер для хранения
- CORS настроен для безопасного взаимодействия
- Все коммуникации по HTTPS в продакшене

## 🎯 Архитектура агентов

1. **CEO** - анализирует требования и определяет бизнес-цели
2. **CTO** - проектирует техническую архитектуру
3. **Programmer** - реализует код приложения
4. **Code Reviewer** - проверяет качество и безопасность кода
5. **QA Tester** - создает стратегию тестирования

## 🚧 API Эндпоинты

- `GET /api/health` - проверка состояния
- `GET /api/sessions` - список сессий
- `POST /api/sessions` - создание новой сессии
- `DELETE /api/sessions/{id}` - удаление сессии
- `GET /api/sessions/{id}/files` - файлы проекта
- `WS /api/sessions/{id}/ws` - WebSocket для реального времени

## 📄 Лицензия

MIT License - см. файл LICENSE

## 🤝 Вклад в проект

Приветствуются пулл-реквесты и issue! Пожалуйста, следуйте:
1. Форкните репозиторий
2. Создайте feature-ветку
3. Сделайте коммит изменений
4. Отправьте пулл-реквест

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
1. Проверьте существующие issues
2. Создайте новый issue с подробным описанием
3. Укажите версии браузера/Node.js/Python

---

**Made with ❤️ using AI agents**