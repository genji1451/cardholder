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

  useEffect(() => {
    // Set up global callback for Telegram
    window.onTelegramAuth = (user: TelegramUser) => {
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

    const container = document.getElementById('telegram-login-container');
    if (container) {
      container.innerHTML = ''; // Clear previous content
      container.appendChild(script);
    }

    return () => {
      // Cleanup
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
      </div>
    </div>
  );
};

export default TelegramAuth;
