import { useState, useRef, useEffect } from 'react';
import './Card3DTestPage.css';

interface Card3DTestPageProps {}

const Card3DTestPage = ({}: Card3DTestPageProps) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

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
    setRotation({ x: 0, y: 0 });
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
            transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${isFlipped ? rotation.y + 180 : rotation.y}deg)`,
          }}
        >
          <div className="card3d-test-face card3d-test-front">
            <img 
              src="/images/spiderman/001.png" 
              alt="Card Front"
              className="card3d-test-full-image"
            />
          </div>

          <div className="card3d-test-face card3d-test-back">
            <img 
              src="/images/spiderman/back-card.png" 
              alt="Card Back"
              className="card3d-test-full-image"
              onError={(e) => {
                // Если изображение не найдено, используем placeholder
                e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect fill="%23667eea" width="400" height="600"/%3E%3Ctext x="50%25" y="50%25" font-size="60" fill="white" text-anchor="middle" dominant-baseline="middle"%3E🕸️%3C/text%3E%3C/svg%3E';
              }}
            />
          </div>
        </div>
      </div>

      <div className="card3d-test-instructions">
        <h3>🎮 Инструкции:</h3>
        <ul>
          <li>✨ Наведите мышь на карточку - она будет наклоняться в 3D</li>
          <li>🔄 Нажмите на карточку - она перевернется обратной стороной</li>
          <li>🎨 Кликните еще раз - карточка вернется в исходное положение</li>
          <li>⚡ 3D эффект работает на обеих сторонах карточки!</li>
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

