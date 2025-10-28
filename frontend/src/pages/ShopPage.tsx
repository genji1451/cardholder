import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import Footer from '../components/Footer';
import './ShopPage.css';

interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  category: 'card' | 'art';
  rarity?: 'common' | 'rare' | 'ultra';
  image: string;
  available: boolean;
  featured?: boolean;
}

// Моковые данные для примера
const mockProducts: Product[] = [
  // Карточки
  {
    id: 1,
    title: "Spider-Man Classic",
    description: "Редкая карточка Человека-Паука в классическом костюме. Состояние: отличное.",
    price: 2500,
    category: 'card',
    rarity: 'ultra',
    image: '/images/spiderman/card_1_1.svg',
    available: true,
    featured: true,
  },
  {
    id: 2,
    title: "Green Goblin",
    description: "Карточка злодея Зеленого Гоблина. Лимитированная серия.",
    price: 1800,
    category: 'card',
    rarity: 'rare',
    image: '/images/spiderman/card_1_2.svg',
    available: true,
  },
  {
    id: 3,
    title: "Venom Symbiote",
    description: "Эксклюзивная карточка Венома. Редкость: ультра.",
    price: 3200,
    category: 'card',
    rarity: 'ultra',
    image: '/images/spiderman/card_1_3.svg',
    available: true,
    featured: true,
  },
  {
    id: 4,
    title: "Mary Jane Watson",
    description: "Карточка персонажа MJ. Обычная редкость.",
    price: 800,
    category: 'card',
    rarity: 'common',
    image: '/images/spiderman/card_2_1.svg',
    available: true,
  },
  // Картины
  {
    id: 5,
    title: "Spider-Verse Artwork",
    description: "Авторская картина 'Вселенная Пауков'. Холст, акрил. 50x70 см.",
    price: 12000,
    category: 'art',
    image: '/images/spiderman/card_3_1.svg',
    available: true,
    featured: true,
  },
  {
    id: 6,
    title: "Web Slinger Portrait",
    description: "Портрет Паутинного героя. Цифровая печать на холсте. 40x60 см.",
    price: 8500,
    category: 'art',
    image: '/images/spiderman/card_3_2.svg',
    available: true,
  },
  {
    id: 7,
    title: "NYC Skyline with Spider-Man",
    description: "Панорама Нью-Йорка с силуэтом Человека-Паука. 60x90 см.",
    price: 15000,
    category: 'art',
    image: '/images/spiderman/card_3_3.svg',
    available: false,
  },
];

const ShopPage = () => {
  const { addToCart, getTotalItems } = useCart();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'card' | 'art'>('all');
  const [selectedRarity, setSelectedRarity] = useState<'all' | 'common' | 'rare' | 'ultra'>('all');

  const filteredProducts = mockProducts.filter(product => {
    const categoryMatch = selectedCategory === 'all' || product.category === selectedCategory;
    const rarityMatch = selectedRarity === 'all' || product.rarity === selectedRarity;
    return categoryMatch && rarityMatch;
  });

  const featuredProducts = mockProducts.filter(p => p.featured);

  const getRarityLabel = (rarity?: string) => {
    switch (rarity) {
      case 'common': return '🟢 Обычная';
      case 'rare': return '🟡 Редкая';
      case 'ultra': return '🔴 Ультра';
      default: return '';
    }
  };

  const handleAddToCart = (product: Product) => {
    if (!product.available) return;
    addToCart(product);
    
    // Показываем уведомление
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.textContent = `✓ "${product.title}" добавлен в корзину`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  };

  return (
    <div className="shop-page">
      {/* Simple Navigation */}
      <nav className="shop-nav">
        <Link to="/" className="shop-nav-logo">
          🕷️ Portfolio Cards
        </Link>
        <div className="shop-nav-links">
          <Link to="/cart" className="shop-nav-link cart-link">
            🛒 Корзина
            {getTotalItems() > 0 && (
              <span className="cart-badge">{getTotalItems()}</span>
            )}
          </Link>
          <Link to="/" className="shop-nav-link">🏠 Главная</Link>
          <Link to="/auth" className="shop-nav-link">🚀 Войти</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="shop-hero">
        <div className="hero-content">
          <div className="shop-logo">🛍️</div>
          <h1>Магазин коллекционера</h1>
          <p>Редкие карточки и авторские картины Spider-Man</p>
        </div>
        <div className="hero-spider-web"></div>
      </div>

      {/* Featured Products */}
      {featuredProducts.length > 0 && (
        <section className="featured-section">
          <h2>⭐ Рекомендуемые</h2>
          <div className="featured-grid">
            {featuredProducts.map(product => (
              <div key={product.id} className="featured-card">
                <div className="featured-badge">FEATURED</div>
                <div className="product-image">
                  <img src={product.image} alt={product.title} />
                  {!product.available && <div className="sold-overlay">ПРОДАНО</div>}
                </div>
                <div className="product-info">
                  <h3>{product.title}</h3>
                  <div className="product-price">₽{product.price.toLocaleString()}</div>
                  {product.rarity && (
                    <div className="product-rarity">{getRarityLabel(product.rarity)}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Filters */}
      <section className="filters-section">
        <div className="filter-group">
          <label>Категория:</label>
          <div className="filter-buttons">
            <button
              className={selectedCategory === 'all' ? 'active' : ''}
              onClick={() => setSelectedCategory('all')}
            >
              🌐 Все
            </button>
            <button
              className={selectedCategory === 'card' ? 'active' : ''}
              onClick={() => setSelectedCategory('card')}
            >
              🎴 Карточки
            </button>
            <button
              className={selectedCategory === 'art' ? 'active' : ''}
              onClick={() => setSelectedCategory('art')}
            >
              🎨 Картины
            </button>
          </div>
        </div>

        {selectedCategory === 'card' && (
          <div className="filter-group">
            <label>Редкость:</label>
            <div className="filter-buttons">
              <button
                className={selectedRarity === 'all' ? 'active' : ''}
                onClick={() => setSelectedRarity('all')}
              >
                Все
              </button>
              <button
                className={selectedRarity === 'common' ? 'active' : ''}
                onClick={() => setSelectedRarity('common')}
              >
                🟢 Обычная
              </button>
              <button
                className={selectedRarity === 'rare' ? 'active' : ''}
                onClick={() => setSelectedRarity('rare')}
              >
                🟡 Редкая
              </button>
              <button
                className={selectedRarity === 'ultra' ? 'active' : ''}
                onClick={() => setSelectedRarity('ultra')}
              >
                🔴 Ультра
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Products Grid */}
      <section className="products-section">
        <div className="products-header">
          <h2>
            {selectedCategory === 'all' && '🌐 Все товары'}
            {selectedCategory === 'card' && '🎴 Карточки'}
            {selectedCategory === 'art' && '🎨 Картины'}
          </h2>
          <div className="products-count">
            Найдено: {filteredProducts.length}
          </div>
        </div>

        {filteredProducts.length === 0 ? (
          <div className="no-products">
            <div className="no-products-icon">🔍</div>
            <h3>Товары не найдены</h3>
            <p>Попробуйте изменить фильтры</p>
          </div>
        ) : (
          <div className="products-grid">
            {filteredProducts.map(product => (
              <div key={product.id} className="product-card">
                <div className="product-image">
                  <img src={product.image} alt={product.title} />
                  {!product.available && <div className="sold-overlay">ПРОДАНО</div>}
                  {product.category === 'card' && product.rarity && (
                    <div className={`rarity-badge ${product.rarity}`}>
                      {getRarityLabel(product.rarity)}
                    </div>
                  )}
                </div>
                
                <div className="product-content">
                  <h3 className="product-title">{product.title}</h3>
                  <p className="product-description">{product.description}</p>
                  
                  <div className="product-footer">
                    <div className="product-price">₽{product.price.toLocaleString()}</div>
                    <button
                      className="buy-button"
                      onClick={() => handleAddToCart(product)}
                      disabled={!product.available}
                    >
                      {product.available ? '🛒 В корзину' : '❌ Продано'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Contact Section */}
      <section className="contact-section">
        <div className="contact-card">
          <h2>💬 Свяжитесь со мной</h2>
          <p>
            Хотите приобрести карточку или картину? Есть вопросы?<br />
            Напишите мне в Telegram!
          </p>
          <a 
            href="https://t.me/your_username" 
            target="_blank" 
            rel="noopener noreferrer"
            className="telegram-button"
          >
            ✈️ Написать в Telegram
          </a>
          <div className="payment-info">
            <p className="payment-note">
              💳 Принимаю: Перевод на карту, СБП, OZON Pay
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default ShopPage;

