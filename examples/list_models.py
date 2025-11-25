"""
Скрипт для получения списка доступных моделей Polza.AI
Цель: Показать список моделей с поддержкой генерации изображений и их цены.
"""

import sys
import os
import requests
from dotenv import load_dotenv

# Добавляем путь к папке src, чтобы Python мог найти наш модуль (если понадобится)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Загружаем переменные окружения
load_dotenv()

def get_models():
    """
    Получает список моделей через API Polza.AI
    """
    # Базовый URL API
    base_url = os.getenv('POLZA_API_URL', 'https://api.polza.ai/v1')
    endpoint = f"{base_url}/models"
    
    print(f"🔍 Запрос списка моделей с: {endpoint} ...")
    
    try:
        # Отправляем GET запрос (аутентификация не требуется согласно документации,
        # но часто лучше передать ключ если он есть, на всякий случай)
        # В документации сказано "Без аутентификации", поэтому headers можно не слать,
        # но requests.get просто так сработает.
        
        response = requests.get(endpoint)
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        
        # Проверяем структуру ответа
        if 'data' not in data:
            print("❌ Некорректный ответ API (нет поля 'data')")
            return
            
        models = data['data']
        print(f"✅ Получено моделей: {len(models)}")
        print("=" * 80)
        
        # Фильтруем модели для изображений (input_modalities содержит 'image' или 'text' -> 'image')
        # В документации: architecture.input_modalities: ["text", "image"] - это обычно для Vision моделей (анализ картинок)
        # Нам нужны модели ГЕНЕРАЦИИ картинок. 
        # Часто у них output_modalities = ["image"] или input="text", output="image".
        # Давайте искать по ключевым словам и output_modalities если есть.
        
        image_gen_models = []
        vision_models = []
        text_models = []
        
        for m in models:
            arch = m.get('architecture', {})
            input_mod = arch.get('input_modalities', [])
            output_mod = arch.get('output_modalities', [])
            name = m.get('name', 'Unknown')
            mid = m.get('id', '')
            
            # Определение типа модели
            is_img_gen = 'image' in output_mod or 'flux' in mid.lower() or 'sd' in mid.lower() or 'dall' in mid.lower() or 'midjourney' in mid.lower() or 'nano' in mid.lower()
            is_vision = 'image' in input_mod and 'text' in output_mod
            
            if is_img_gen:
                image_gen_models.append(m)
            elif is_vision:
                vision_models.append(m)
            else:
                text_models.append(m)

        # Выводим модели для генерации изображений
        print(f"🎨 МОДЕЛИ ДЛЯ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ ({len(image_gen_models)}):")
        print(f"{'ID Модели':<50} | {'Название':<30} | {'Цена (RUB/шт)'}")
        print("-" * 100)
        
        for m in image_gen_models:
            mid = m.get('id')
            name = m.get('name')[:30]
            pricing = m.get('pricing', {})
            # Цена за изображение
            price_img1 = pricing.get('prompt', 'N/A')
            price_img2 = pricing.get('completion', 'N/A')
            price_img3 = pricing.get('image', 'N/A')
            price_img4 = pricing.get('nternal_reasoning', 'N/A')
            price_img5 = pricing.get('input_cache_read', 'N/A')
            
            print(f"{mid:<50} | {name:<30} | {price_img3}")

        print("=" * 80)
        print(f"👁️ Vision Модели (анализ изображений): {len(vision_models)} шт.")
        print(f"📝 Текстовые модели: {len(text_models)} шт.")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    get_models()
