import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="homepage">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-container">
          <div className="hero-badge">COLLECTION MANAGER</div>
          <h1 className="hero-title">
            Управляй своими <br />
            <span className="highlight">коллекциями карточек</span>
          </h1>
          <p className="hero-subtitle">
            Профессиональная платформа для коллекционеров. 
            Отслеживай прогресс, анализируй инвестиции и управляй своей коллекцией.
          </p>
          <div className="hero-actions">
            <Link to="/shop" className="cta-button primary">
              🛍️ Магазин
            </Link>
            <Link to="/auth" className="cta-button secondary">
              🚀 Начать работу
            </Link>
            <Link to="/dashboard" className="cta-button tertiary">
              👀 Посмотреть демо
            </Link>
          </div>
        </div>
      </div>

      {/* Collections Section */}
      <div className="collections-section">
        <div className="collections-container">
          <h2 className="section-heading">Доступные коллекции</h2>
          
          <div className="collections-grid">
            {/* Spider-Man Collection */}
            <Link to="/dashboard" className="collection-card spiderman">
              <div className="card-header">
                <span className="card-icon">🕷️</span>
                <div className="status-badge ready">
                  <span className="badge-dot"></span>
                  Доступно
                </div>
              </div>
              
              <h3 className="card-title">Человек-Паук</h3>
              <p className="card-subtitle">Герои и Злодеи</p>
              
              <p className="card-description">
                Коллекция карточек с героями и злодеями вселенной Человека-Паука
              </p>
              
              <div className="card-footer">
                <span className="card-cta">Открыть коллекцию</span>
                <span className="card-arrow">→</span>
              </div>
              
              <div className="card-gradient"></div>
            </Link>

            {/* Shop Collection */}
            <Link to="/shop" className="collection-card shop">
              <div className="card-header">
                <span className="card-icon">🛍️</span>
                <div className="status-badge ready">
                  <span className="badge-dot"></span>
                  Доступно
                </div>
              </div>
              
              <h3 className="card-title">Магазин</h3>
              <p className="card-subtitle">Карты и Картины</p>
              
              <p className="card-description">
                Покупайте редкие карточки и авторские картины Spider-Man
              </p>
              
              <div className="card-footer">
                <span className="card-cta">Открыть магазин</span>
                <span className="card-arrow">→</span>
              </div>
              
              <div className="card-gradient"></div>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="features-container">
          <h2 className="section-heading">Возможности платформы</h2>
          
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <h3>Аналитика</h3>
              <p>Детальная статистика и прогресс по коллекциям</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">💼</div>
              <h3>Портфолио</h3>
              <p>Управление и оценка стоимости коллекции</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">📚</div>
              <h3>Каталог</h3>
              <p>Полный каталог всех доступных карточек</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">💝</div>
              <h3>Wishlist</h3>
              <p>Список желаемых карточек для покупки</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="homepage-footer">
        <p>© 2025 Collection Portfolio. Создано для коллекционеров.</p>
      </footer>
    </div>
  );
};

export default HomePage;

