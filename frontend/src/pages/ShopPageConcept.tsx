import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import './ShopPageConcept.css';

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

// Reusing mock data for consistency
const mockProducts: Product[] = [
  {
    id: 999,
    title: "🧪 ТЕСТОВЫЙ ТОВАР",
    description: "Тестовый товар для проверки оплаты",
    price: 50,
    category: 'meme',
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
    description: "Вторая карта мемной серии.",
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
    description: "Третья карта мемной серии.",
    price: 300,
    category: 'meme',
    available: true,
    image: '/images/spiderman/003.png',
  },
  {
    id: 101,
    title: "Пятно",
    description: "Авторская картина 'Пятно'. Холст, акрил.",
    price: 3000,
    category: 'art',
    isLimited: true,
    limitedInfo: "2/5",
    stock: 2,
    totalStock: 5,
    image: '/images/spiderman/spot.jpeg',
    available: true,
  },
  {
    id: 201,
    title: "Design Card Custom",
    description: "Unique commission work.",
    price: 500,
    category: 'design',
    image: '/images/spiderman/personal.png',
    available: true,
  },
];

const ShopPageConcept = () => {
  const { addToCart } = useCart();
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'original' | 'meme' | 'art' | 'design'>('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  
  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const filteredProducts = mockProducts.filter(product => {
    return selectedCategory === 'all' || product.category === selectedCategory;
  });

  const handleProductClick = (product: Product) => {
    if (!product.available && !product.inDevelopment) return;
    setSelectedProduct(product);
  };

  return (
    <div className="shop-concept-page">
      {/* Navbar placeholder */}
      <nav style={{ position: 'fixed', top: 0, width: '100%', padding: '2rem', zIndex: 50, display: 'flex', justifyContent: 'space-between', mixBlendMode: 'difference' }}>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', fontFamily: 'var(--font-display)', fontSize: '1.5rem' }}>
          PC_SHOP_V2
        </Link>
        <Link to="/cart" style={{ color: 'white', textDecoration: 'none', fontFamily: 'var(--font-mono)' }}>
          CART [0]
        </Link>
      </nav>

      {/* Hero */}
      <header className="concept-hero">
        <div className="hero-circle"></div>
        <div className="hero-glitch-container">
          <h1 className="hero-title" data-text="COLLECTION">COLLECTION</h1>
          <div className="hero-subtitle">WEB 3.0 // SPIDER-VERSE // ART</div>
        </div>
      </header>

      {/* Filters */}
      <section className="concept-filters">
        <span className="filter-label">Select Frequency</span>
        <div className="filter-buttons-concept">
          {['all', 'original', 'meme', 'art', 'design'].map((cat) => (
            <button
              key={cat}
              className={`filter-btn-concept ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat as any)}
            >
              {cat.toUpperCase()}
            </button>
          ))}
        </div>
      </section>

      {/* Grid */}
      <section className="concept-grid-section">
        <div className="concept-grid">
          {filteredProducts.map((product, i) => (
            <div 
              key={product.id} 
              className="concept-card"
              style={{ '--i': i } as React.CSSProperties}
              onClick={() => handleProductClick(product)}
            >
              <div className="card-image-wrapper">
                <img src={product.image} alt={product.title} loading="lazy" />
                <div className="card-overlay"></div>
                <div className="card-badges">
                   {product.isLimited && <span className="concept-badge">LIMITED</span>}
                   {!product.available && <span className="concept-badge sold">SOLD</span>}
                </div>
              </div>
              
              <div className="card-info">
                <h3 className="card-title">{product.title}</h3>
                <span className="card-price">₽{product.price}</span>
              </div>
              <div className="card-meta">
                <span>{product.category.toUpperCase()}</span>
                <span>#{String(product.id).padStart(3, '0')}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Product Modal */}
      {selectedProduct && (
        <div className="concept-modal-overlay" onClick={() => setSelectedProduct(null)}>
          <div className="concept-modal" onClick={e => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setSelectedProduct(null)}>×</button>
            
            <div className="modal-img-col">
              <img src={selectedProduct.image} alt={selectedProduct.title} />
            </div>
            
            <div className="modal-info-col">
              <div>
                <div className="text-mono" style={{ color: 'var(--c-accent-secondary)', marginBottom: '1rem' }}>
                  ITEM #{String(selectedProduct.id).padStart(3, '0')}
                </div>
                <h2 className="modal-title">{selectedProduct.title}</h2>
              </div>
              
              <p className="modal-desc">{selectedProduct.description}</p>
              
              <div className="modal-price">₽{selectedProduct.price}</div>
              
              <div className="modal-actions">
                <button 
                  className="btn-glitch"
                  onClick={() => {
                    addToCart(selectedProduct);
                    setSelectedProduct(null);
                  }}
                >
                  ADD TO CART
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShopPageConcept;

