# Netlify Environment Variables Configuration

Для правильной работы приложения на Netlify необходимо настроить следующие переменные окружения в настройках сайта:

## Шаги для настройки:

1. Зайдите в панель управления Netlify
2. Выберите ваш сайт kodix.netlify.app
3. Перейдите в Site settings -> Environment variables
4. Добавьте следующие переменные:

### Переменные окружения:

```
REACT_APP_BACKEND_URL=https://ai-coding-51ss.onrender.com
VITE_BACKEND_URL=https://ai-coding-51ss.onrender.com
```

## Альтернативный способ через CLI:

```bash
netlify env:set REACT_APP_BACKEND_URL https://ai-coding-51ss.onrender.com
netlify env:set VITE_BACKEND_URL https://ai-coding-51ss.onrender.com
```

После настройки переменных окружения, пересоберите и разверните сайт.