import React, { useState } from 'react';
import './TelegramAuthDev.css';

interface TelegramAuthDevProps {
  onAuth: (user: any) => void;
}

const TelegramAuthDev: React.FC<TelegramAuthDevProps> = ({ onAuth }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [telegramId, setTelegramId] = useState('');
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');

  const handleDevAuth = async () => {
    if (!telegramId || !firstName) {
      setError('Заполните обязательные поля');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Создаем тестовые данные Telegram пользователя
      const telegramUser = {
        id: parseInt(telegramId),
        first_name: firstName,
        last_name: username || '',
        username: username || '',
        photo_url: '',
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'dev_hash_' + Date.now() // Для разработки
      };

      onAuth(telegramUser);
    } catch (error: any) {
      console.error('Dev auth error:', error);
      setError(error.message || 'Ошибка авторизации');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="telegram-auth-dev">
      <div className="auth-header">
        <h2>🔧 Режим разработки</h2>
        <p>Используйте тестовые данные для авторизации</p>
      </div>
      
      <div className="auth-form">
        <div className="form-group">
          <label htmlFor="telegramId">Telegram ID *</label>
          <input
            type="number"
            id="telegramId"
            value={telegramId}
            onChange={(e) => setTelegramId(e.target.value)}
            placeholder="123456789"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="firstName">Имя *</label>
          <input
            type="text"
            id="firstName"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="Иван"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="ivan_dev"
          />
        </div>
        
        <button 
          onClick={handleDevAuth}
          disabled={isLoading || !telegramId || !firstName}
          className="auth-button"
        >
          {isLoading ? '🔄 Авторизация...' : '🚀 Войти'}
        </button>
        
        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
          </div>
        )}
      </div>
      
      <div className="auth-footer">
        <p className="dev-note">
          ⚠️ Это режим разработки. В продакшене будет использоваться настоящий Telegram Login Widget
        </p>
      </div>
    </div>
  );
};

export default TelegramAuthDev;
