#!/usr/bin/env python3

"""
ИТОГОВЫЙ ТЕСТ - Проверка всех исправлений
Запустите этот скрипт после деплоя для проверки
"""

import requests
import json

# Ваш OpenAI API ключ
OPENAI_KEY = "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"

def test_1_backend_health():
    """Тест 1: Проверка здоровья backend"""
    print("🔄 Тест 1: Проверка backend...")
    try:
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend здоров!")
            print(f"   📊 Версия: {data.get('version')}")
            print(f"   🤖 Модели: {data.get('supported_models', {}).get('openai', [])}")
            
            # Проверяем, что gpt-3.5-turbo есть в списке
            if 'gpt-3.5-turbo' in data.get('supported_models', {}).get('openai', []):
                print("   ✅ Модель gpt-3.5-turbo ПОДДЕРЖИВАЕТСЯ!")
                return True
            else:
                print("   ❌ Модель gpt-3.5-turbo НЕ найдена!")
                return False
        else:
            print(f"   ❌ Backend недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_2_cors():
    """Тест 2: Проверка CORS"""
    print("\n🔄 Тест 2: Проверка CORS...")
    try:
        response = requests.get(
            "https://ai-coding-51ss.onrender.com/api/cors-test",
            headers={"Origin": "https://kodix.netlify.app"},
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ CORS настроен правильно!")
            return True
        else:
            print(f"   ❌ CORS проблема: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_3_frontend():
    """Тест 3: Проверка frontend"""
    print("\n🔄 Тест 3: Проверка frontend...")
    try:
        response = requests.get("https://kodix.netlify.app/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend загружается!")
            print(f"   📏 Размер: {len(response.content)} байт")
            return True
        else:
            print(f"   ❌ Frontend проблема: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_4_session_creation():
    """Тест 4: Создание сессии с gpt-3.5-turbo"""
    print("\n🔄 Тест 4: Создание сессии с РЕАЛЬНЫМ API ключом...")
    try:
        payload = {
            "task": "Создай простую HTML страницу с заголовком Hello World",
            "project_name": "HelloWorldTest",
            "model_type": "gpt-3.5-turbo",  # КРИТИЧНО! Это было сломано
            "api_key": OPENAI_KEY,
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=payload,
            timeout=30
        )
        
        print(f"   📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Сессия создана успешно!")
            print(f"   🆔 Session ID: {data.get('session_id')}")
            print(f"   💬 Сообщение: {data.get('message')}")
            return True
        else:
            print(f"   ❌ Ошибка создания сессии:")
            print(f"   📄 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Исключение: {e}")
        return False

def test_5_openai_direct():
    """Тест 5: Прямой тест OpenAI API"""
    print("\n🔄 Тест 5: Прямой тест OpenAI...")
    try:
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Привет! Это тест."}],
            max_tokens=20
        )
        
        print(f"   ✅ OpenAI API работает!")
        print(f"   💬 Ответ: {response.choices[0].message.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI ошибка: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 ИТОГОВЫЙ ТЕСТ ИСПРАВЛЕНИЙ CHATDEV WEB")
    print("=" * 60)
    
    tests = [
        test_1_backend_health,
        test_2_cors,
        test_3_frontend,
        test_4_session_creation,
        test_5_openai_direct
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print("=" * 60)
    
    test_names = [
        "Backend Health",
        "CORS Setup", 
        "Frontend Loading",
        "Session Creation (gpt-3.5-turbo)",
        "Direct OpenAI API"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛИЛСЯ"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 ИТОГО: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("\n🎉 ПОЗДРАВЛЯЮ! ВСЕ ИСПРАВЛЕНИЯ РАБОТАЮТ!")
        print("🌐 Откройте https://kodix.netlify.app/ и протестируйте!")
        print("🔑 Используйте свой OpenAI API ключ в настройках")
        print("🤖 Выберите модель gpt-3.5-turbo")
        return 0
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        print("📞 Обратитесь за помощью если проблемы продолжаются")
        return 1

if __name__ == "__main__":
    exit(main())