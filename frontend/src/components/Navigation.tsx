import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const navItems = [
    { path: '/', label: 'Главная', icon: '🏠' },
    { path: '/dashboard', label: 'Дашборд', icon: '📊' },
    { path: '/portfolio', label: 'Портфолио', icon: '💼' },
    { path: '/catalog', label: 'Каталог', icon: '📚' },
    { path: '/inventory', label: 'Инвентарь', icon: '📦' },
    { path: '/wishlist', label: 'Список желаний', icon: '💝' },
    { path: '/analytics', label: 'Аналитика', icon: '📈' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h1>🕷️ Человек-Паук Герои и Злодеи</h1>
      </div>
      
      <ul className="nav-menu">
        {navItems.map((item) => (
          <li key={item.path} className="nav-item">
            <Link
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>

      {isAuthenticated && user && (
        <div className="nav-user">
          <div className="user-info">
            <div className="user-avatar">
              {user.profile.telegram_photo_url ? (
                <img 
                  src={user.profile.telegram_photo_url} 
                  alt={user.profile.telegram_first_name || user.username}
                  className="avatar-image"
                />
              ) : (
                <span className="avatar-placeholder">
                  {user.profile.telegram_first_name?.[0] || user.username[0]?.toUpperCase()}
                </span>
              )}
            </div>
            <div className="user-details">
              <span className="user-name">
                {user.profile.telegram_first_name || user.username}
              </span>
              {user.profile.has_premium_access && (
                <span className="premium-badge">⭐ Premium</span>
              )}
            </div>
          </div>
          <button 
            onClick={logout}
            className="logout-button"
            title="Выйти"
          >
            🚪
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
