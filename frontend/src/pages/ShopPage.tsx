import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import Footer from '../components/Footer';
import './ShopPage.css';

interface ProductOptions {
  hasCase?: boolean;
  filmType?: 'none' | 'holographic' | 'metallic';
}

interface Product {
  id: number;
  title: string;
  description: string;
  price: number;
  category: 'original' | 'meme' | 'art' | 'design';
  isLimited?: boolean;
  limitedInfo?: string;
  stock?: number;
  totalStock?: number;
  image: string;
  available: boolean;
  inDevelopment?: boolean;
  options?: ProductOptions;
}

// Данные товаров
const mockProducts: Product[] = [
  // Мемная серия
  {
    id: 1,
    title: "Карточный картель #001",
    description: "Первая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ПРОДАНО",
    stock: 0,
    totalStock: 1,
    image: '/images/spiderman/001.png',
    available: false,
  },
  {
    id: 2,
    title: "Самозванцы #002",
    description: "Вторая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ПРОДАНО",
    stock: 0,
    totalStock: 1,
    image: '/images/spiderman/002.png',
    available: false,
  },
  {
    id: 3,
    title: "Спуди #003",
    description: "Третья карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/003.png',
    available: true,
  },
  {
    id: 4,
    title: "Женщина-невидимка #004",
    description: "Четвертая карта мемной серии. Лимитированный тираж.",
    price: 300,
    category: 'meme',
    isLimited: true,
    limitedInfo: "ПРОДАНО",
    stock: 0,
    totalStock: 1,
    image: '/images/spiderman/004.png',
    available: false,
  },
  {
    id: 5,
    title: "Пачка кириешек#005",
    description: "Пятая карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/005.png',
    available: true,
  },
  {
    id: 6,
    title: "Стая собак #006",
    description: "Шестая карта мемной серии. Обычный тираж.",
    price: 300,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/006.png',
    available: true,
  },
  {
    id: 7,
    title: "Собаки лают-караван прет #007",
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
  // Картины
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
    image: '/images/spiderman/spot.jpeg',
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
    image: '/images/spiderman/daily.png',
    available: true,
  },
  // Дизайнерские карточки
  {
    id: 201,
    title: "Персональная карточка",
    description: "Закажите уникальную карточку с вашим собственным дизайном! Отправьте нам свою идею, и мы воплотим её в жизнь.",
    price: 500,
    category: 'design',
    image: '/images/spiderman/personal.png',
    available: true,
  },
];

const ShopPage = () => {
  const { addToCart, getTotalItems } = useCart();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'original' | 'meme' | 'art' | 'design'>('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [hasCase, setHasCase] = useState(false);
  const [filmType, setFilmType] = useState<'none' | 'holographic' | 'metallic'>('none');

  const filteredProducts = mockProducts.filter(product => {
    return selectedCategory === 'all' || product.category === selectedCategory;
  });

  const calculatePrice = (product: Product) => {
    let totalPrice = product.price;
    if (hasCase) totalPrice += 300;
    if (filmType === 'holographic') totalPrice += 100;
    if (filmType === 'metallic') totalPrice += 100;
    return totalPrice;
  };

  const openProductModal = (product: Product) => {
    if (!product.available) return;
    setSelectedProduct(product);
    setHasCase(false);
    setFilmType('none');
  };

  const closeProductModal = () => {
    setSelectedProduct(null);
    setHasCase(false);
    setFilmType('none');
  };

  const handleAddToCart = () => {
    if (!selectedProduct) return;
    
    const productWithOptions = {
      ...selectedProduct,
      price: calculatePrice(selectedProduct),
      options: {
        hasCase,
        filmType
      }
    };
    
    addToCart(productWithOptions);
    
    // Показываем уведомление
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.textContent = `✓ "${selectedProduct.title}" добавлен в корзину`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2000);
    
    closeProductModal();
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
          <h1>CGC Shop</h1>
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
              🎨 Картины
            </button>
            <button
              className={selectedCategory === 'design' ? 'active' : ''}
              onClick={() => setSelectedCategory('design')}
            >
              ✨ Дизайнерские карточки
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
                {selectedCategory === 'art' && '🎨 Картины'}
                {selectedCategory === 'design' && '✨ Дизайнерские карточки'}
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
                  <div 
                    key={product.id} 
                    className={`product-card ${(!product.available || product.inDevelopment) ? 'unavailable' : ''}`}
                  >
                    <div className="product-image">
                      <img src={product.image} alt={product.title} />
                      {product.isLimited && product.limitedInfo && (
                        <div className={`limited-badge ${product.stock === 0 ? 'sold-out' : product.inDevelopment ? 'in-dev' : 'available'}`}>
                          ⭐ {product.limitedInfo}
                        </div>
                      )}
                      {/* Темный overlay для проданных карт */}
                      {((!product.available && !product.inDevelopment) || (product.isLimited && product.stock === 0)) && (
                        <div className="sold-overlay">ПРОДАНО</div>
                      )}
                      {/* Темный overlay для карт в разработке */}
                      {product.inDevelopment && (
                        <div className="dev-overlay">В РАЗРАБОТКЕ</div>
                      )}
                    </div>
                    
                    <div className="product-content">
                      <h3 className="product-title">{product.title}</h3>
                      <p className="product-description">{product.description}</p>
                      
                      <div className="product-footer">
                        <div className="product-price">от ₽{product.price.toLocaleString()}</div>
                        <button
                          className="buy-button"
                          onClick={() => openProductModal(product)}
                          disabled={!product.available}
                        >
                          {product.inDevelopment ? '🚧 В разработке' : product.available ? '👁️ Подробнее' : '❌ Продано'}
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

        </div>
      </section>

      {/* Product Modal */}
      {selectedProduct && (
        <div className="modal-overlay" onClick={closeProductModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeProductModal}>✕</button>
            
            <div className="modal-body">
              <div className="modal-image">
                <img src={selectedProduct.image} alt={selectedProduct.title} />
                {selectedProduct.isLimited && selectedProduct.limitedInfo && (
                  <div className={`limited-badge ${selectedProduct.stock === 0 ? 'sold-out' : 'available'}`}>
                    ⭐ {selectedProduct.limitedInfo}
                  </div>
                )}
              </div>
              
              <div className="modal-info">
                <h2>{selectedProduct.title}</h2>
                <p className="modal-description">{selectedProduct.description}</p>
                
                {/* Options for Meme cards */}
                {selectedProduct.category === 'meme' && (
                  <div className="options-section">
                    <h3>Выберите вариант:</h3>
                    
                    <div className="option-group">
                      <label className="option-label">
                        <input
                          type="checkbox"
                          checked={hasCase}
                          onChange={(e) => setHasCase(e.target.checked)}
                        />
                        <span className="option-text">
                          В кейсе <span className="option-price">+300₽</span>
                        </span>
                      </label>
                    </div>
                  </div>
                )}
                
                {/* Options for Design cards */}
                {selectedProduct.category === 'design' && (
                  <div className="options-section">
                    <h3>Выберите опции:</h3>
                    
                    <div className="option-group">
                      <label className="option-label">
                        <input
                          type="checkbox"
                          checked={hasCase}
                          onChange={(e) => setHasCase(e.target.checked)}
                        />
                        <span className="option-text">
                          В кейсе <span className="option-price">+300₽</span>
                        </span>
                      </label>
                    </div>
                    
                    <div className="option-group">
                      <h4>Тип пленки:</h4>
                      <label className="option-label">
                        <input
                          type="radio"
                          name="filmType"
                          checked={filmType === 'none'}
                          onChange={() => setFilmType('none')}
                        />
                        <span className="option-text">Без пленки</span>
                      </label>
                      
                      <label className="option-label">
                        <input
                          type="radio"
                          name="filmType"
                          checked={filmType === 'holographic'}
                          onChange={() => setFilmType('holographic')}
                        />
                        <span className="option-text">
                          Голографическая <span className="option-price">+100₽</span>
                        </span>
                      </label>
                      
                      <label className="option-label">
                        <input
                          type="radio"
                          name="filmType"
                          checked={filmType === 'metallic'}
                          onChange={() => setFilmType('metallic')}
                        />
                        <span className="option-text">
                          Металлическая <span className="option-price">+100₽</span>
                        </span>
                      </label>
                    </div>
                  </div>
                )}
                
                <div className="modal-footer">
                  <div className="total-price">
                    <span>Итого:</span>
                    <span className="price-value">₽{calculatePrice(selectedProduct).toLocaleString()}</span>
                  </div>
                  <button className="add-to-cart-btn" onClick={handleAddToCart}>
                    🛒 Добавить в корзину
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default ShopPage;

