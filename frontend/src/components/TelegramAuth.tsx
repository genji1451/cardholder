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

    // Load Telegram script with retry logic
    const loadScript = (attempt = 1) => {
      const script = document.createElement('script');
      // Try different CDN if first attempt fails
      script.src = attempt === 1 
        ? 'https://telegram.org/js/telegram-widget.js?22'
        : `https://telegram.org/js/telegram-widget.js?${Date.now()}`;
      
      script.setAttribute('data-telegram-login', botName);
      script.setAttribute('data-size', 'large');
      script.setAttribute('data-onauth', 'onTelegramAuth(user)');
      script.setAttribute('data-request-access', 'write');
      script.setAttribute('data-userpic', 'false');
      script.async = true;
      script.crossOrigin = 'anonymous';

      script.onload = () => {
        console.log('✅ Telegram script loaded (attempt', attempt, ')');
        setDebugInfo('Скрипт загружен');
        
        // Check if iframe was created
        setTimeout(() => {
          const iframe = document.querySelector('iframe[id^="telegram-login"]');
          console.log('🔍 Checking for iframe:', iframe);
          if (iframe) {
            console.log('✅ Iframe found');
            console.log('Iframe src:', iframe.getAttribute('src'));
            setDebugInfo('Виджет загружен ✅');
          } else {
            console.log('❌ Iframe not found');
            setDebugInfo('Виджет не создан (возможно проблема с доменом в BotFather)');
          }
        }, 1500);
      };

      script.onerror = (e) => {
        console.error('❌ Failed to load Telegram script (attempt', attempt, ')', e);
        console.error('Script URL:', script.src);
        
        if (attempt < 2) {
          console.log('🔄 Retrying with different URL...');
          setDebugInfo(`Повтор загрузки... (попытка ${attempt + 1})`);
          setTimeout(() => loadScript(attempt + 1), 2000);
        } else {
          setDebugInfo('❌ Не удалось загрузить скрипт Telegram');
          setError('Не удалось загрузить Telegram виджет. Возможно telegram.org заблокирован или проблемы с сетью.');
        }
      };
      
      return script;
    };

    const script = loadScript();

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
            <div style={{ 
              marginTop: '0.75rem', 
              padding: '0.75rem',
              background: 'rgba(234, 179, 8, 0.1)',
              border: '1px solid rgba(234, 179, 8, 0.3)',
              borderRadius: '6px',
              fontSize: '0.85rem',
              color: '#fbbf24'
            }}>
              <strong>💡 Решение:</strong> Используйте "Режим разработки" ниже. 
              Он полностью функционален и не требует доступа к telegram.org
            </div>
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
