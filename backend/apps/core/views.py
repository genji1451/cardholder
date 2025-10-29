import hashlib
import hmac
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import TelegramAuthSerializer, UserSerializer, RegisterSerializer, LoginSerializer


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
    try:
        serializer = TelegramAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
            
            # Check if username already exists and make it unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                first_name=auth_data.get('first_name', ''),
                last_name=auth_data.get('last_name', '')
            )
            
            # Get or create profile (signal should create it, but let's be safe)
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
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
        
    except Exception as e:
        # Return detailed error for debugging
        import traceback
        return Response({
            'error': 'Server error',
            'details': str(e),
            'traceback': traceback.format_exc(),
            'message': 'Произошла ошибка на сервере. Попробуйте позже или обратитесь к администратору.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register new user with email and password
    """
    try:
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'message': 'Регистрация прошла успешно'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        return Response({
            'error': 'Registration failed',
            'details': str(e),
            'traceback': traceback.format_exc(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user with email/username and password
    """
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        login_input = serializer.validated_data['login']
        password = serializer.validated_data['password']
        
        # Try to find user by email or username
        user = None
        if '@' in login_input:
            # Looks like email
            try:
                user = User.objects.get(email=login_input)
            except User.DoesNotExist:
                pass
        
        if user is None:
            # Try username
            try:
                user = User.objects.get(username=login_input)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid credentials',
                    'message': 'Неверный email/логин или пароль'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate
        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user is None:
            return Response({
                'error': 'Invalid credentials',
                'message': 'Неверный email/логин или пароль'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(authenticated_user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(authenticated_user).data,
            'message': 'Вход выполнен успешно'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        return Response({
            'error': 'Login failed',
            'details': str(e),
            'traceback': traceback.format_exc(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    # Simplified API root - no database initialization
    
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
            'payment': '/api/payment/',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    try:
        from apps.cards.models import Card
        card_count = Card.objects.count()
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'cards_count': card_count,
            'timestamp': str(timezone.now())
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(timezone.now())
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def init_database(request):
    """Initialize database with sample data"""
    try:
        from apps.cards.models import Card, Series
        from decimal import Decimal
        
        # Create series if not exists
        series, created = Series.objects.get_or_create(
            number=1,
            defaults={
                'title': 'Spider-Man Collection'
            }
        )
        
        # Create sample cards
        sample_cards = [
            {
                'number': 1,
                'title': 'Человек-Паук',
                'rarity': 'o',
                'base_price_rub': Decimal('52.50'),
                'notes': 'Основной герой комиксов Marvel',
                'series': series
            },
            {
                'number': 2,
                'title': 'Железный Человек',
                'rarity': 'o',
                'base_price_rub': Decimal('55.00'),
                'notes': 'Гений, миллиардер, филантроп',
                'series': series
            },
            {
                'number': 3,
                'title': 'Веном',
                'rarity': 'ск',
                'base_price_rub': Decimal('92.50'),
                'notes': 'Симбиот и бывший хост Эдди Брок',
                'series': series
            }
        ]
        
        created_count = 0
        for card_data in sample_cards:
            card, created = Card.objects.get_or_create(
                number=card_data['number'],
                series=series,
                defaults=card_data
            )
            if created:
                created_count += 1
        
        total_cards = Card.objects.count()
        return Response({
            'status': 'success',
            'message': f'База данных инициализирована',
            'cards_created': created_count,
            'total_cards': total_cards,
            'timestamp': str(timezone.now())
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': str(timezone.now())
        }, status=500)    


@api_view(['POST'])
@permission_classes([AllowAny])
def run_migrations(request):
    """Run Django migrations"""
    try:
        import subprocess
        import os
        
        # Run migrations
        result = subprocess.run(
            ['python', 'manage.py', 'migrate', '--noinput'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        
        if result.returncode == 0:
            return Response({
                'status': 'success',
                'message': 'Миграции выполнены успешно',
                'output': result.stdout,
                'timestamp': str(timezone.now())
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Ошибка выполнения миграций',
                'error': result.stderr,
                'timestamp': str(timezone.now())
            }, status=500)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': str(timezone.now())
        }, status=500)