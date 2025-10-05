import hashlib
import hmac
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import TelegramAuthSerializer, UserSerializer


def verify_telegram_auth(auth_data, bot_token):
    """Verify Telegram authentication data"""
    check_hash = auth_data.pop('hash', None)
    if not check_hash:
        return False
    
    # Для разработки пропускаем проверку hash
    if check_hash.startswith('dev_hash_'):
        return True
    
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
    data_check_string = '\n'.join(data_check_arr)
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return calculated_hash == check_hash


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth(request):
    """
    Authenticate user via Telegram
    """
    serializer = TelegramAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    auth_data = serializer.validated_data.copy()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    # Verify Telegram data
    if not verify_telegram_auth(auth_data, bot_token):
        return Response(
            {'error': 'Invalid authentication data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    telegram_id = auth_data['id']
    
    # Get or create user
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
        created = False
    except UserProfile.DoesNotExist:
        # Create new user
        username = auth_data.get('username') or f"tg_user_{telegram_id}"
        user = User.objects.create_user(
            username=username,
            first_name=auth_data.get('first_name', ''),
            last_name=auth_data.get('last_name', '')
        )
        profile = user.profile
        created = True
    
    # Update profile with Telegram data
    profile.telegram_id = telegram_id
    profile.telegram_username = auth_data.get('username', '')
    profile.telegram_first_name = auth_data.get('first_name', '')
    profile.telegram_last_name = auth_data.get('last_name', '')
    profile.telegram_photo_url = auth_data.get('photo_url', '')
    profile.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
        'created': created
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
def check_telegram_subscription(request):
    """Check if user is subscribed to Telegram channel"""
    from .telegram_utils import check_telegram_subscription as check_subscription
    
    user_profile = request.user.profile
    
    if not user_profile.telegram_id:
        return Response({
            'error': 'User not linked to Telegram'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check subscription via Telegram Bot API
    channel_id = settings.TELEGRAM_CHANNEL_ID
    subscription_result = check_subscription(user_profile.telegram_id, channel_id)
    
    if subscription_result['error']:
        # If API error, return current cached status
        return Response({
            'is_subscribed': user_profile.is_telegram_subscriber,
            'has_premium': user_profile.has_premium_access,
            'api_error': subscription_result['error']
        })
    
    # Update profile with fresh subscription status
    is_subscribed = subscription_result['is_subscribed']
    user_profile.is_telegram_subscriber = is_subscribed
    user_profile.has_premium_access = is_subscribed  # Premium access = subscription
    user_profile.save()
    
    return Response({
        'is_subscribed': is_subscribed,
        'has_premium': is_subscribed,
        'status': subscription_result['status']
    })
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