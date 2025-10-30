import { useState, useRef, useEffect } from 'react';
import './BoosterPackPage.css';

interface BoosterPackPageProps {}

interface Card {
  id: number;
  image: string;
  title: string;
  rarity: 'common' | 'uncommon' | 'rare';
}

const BoosterPackPage = ({}: BoosterPackPageProps) => {
  const [isOpening, setIsOpening] = useState(false);
  const [isOpened, setIsOpened] = useState(false);
  const [isCutting, setIsCutting] = useState(false);
  const [topFlipped, setTopFlipped] = useState(false);
  const [cardStack, setCardStack] = useState<Card[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showCard, setShowCard] = useState(false);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  
  const packRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const topPartRef = useRef<HTMLDivElement>(null);

  // Генерируем случайные карты
  const generateCards = (): Card[] => {
    const cards: Card[] = [];
    const cardCount = 8;
    
    for (let i = 0; i < cardCount; i++) {
      // Случайная редкость
      const rarities: ('common' | 'uncommon' | 'rare')[] = ['common', 'uncommon', 'rare'];
      const rarity = rarities[Math.floor(Math.random() * rarities.length)];
      
      // Случайное изображение
      const imageNum = Math.floor(Math.random() * 276) + 1;
      const image = `/images/spiderman/${imageNum.toString().padStart(3, '0')}.png`;
      
      cards.push({
        id: i,
        image,
        title: `Card #${imageNum}`,
        rarity
      });
    }
    
    return cards;
  };

  const handleOpenPack = () => {
    if (isOpening || isOpened) return;
    
    setIsOpening(true);
    
    // Генерируем карты
    const cards = generateCards();
    setCardStack(cards);
    
    // Этап 1: Разрез (0.5 сек)
    setTimeout(() => {
      setIsCutting(true);
    }, 300);
    
    // Этап 2: Поворот верхней части (0.8 сек)
    setTimeout(() => {
      setTopFlipped(true);
    }, 800);
    
    // Этап 3: Удаление верхней части и показ карт (1.6 сек)
    setTimeout(() => {
      setIsOpening(false);
      setIsCutting(false);
      setTopFlipped(false);
      setIsOpened(true);
      setShowCard(true);
    }, 1600);
  };

  const handleSwipe = (direction: 'left' | 'right') => {
    if (!isOpened || currentCardIndex >= cardStack.length - 1) return;
    
    setShowCard(false);
    
    setTimeout(() => {
      setCurrentCardIndex(currentCardIndex + 1);
      setShowCard(true);
    }, 300);
  };

  const handleReset = () => {
    setIsOpening(false);
    setIsOpened(false);
    setIsCutting(false);
    setTopFlipped(false);
    setCardStack([]);
    setCurrentCardIndex(0);
    setShowCard(false);
    setRotation({ x: 0, y: 0 });
  };

  const handleCardMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current || !showCard) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * 20; // Максимальный наклон 20 градусов
    const rotateY = ((centerX - x) / centerX) * 20;

    setRotation({ x: rotateX, y: rotateY });
  };

  const handleCardMouseLeave = () => {
    setRotation({ x: 0, y: 0 });
  };

  const currentCard = cardStack[currentCardIndex];

  return (
    <div className="booster-pack-container">
      <div className="booster-pack-header">
        <h1>🎴 Booster Pack Opener</h1>
        <p>Откройте пак и посмотрите, какие карты вы получили!</p>
      </div>

      {!isOpened ? (
        <div className="pack-section">
          <div 
            ref={packRef}
            className={`booster-pack ${isOpening ? 'opening' : ''} ${isCutting ? 'cutting' : ''} ${topFlipped ? 'top-flipped' : ''}`}
            onClick={handleOpenPack}
          >
            <div className="pack-wrap">
              <div className="pack-logo-section">
                <div className="pack-logo">🕸️</div>
                <div className="pack-age-rating">6+</div>
              </div>
              <div className="pack-brand-banner">TRADING CARD GAME</div>
              
              <div className="pack-image-section">
                <div className="pack-hero">🕷️</div>
                <div className="pack-background-elements">
                  <div className="cloud cloud-1"></div>
                  <div className="cloud cloud-2"></div>
                  <div className="cloud cloud-3"></div>
                </div>
              </div>
              
              <div className="pack-set-section">
                <div className="pack-set-name">SPIDER-MAN</div>
                <div className="pack-set-subname">WEB OF HEROES</div>
              </div>
              
              <div className="pack-content-info">
                <div className="pack-cards-count">10 ADDITIONAL GAME CARDS</div>
              </div>
            </div>
            
            {isCutting && (
              <div className="cutting-line"></div>
            )}
            
            {topFlipped && (
              <div 
                ref={topPartRef}
                className="pack-top-part-flipped"
              >
                <div className="top-part-content">
                  <div className="pack-logo-section">
                    <div className="pack-logo">🕸️</div>
                    <div className="pack-age-rating">6+</div>
                  </div>
                  <div className="pack-brand-banner">TRADING CARD GAME</div>
                </div>
              </div>
            )}
            
            {isOpening && !topFlipped && (
              <div className="pack-top-part-static">
                <div className="top-part-content">
                  <div className="pack-logo-section">
                    <div className="pack-logo">🕸️</div>
                    <div className="pack-age-rating">6+</div>
                  </div>
                  <div className="pack-brand-banner">TRADING CARD GAME</div>
                </div>
              </div>
            )}
          </div>
          
          {!isOpening && (
            <button className="open-button" onClick={handleOpenPack}>
              ✂️ Открыть пак
            </button>
          )}
        </div>
      ) : (
        <div className="cards-section">
          {showCard && currentCard && (
            <div className="card-3d-wrapper">
              <div 
                ref={cardRef}
                className={`card-container ${showCard ? 'show' : ''}`}
                onMouseMove={handleCardMouseMove}
                onMouseLeave={handleCardMouseLeave}
                onClick={() => handleSwipe('left')}
                style={{
                  transform: `perspective(1500px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale3d(1, 1, 1)`,
                }}
              >
                <div className="card-flip">
                  <div className="card-front-face">
                    <img src={currentCard.image} alt={currentCard.title} />
                  </div>
                </div>
              </div>
              
              <div className="card-shadow"></div>
              
              <div className="card-info">
                <div className={`rarity-badge ${currentCard.rarity}`}>
                  {currentCard.rarity === 'common' ? '🟢 Обычная' : 
                   currentCard.rarity === 'uncommon' ? '🟡 Необычная' : 
                   '🔴 Редкая'}
                </div>
                <h3>{currentCard.title}</h3>
                <div className="card-counter">
                  Карта {currentCardIndex + 1} из {cardStack.length}
                </div>
              </div>
            </div>
          )}
          
          {!showCard && currentCard && (
            <div className="card-3d-wrapper">
              <div className="card-container">
                <div className="card-flip">
                  <div className="card-front-face">
                    <img src={currentCard.image} alt={currentCard.title} />
                  </div>
                </div>
              </div>
              <div className="card-shadow"></div>
            </div>
          )}
          
          <div className="cards-controls">
            {currentCardIndex < cardStack.length - 1 ? (
              <button className="next-button" onClick={() => handleSwipe('left')}>
                👈 Следующая карта
              </button>
            ) : (
              <div className="pack-complete">
                <h2>🎉 Пак открыт!</h2>
                <p>Вы получили {cardStack.length} карт</p>
                <button className="reset-button" onClick={handleReset}>
                  🔄 Открыть новый пак
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="booster-pack-instructions">
        <h3>🎮 Как открыть:</h3>
        <ul>
          <li>✂️ Нажмите "Открыть пак" - упаковка разрежется сверху</li>
          <li>🎴 Появятся карты в стопке</li>
          <li>👆 Нажимайте на карту или "Следующая карта" для листания</li>
          <li>⭐ Откройте все 8 карт из пака!</li>
        </ul>
      </div>
    </div>
  );
};

export default BoosterPackPage;

