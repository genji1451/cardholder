import React, { useEffect, useState } from 'react';
import './TelegramAuth.css';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

interface TelegramAuthProps {
  onAuth: (user: TelegramUser) => void;
  botName: string;
}

declare global {
  interface Window {
    onTelegramAuth: (user: TelegramUser) => void;
  }
}

const TelegramAuth: React.FC<TelegramAuthProps> = ({ onAuth, botName }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('Инициализация...');

  useEffect(() => {
    console.log('🔵 TelegramAuth: Component mounted');
    console.log('🔵 Bot name:', botName);
    
    // Set up global callback for Telegram
    window.onTelegramAuth = (user: TelegramUser) => {
      console.log('🟢 Telegram auth callback called', user);
      setIsLoading(true);
      setError(null);
      onAuth(user);
    };

    // Load Telegram script
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-userpic', 'false');
    script.async = true;

    script.onload = () => {
      console.log('✅ Telegram script loaded');
      setDebugInfo('Скрипт загружен');
      
      // Check if iframe was created
      setTimeout(() => {
        const iframe = document.querySelector('iframe[id^="telegram-login"]');
        console.log('🔍 Checking for iframe:', iframe);
        if (iframe) {
          console.log('✅ Iframe found');
          setDebugInfo('Виджет загружен');
        } else {
          console.log('❌ Iframe not found');
          setDebugInfo('Виджет не создан');
        }
      }, 1000);
    };

    script.onerror = (e) => {
      console.error('❌ Failed to load Telegram script', e);
      setDebugInfo('Ошибка загрузки скрипта');
      setError('Не удалось загрузить Telegram виджет');
    };

    const container = document.getElementById('telegram-login-container');
    console.log('🔍 Container found:', !!container);
    
    if (container) {
      container.innerHTML = ''; // Clear previous content
      container.appendChild(script);
      console.log('✅ Script appended to container');
      setDebugInfo('Загрузка виджета...');
    } else {
      console.error('❌ Container not found!');
      setDebugInfo('Контейнер не найден');
    }

    return () => {
      // Cleanup
      console.log('🔴 TelegramAuth: Cleanup');
      if (container) {
        container.innerHTML = '';
      }
      (window as any).onTelegramAuth = undefined;
    };
  }, [botName, onAuth]);

  return (
    <div className="telegram-auth">
      <div className="auth-header">
        <h2>Войти через Telegram</h2>
        <p>Используйте свой Telegram аккаунт для входа в приложение</p>
      </div>
      
      <div className="auth-content">
        <div id="telegram-login-container" className="telegram-widget-container"></div>
        
        {/* Debug info */}
        <div style={{ 
          marginTop: '1rem', 
          padding: '0.5rem', 
          background: 'rgba(59, 130, 246, 0.1)', 
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: '#60a5fa'
        }}>
          🔧 Debug: {debugInfo}
        </div>
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Авторизация...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}
      </div>
      
      <div className="auth-footer">
        <p className="privacy-note">
          🔒 Мы используем только базовую информацию из вашего Telegram профиля
        </p>
        <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
          Bot: @{botName}
        </p>
      </div>
    </div>
  );
};

export default TelegramAuth;
