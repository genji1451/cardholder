import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../api/client';
import './SubscriptionChecker.css';

interface SubscriptionStatus {
  is_subscribed: boolean;
  has_premium: boolean;
  status?: string;
  api_error?: string;
}

const SubscriptionChecker: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkSubscription = async () => {
    if (!isAuthenticated || !user?.profile.telegram_id) return;

    setIsChecking(true);
    setError(null);

    try {
      const response = await apiClient.post('/auth/subscription/');
      setSubscriptionStatus(response.data);
    } catch (error: any) {
      console.error('Error checking subscription:', error);
      setError(error.response?.data?.error || 'Ошибка проверки подписки');
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && user?.profile.telegram_id) {
      checkSubscription();
    }
  }, [isAuthenticated, user]);

  if (!isAuthenticated) {
    return null;
  }

  if (!user?.profile.telegram_id) {
    return (
      <div className="subscription-notice">
        <div className="notice-content">
          <h3>🔗 Подключите Telegram</h3>
          <p>Для доступа к премиум функциям подключите свой Telegram аккаунт</p>
        </div>
      </div>
    );
  }

  return (
    <div className="subscription-checker">
      <div className="subscription-header">
        <h3>📺 Статус подписки</h3>
        <button 
          onClick={checkSubscription}
          disabled={isChecking}
          className="check-button"
        >
          {isChecking ? '🔄' : '🔄'} Проверить
        </button>
      </div>

      {error && (
        <div className="subscription-error">
          <p>❌ {error}</p>
        </div>
      )}

      {subscriptionStatus && (
        <div className="subscription-status">
          <div className={`status-indicator ${subscriptionStatus.is_subscribed ? 'subscribed' : 'not-subscribed'}`}>
            {subscriptionStatus.is_subscribed ? '✅' : '❌'}
          </div>
          
          <div className="status-info">
            <div className="status-text">
              {subscriptionStatus.is_subscribed ? 'Подписан' : 'Не подписан'}
            </div>
            <div className="status-details">
              {subscriptionStatus.has_premium ? '⭐ Premium доступ' : '🔒 Ограниченный доступ'}
            </div>
            {subscriptionStatus.status && (
              <div className="status-api">
                Статус: {subscriptionStatus.status}
              </div>
            )}
          </div>
        </div>
      )}

      {subscriptionStatus && !subscriptionStatus.is_subscribed && (
        <div className="subscription-actions">
          <p>Для получения полного доступа подпишитесь на наш Telegram канал:</p>
          <a 
            href="https://t.me/your_channel" 
            target="_blank" 
            rel="noopener noreferrer"
            className="subscribe-button"
          >
            📱 Подписаться на канал
          </a>
        </div>
      )}
    </div>
  );
};

export default SubscriptionChecker;
