import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import TelegramAuth from '../components/TelegramAuth';
import TelegramAuthDev from '../components/TelegramAuthDev';
import EmailAuth from '../components/EmailAuth';
import apiClient from '../api/client';
import './AuthPage.css';

const AuthPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [authMethod, setAuthMethod] = useState<'telegram' | 'email' | 'dev'>('email');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleTelegramAuth = async (telegramUser: any) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

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

  const handleEmailAuth = async (authData: any) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      let response;
      
      if (authData.mode === 'register') {
        // Registration
        response = await apiClient.post('/auth/register/', {
          username: authData.username,
          email: authData.email,
          password: authData.password,
          password2: authData.password2,
          first_name: authData.first_name,
          last_name: authData.last_name,
        });
        setSuccessMessage(response.data.message || 'Регистрация прошла успешно!');
      } else {
        // Login
        response = await apiClient.post('/auth/login/', {
          login: authData.login,
          password: authData.password,
        });
        setSuccessMessage(response.data.message || 'Вход выполнен успешно!');
      }

      const { access, refresh } = response.data;
      
      // Save tokens and load user data
      await login(access, refresh);
      
      // Show success message briefly before redirect
      setTimeout(() => {
        navigate('/dashboard');
      }, 500);
      
    } catch (error: any) {
      console.error('Email auth error:', error);
      const errorData = error.response?.data;
      
      // Handle validation errors
      if (errorData?.details) {
        const errorMessages = Object.entries(errorData.details)
          .map(([field, messages]: [string, any]) => {
            if (Array.isArray(messages)) {
              return messages.join(', ');
            }
            return messages;
          })
          .join('. ');
        setError(errorMessages);
      } else {
        setError(errorData?.message || errorData?.error || 'Ошибка авторизации');
      }
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
          {/* Auth method selector */}
          <div className="auth-method-selector">
            <button
              className={`method-button ${authMethod === 'email' ? 'active' : ''}`}
              onClick={() => setAuthMethod('email')}
              disabled={isLoading}
            >
              📧 Email/Логин
            </button>
            <button
              className={`method-button ${authMethod === 'telegram' ? 'active' : ''}`}
              onClick={() => setAuthMethod('telegram')}
              disabled={isLoading}
            >
              ✈️ Telegram
            </button>
            <button
              className={`method-button ${authMethod === 'dev' ? 'active' : ''}`}
              onClick={() => setAuthMethod('dev')}
              disabled={isLoading}
            >
              🔧 Dev Mode
            </button>
          </div>

          {/* Auth components based on selected method */}
          <div className="auth-method-content">
            {authMethod === 'email' && (
              <EmailAuth 
                onAuth={handleEmailAuth}
                isLoading={isLoading}
              />
            )}
            
            {authMethod === 'telegram' && (
              <TelegramAuth 
                onAuth={handleTelegramAuth}
                botName="cardloginbot"
              />
            )}
            
            {authMethod === 'dev' && (
              <TelegramAuthDev onAuth={handleTelegramAuth} />
            )}
          </div>
          
          {isLoading && (
            <div className="auth-loading">
              <div className="loading-spinner"></div>
              <p>Входим в систему...</p>
            </div>
          )}
          
          {successMessage && (
            <div className="auth-success">
              <p>✅ {successMessage}</p>
            </div>
          )}
          
          {error && (
            <div className="auth-error">
              <p>❌ {error}</p>
              <button 
                onClick={() => setError(null)}
                className="retry-button"
              >
                Закрыть
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
