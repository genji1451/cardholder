import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import './ShopPageTest.css';

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

// Данные товаров (копия для автономной работы тестовой страницы)
const mockProducts: Product[] = [
  {
    id: 999,
    title: "🧪 ТЕСТОВЫЙ ТОВАР",
    description: "Тестовый товар для проверки оплаты и бесплатной доставки",
    price: 50,
    category: 'meme',
    isLimited: false,
    image: '/images/spiderman/001.png',
    available: true,
  },
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
    title: "Пачка кириешек #005",
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
    title: "Собаки лают #007",
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

const ShopPageTest = () => {
  const { addToCart, getTotalItems } = useCart();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'original' | 'meme' | 'art' | 'design'>('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [hoveredProduct, setHoveredProduct] = useState<number | null>(null);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const filteredProducts = mockProducts.filter(product => {
    return selectedCategory === 'all' || product.category === selectedCategory;
  });

  const handleAddToCart = (product: Product) => {
    addToCart(product);
    // Simple notification logic could be added here
    const btn = document.getElementById(`btn-${product.id}`);
    if (btn) {
      const originalText = btn.innerText;
      btn.innerText = "ADDED ✓";
      setTimeout(() => {
        btn.innerText = originalText;
      }, 1000);
    }
    setSelectedProduct(null);
  };

  return (
    <div className="shop-test-page">
      <div className="shop-container">
        {/* Navigation */}
        <nav className="shop-header">
          <div>
            <span className="shop-subtitle">Exclusive Collection // 2025</span>
            <h1 className="shop-title">Spider<br/>Shop</h1>
          </div>
          <div className="test-nav">
             <Link to="/" className="nav-link">Home</Link>
             <Link to="/cart" className="nav-link">
                Cart [{getTotalItems()}]
             </Link>
          </div>
        </nav>

        {/* Filters */}
        <div className="shop-filters">
          {['all', 'original', 'meme', 'art', 'design'].map((cat) => (
            <button
              key={cat}
              className={`filter-btn ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat as any)}
            >
              {cat === 'all' ? 'ALL ITEMS' : cat.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Grid */}
        <div className="products-grid-test">
          {filteredProducts.map((product, index) => (
            <div 
              key={product.id} 
              className="product-card-test"
              style={{ '--i': index } as React.CSSProperties}
              onMouseEnter={() => setHoveredProduct(product.id)}
              onMouseLeave={() => setHoveredProduct(null)}
              onClick={() => {
                if (product.available || product.inDevelopment) {
                    setSelectedProduct(product);
                }
              }}
            >
              {/* Badges */}
              {product.stock === 0 && product.isLimited && (
                <div className="status-badge sold">SOLD OUT</div>
              )}
              {product.isLimited && product.stock !== 0 && (
                <div className="status-badge limited">LIMITED</div>
              )}
              {product.inDevelopment && (
                <div className="status-badge limited">DEV</div>
              )}

              <div className="card-image-container">
                <img src={product.image} alt={product.title} loading="lazy" />
              </div>
              
              <div className="card-info">
                <span className="card-category">{product.category}</span>
                <h3 className="card-title">{product.title}</h3>
                
                <div className="card-price-row">
                   <span className="card-price">₽{product.price}</span>
                   <button 
                     id={`btn-${product.id}`}
                     className="glitch-btn"
                     disabled={!product.available}
                     onClick={(e) => {
                       e.stopPropagation();
                       if (product.available) handleAddToCart(product);
                     }}
                   >
                     {product.available ? 'ADD +' : 'N/A'}
                   </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredProducts.length === 0 && (
          <div style={{ padding: '4rem', textAlign: 'center', color: '#666', textTransform: 'uppercase', letterSpacing: '2px' }}>
            No artifacts found in this sector.
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedProduct && (
        <div className="test-modal-overlay" onClick={() => setSelectedProduct(null)}>
          <div className="test-modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setSelectedProduct(null)}>✕</button>
            
            <div className="modal-left">
              <img src={selectedProduct.image} alt={selectedProduct.title} />
            </div>
            
            <div className="modal-right">
              <span className="card-category" style={{fontSize: '1rem', marginBottom: '1rem'}}>
                {selectedProduct.category} // ID: {selectedProduct.id}
              </span>
              
              <h2 className="modal-title-test">{selectedProduct.title}</h2>
              
              <div className="modal-price-test">
                ₽{selectedProduct.price}
              </div>

              <p className="modal-desc-test">
                {selectedProduct.description}
                {selectedProduct.isLimited && (
                   <div style={{marginTop: '1rem', color: 'var(--sp-accent-yellow)'}}>
                     ⚠ LIMITED EDITION: {selectedProduct.limitedInfo}
                   </div>
                )}
              </p>

              {selectedProduct.available ? (
                  <button 
                    className="modal-add-btn"
                    onClick={() => handleAddToCart(selectedProduct)}
                  >
                    Add to Collection
                  </button>
              ) : (
                  <button className="modal-add-btn" disabled style={{opacity: 0.5, cursor: 'not-allowed'}}>
                    {selectedProduct.inDevelopment ? 'Coming Soon' : 'Sold Out'}
                  </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShopPageTest;

