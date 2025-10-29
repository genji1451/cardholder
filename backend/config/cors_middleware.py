"""
Кастомный CORS middleware для добавления заголовков даже при ошибках
"""
from django.utils.deprecation import MiddlewareMixin


class CorsMiddleware(MiddlewareMixin):
    """Middleware для добавления CORS заголовков ко всем ответам"""
    
    def process_response(self, request, response):
        # Добавляем CORS заголовки ко всем ответам
        origin = request.META.get('HTTP_ORIGIN')
        
        # Разрешаем все источники
        if origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = '*'
        
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        
        return response
