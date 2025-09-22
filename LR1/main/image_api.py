"""
Утилиты для работы с API изображений
"""
import requests
import random
from typing import Optional


def get_image_from_unsplash(query: str = "technology", width: int = 800, height: int = 600) -> Optional[str]:
    """
    Получает URL изображения из Unsplash API
    
    Args:
        query: поисковый запрос для изображения
        width: ширина изображения
        height: высота изображения
    
    Returns:
        URL изображения или None при ошибке
    """
    try:
        # Используем Unsplash Source API (не требует ключа для базового использования)
        url = f"https://source.unsplash.com/{width}x{height}/?{query}"
        
        # Проверяем доступность изображения
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            return url
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении изображения из Unsplash: {e}")
        return None


def get_image_from_picsum(width: int = 800, height: int = 600) -> Optional[str]:
    """
    Получает случайное изображение из Lorem Picsum API
    
    Args:
        width: ширина изображения
        height: высота изображения
    
    Returns:
        URL изображения или None при ошибке
    """
    try:
        # Lorem Picsum API для случайных изображений
        image_id = random.randint(1, 1000)
        url = f"https://picsum.photos/{width}/{height}?random={image_id}"
        
        # Проверяем доступность изображения
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            return url
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении изображения из Picsum: {e}")
        return None


def get_placeholder_image(width: int = 800, height: int = 600, text: str = "News") -> str:
    """
    Получает placeholder изображение с текстом
    
    Args:
        width: ширина изображения
        height: высота изображения
        text: текст для отображения на изображении
    
    Returns:
        URL placeholder изображения
    """
    # Используем via.placeholder.com для создания placeholder изображений
    return f"https://via.placeholder.com/{width}x{height}/0066CC/FFFFFF?text={text}"


def get_news_image(category: str = "technology", fallback: bool = True) -> Optional[str]:
    """
    Получает изображение для новости, пытаясь использовать разные источники
    
    Args:
        category: категория для поиска изображения
        fallback: использовать ли fallback изображения при неудаче
    
    Returns:
        URL изображения или None
    """
    # Словарь категорий для поиска в Unsplash
    category_keywords = {
        'technology': 'technology,computer,smartphone',
        'repair': 'repair,electronics,tools',
        'service': 'service,support,customer',
        'news': 'business,office,news',
        'mobile': 'smartphone,mobile,phone',
        'computer': 'computer,laptop,pc'
    }
    
    search_query = category_keywords.get(category, category)
    
    # Пытаемся получить изображение из Unsplash
    image_url = get_image_from_unsplash(search_query)
    if image_url:
        return image_url
    
    # Если Unsplash не сработал, пытаемся Picsum
    image_url = get_image_from_picsum()
    if image_url:
        return image_url
    
    # Если все не сработало и включен fallback, возвращаем placeholder
    if fallback:
        return get_placeholder_image(text="News")
    
    return None


def get_predefined_news_images() -> list:
    """
    Возвращает список предопределенных URL изображений для новостей
    """
    return [
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1556761175-4b46a572b786?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&h=600&fit=crop",
        "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=600&fit=crop",
        "https://source.unsplash.com/800x600/?technology",
        "https://source.unsplash.com/800x600/?electronics",
        "https://source.unsplash.com/800x600/?repair",
        "https://source.unsplash.com/800x600/?service",
        "https://source.unsplash.com/800x600/?mobile"
    ]
