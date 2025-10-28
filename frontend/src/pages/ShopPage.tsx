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
  category: 'original' | 'meme' | 'art';
  isLimited?: boolean;
  limitedInfo?: string;
  stock?: number;
  totalStock?: number;
  image: string;
  available: boolean;
  inDevelopment?: boolean;
}

// Данные товаров
const mockProducts: Product[] = [
  // Мемная серия
  {
    id: 1,
    title: "Мемная карта #001",
    description: "Первая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ПРОДАНО",
    stock: 0,
    totalStock: 1,
    image: '/images/spiderman/card_1_1.svg',
    available: false,
  },
  {
    id: 2,
    title: "Мемная карта #002",
    description: "Вторая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ПРОДАНО",
    stock: 0,
    totalStock: 1,
    image: '/images/spiderman/card_1_2.svg',
    available: false,
  },
  {
    id: 3,
    title: "Мемная карта #003",
    description: "Третья карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/card_1_3.svg',
    available: true,
  },
  {
    id: 4,
    title: "Мемная карта #004",
    description: "Четвертая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ОСТАЛОСЬ 1 ШТ.",
    stock: 1,
    totalStock: 1,
    image: '/images/spiderman/card_2_1.svg',
    available: true,
  },
  {
    id: 5,
    title: "Мемная карта #005",
    description: "Пятая карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/card_2_2.svg',
    available: true,
  },
  {
    id: 6,
    title: "Мемная карта #006",
    description: "Шестая карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/card_2_3.svg',
    available: true,
  },
  {
    id: 7,
    title: "Мемная карта #007",
    description: "Седьмая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "В РАЗРАБОТКЕ",
    image: '/images/spiderman/card_3_1.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 8,
    title: "Мемная карта #008",
    description: "Восьмая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_3_2.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 9,
    title: "Мемная карта #009",
    description: "Девятая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_3_3.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 10,
    title: "Мемная карта #010",
    description: "Десятая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_1_1.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 11,
    title: "Мемная карта #011",
    description: "Одиннадцатая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_1_2.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 12,
    title: "Мемная карта #012",
    description: "Двенадцатая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_1_3.svg',
    available: false,
    inDevelopment: true,
  },
  {
    id: 13,
    title: "Мемная карта #013",
    description: "Тринадцатая карта мемной серии.",
    price: 300,
    category: 'meme',
    image: '/images/spiderman/card_2_1.svg',
    available: false,
    inDevelopment: true,
  },
  // Дизайнерские карты (Картины)
  {
    id: 101,
    title: "Пятно",
    description: "Авторская картина 'Пятно'. Холст, акрил. Лимитированный тираж.",
    price: 3000,
    category: 'art',
    isLimited: true,
    limitedInfo: "ОСТАЛОСЬ 2 из 5",
    stock: 2,
    totalStock: 5,
    image: '/images/spiderman/card_3_1.svg',
    available: true,
  },
  {
    id: 102,
    title: "Дейли Багл",
    description: "Авторская картина 'Дейли Багл'. Холст, акрил. Лимитированный тираж.",
    price: 4500,
    category: 'art',
    isLimited: true,
    limitedInfo: "ОСТАЛОСЬ 2 из 5",
    stock: 2,
    totalStock: 5,
    image: '/images/spiderman/card_3_2.svg',
    available: true,
  },
];

const ShopPage = () => {
  const { addToCart, getTotalItems } = useCart();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'original' | 'meme' | 'art'>('all');

  const filteredProducts = mockProducts.filter(product => {
    return selectedCategory === 'all' || product.category === selectedCategory;
  });


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
              className={selectedCategory === 'original' ? 'active' : ''}
              onClick={() => setSelectedCategory('original')}
            >
              ⭐ Оригинальная серия
            </button>
            <button
              className={selectedCategory === 'meme' ? 'active' : ''}
              onClick={() => setSelectedCategory('meme')}
            >
              😄 Мемная серия
            </button>
            <button
              className={selectedCategory === 'art' ? 'active' : ''}
              onClick={() => setSelectedCategory('art')}
            >
              🎨 Дизайнерские карты
            </button>
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="products-section">
        {selectedCategory === 'original' ? (
          <div className="in-development-message">
            <div className="dev-icon">🚧</div>
            <h2>Оригинальная серия</h2>
            <p>Раздел находится в разработке</p>
            <p className="dev-subtitle">Скоро здесь появятся эксклюзивные карты!</p>
          </div>
        ) : (
          <>
            <div className="products-header">
              <h2>
                {selectedCategory === 'all' && '🌐 Все товары'}
                {selectedCategory === 'meme' && '😄 Мемная серия'}
                {selectedCategory === 'art' && '🎨 Дизайнерские карты'}
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
                      {product.isLimited && product.limitedInfo && (
                        <div className={`limited-badge ${product.stock === 0 ? 'sold-out' : product.inDevelopment ? 'in-dev' : 'available'}`}>
                          ⭐ {product.limitedInfo}
                        </div>
                      )}
                      {!product.available && !product.isLimited && (
                        <div className="sold-overlay">ПРОДАНО</div>
                      )}
                      {product.inDevelopment && !product.isLimited && (
                        <div className="dev-overlay">В РАЗРАБОТКЕ</div>
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
                          {product.inDevelopment ? '🚧 В разработке' : product.available ? '🛒 В корзину' : '❌ Продано'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
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
            href="https://t.me/rex_testudo" 
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

