"""
Утилиты для работы с Telegram Bot API
"""

import requests
from django.conf import settings
from typing import Optional, Dict, Any

def check_telegram_subscription(user_telegram_id: int, channel_id: str) -> Dict[str, Any]:
    """
    Проверяет, подписан ли пользователь на Telegram канал
    
    Args:
        user_telegram_id: ID пользователя в Telegram
        channel_id: ID канала (например, @channel_name или -1001234567890)
    
    Returns:
        Dict с информацией о подписке
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    try:
        # Получаем информацию о пользователе в канале
        url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
        
        params = {
            'chat_id': channel_id,
            'user_id': user_telegram_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok'):
                member_info = data.get('result', {})
                status = member_info.get('status', '')
                
                # Статусы подписчика в Telegram
                subscriber_statuses = ['member', 'administrator', 'creator']
                is_subscribed = status in subscriber_statuses
                
                return {
                    'is_subscribed': is_subscribed,
                    'status': status,
                    'member_info': member_info,
                    'error': None
                }
            else:
                return {
                    'is_subscribed': False,
                    'status': 'unknown',
                    'member_info': None,
                    'error': data.get('description', 'Unknown API error')
                }
        else:
            return {
                'is_subscribed': False,
                'status': 'error',
                'member_info': None,
                'error': f'HTTP {response.status_code}: {response.text}'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'is_subscribed': False,
            'status': 'error',
            'member_info': None,
            'error': f'Request error: {str(e)}'
        }
    except Exception as e:
        return {
            'is_subscribed': False,
            'status': 'error',
            'member_info': None,
            'error': f'Unexpected error: {str(e)}'
        }

def send_telegram_message(user_telegram_id: int, message: str) -> Dict[str, Any]:
    """
    Отправляет сообщение пользователю в Telegram
    
    Args:
        user_telegram_id: ID пользователя в Telegram
        message: Текст сообщения
    
    Returns:
        Dict с результатом отправки
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            'chat_id': user_telegram_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': data.get('ok', False),
                'error': None,
                'message_id': data.get('result', {}).get('message_id') if data.get('ok') else None
            }
        else:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text}',
                'message_id': None
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Request error: {str(e)}',
            'message_id': None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'message_id': None
        }
