import { useState, useRef, useEffect } from 'react';
import './Card3DTestPage.css';

interface Card3DTestPageProps {}

const Card3DTestPage = ({}: Card3DTestPageProps) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current || isFlipped) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * 15; // Максимальный наклон 15 градусов
    const rotateY = ((centerX - x) / centerX) * 15;

    setRotation({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    if (!isFlipped) {
      setRotation({ x: 0, y: 0 });
    }
  };

  const handleCardClick = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="card3d-test-container">
      <div className="card3d-test-header">
        <h1>🎴 3D Карточка - Тестовый режим</h1>
        <p>Наведите мышь на карточку, чтобы увидеть 3D эффект</p>
        <p>Нажмите на карточку, чтобы перевернуть</p>
      </div>

      <div className="card3d-test-wrapper">
        <div
          ref={cardRef}
          className={`card3d-test-card ${isFlipped ? 'flipped' : ''}`}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleCardClick}
          style={{
            transform: `perspective(1000px) rotateX(${isFlipped ? 0 : rotation.x}deg) rotateY(${isFlipped ? 0 : rotation.y}deg) ${
              isFlipped ? 'rotateY(180deg)' : ''
            }`,
          }}
        >
          <div className="card3d-test-face card3d-test-front">
            <div className="card3d-test-image-wrapper">
              <img 
                src="/images/spiderman/001.png" 
                alt="Card Front"
                className="card3d-test-image"
              />
            </div>
            <div className="card3d-test-info">
              <h2>Карточный картель #001</h2>
              <p>Первая карта мемной серии</p>
              <div className="card3d-test-price">300₽</div>
              <div className="card3d-test-hint">Нажмите, чтобы перевернуть 👆</div>
            </div>
          </div>

          <div className="card3d-test-face card3d-test-back">
            <div className="card3d-test-back-content">
              <h2>🕸️ Spider-Man Cards</h2>
              <div className="card3d-test-back-info">
                <div className="card3d-test-back-section">
                  <strong>Серия:</strong> Мемная
                </div>
                <div className="card3d-test-back-section">
                  <strong>Номер:</strong> 001
                </div>
                <div className="card3d-test-back-section">
                  <strong>Дата выпуска:</strong> 2024
                </div>
                <div className="card3d-test-back-stats">
                  <div className="stat-item">
                    <span className="stat-label">Редкость</span>
                    <span className="stat-value">⭐⭐⭐</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Тираж</span>
                    <span className="stat-value">1 шт</span>
                  </div>
                </div>
              </div>
              <div className="card3d-test-back-qr">
                <div className="qr-placeholder">📱 QR CODE</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card3d-test-instructions">
        <h3>🎮 Инструкции:</h3>
        <ul>
          <li>✨ Наведите мышь на карточку - она будет наклоняться</li>
          <li>🔄 Нажмите на карточку - она перевернется обратной стороной</li>
          <li>🎨 Кликните еще раз - карточка вернется в исходное положение</li>
          <li>⚡ Эффект 3D работает только для лицевой стороны</li>
        </ul>
      </div>

      <div className="card3d-test-controls">
        <button onClick={() => setIsFlipped(!isFlipped)} className="test-button">
          {isFlipped ? '🔄 Показать лицевую сторону' : '🔄 Перевернуть карточку'}
        </button>
        <button onClick={() => setRotation({ x: 0, y: 0 })} className="test-button">
          🎯 Сбросить наклон
        </button>
      </div>
    </div>
  );
};

export default Card3DTestPage;

