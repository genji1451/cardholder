import { useState, useEffect } from 'react';
import './CookieConsent.css';

const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Проверяем, дал ли пользователь согласие ранее
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      // Показываем баннер через 1 секунду после загрузки
      setTimeout(() => setIsVisible(true), 1000);
    }
  }, []);

  const acceptCookies = () => {
    localStorage.setItem('cookieConsent', 'accepted');
    setIsVisible(false);
  };

  const declineCookies = () => {
    localStorage.setItem('cookieConsent', 'declined');
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="cookie-consent">
      <div className="cookie-content">
        <div className="cookie-icon">🍪</div>
        <div className="cookie-text">
          <h3>Мы используем файлы cookie</h3>
          <p>
            Этот сайт использует файлы cookie для улучшения работы и анализа трафика. 
            Продолжая использовать сайт, вы соглашаетесь с нашей{' '}
            <a href="/legal/privacy" target="_blank" rel="noopener noreferrer">
              политикой конфиденциальности
            </a>
            .
          </p>
        </div>
        <div className="cookie-actions">
          <button 
            className="cookie-btn decline" 
            onClick={declineCookies}
          >
            Отклонить
          </button>
          <button 
            className="cookie-btn accept" 
            onClick={acceptCookies}
          >
            Принять
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
