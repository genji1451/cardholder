from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('auth/telegram/', views.telegram_auth, name='telegram_auth'),
    path('auth/me/', views.current_user, name='current_user'),
    path('auth/subscription/', views.check_telegram_subscription, name='check_subscription'),
]
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint"""
    return Response({
        'message': 'Spider-Man Cards Collection API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth/telegram/',
            'user': '/api/auth/me/',
            'subscription': '/api/auth/subscription/',
            'cards': '/api/cards/',
            'inventory': '/api/inventory/',
            'wishlist': '/api/wishlist/',
            'analytics': '/api/analytics/',
        }
    })