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
  const [cardStack, setCardStack] = useState<Card[]>([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showCard, setShowCard] = useState(false);
  
  const packRef = useRef<HTMLDivElement>(null);

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
    
    // Анимация разрезания упаковки
    setTimeout(() => {
      setIsOpening(false);
      setIsOpened(true);
      setShowCard(true);
    }, 2000);
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
    setCardStack([]);
    setCurrentCardIndex(0);
    setShowCard(false);
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
            className={`booster-pack ${isOpening ? 'opening' : ''}`}
            onClick={handleOpenPack}
          >
            <div className="pack-wrap">
              <div className="pack-label">🕸️ SPIDER-MAN</div>
              <div className="pack-subtitle">BOOSTER PACK</div>
            </div>
            
            {isOpening && (
              <>
                <div className="cutting-line"></div>
                <div className="pack-top-part"></div>
              </>
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
            <div 
              className={`card-container ${showCard ? 'show' : ''}`}
              onClick={() => handleSwipe('left')}
            >
              <div className="card-flip">
                <div className="card-front-face">
                  <img src={currentCard.image} alt={currentCard.title} />
                </div>
              </div>
              
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
            <div className="card-container">
              <div className="card-flip">
                <div className="card-front-face">
                  <img src={currentCard.image} alt={currentCard.title} />
                </div>
              </div>
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

