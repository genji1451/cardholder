import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TelegramAuth from '../components/TelegramAuth';
import TelegramAuthDev from '../components/TelegramAuthDev';
import apiClient from '../api/client';
import './AuthPage.css';

const AuthPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useDevMode, setUseDevMode] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleTelegramAuth = async (telegramUser: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post('/auth/telegram/', telegramUser);
      const { access, refresh } = response.data;
      
      // Save tokens and load user data
      await login(access, refresh);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Telegram auth error:', error);
      setError(error.response?.data?.error || 'Ошибка авторизации');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-logo">
          <h1>🕷️ Collection Portfolio</h1>
          <p>Управляй своими коллекциями карточек</p>
        </div>

        <div className="auth-content">
          {!useDevMode ? (
            <TelegramAuth 
              onAuth={handleTelegramAuth}
              botName="cardloginbot" // Имя бота из Telegram
            />
          ) : (
            <TelegramAuthDev onAuth={handleTelegramAuth} />
          )}
          
          <div className="auth-mode-toggle">
            <button 
              onClick={() => setUseDevMode(!useDevMode)}
              className="toggle-button"
            >
              {useDevMode ? '🔄 Переключиться на Telegram' : '🔧 Режим разработки'}
            </button>
          </div>
          
          {isLoading && (
            <div className="auth-loading">
              <div className="loading-spinner"></div>
              <p>Входим в систему...</p>
            </div>
          )}
          
          {error && (
            <div className="auth-error">
              <p>❌ {error}</p>
              <button 
                onClick={() => setError(null)}
                className="retry-button"
              >
                Попробовать снова
              </button>
            </div>
          )}
        </div>

        <div className="auth-features">
          <h3>Возможности для авторизованных пользователей:</h3>
          <ul>
            <li>📊 Детальная аналитика коллекции</li>
            <li>💼 Управление портфолио</li>
            <li>💝 Список желаний</li>
            <li>🔗 Поделиться коллекцией</li>
            <li>🛍️ Доступ к магазину</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
