import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import './App.css';
import apiClient from './api/client';

// Contexts
import { AuthProvider } from './contexts/AuthContext';

// Components
import Navigation from './components/Navigation';
import SimplePortfolio from './components/SimplePortfolio';
import CatalogGrid from './components/Catalog/CatalogGrid';
import InventoryGrid from './components/Inventory/InventoryGrid';
import AnalyticsPage from './pages/AnalyticsPage';
import WishlistPage from './pages/WishlistPage';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import ProtectedRoute from './components/ProtectedRoute';

// Enhanced Dashboard with real data and interactivity
const Dashboard = () => {
  console.log('Dashboard component rendering...');
  
  const { isLoading: overviewLoading, error: overviewError } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      console.log('Fetching analytics...');
      const response = await apiClient.get('/analytics/overview/');
      console.log('Analytics response:', response.data);
      return response.data;
    },
  });

  const { data: cardsData, isLoading: cardsLoading } = useQuery({
    queryKey: ['cards'],
    queryFn: async () => {
      console.log('Fetching cards...');
      const response = await apiClient.get('/cards/');
      console.log('Cards response:', response.data);
      return response.data.results || response.data;
    },
  });

  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      console.log('Fetching inventory...');
      const response = await apiClient.get('/inventory/items/');
      console.log('Inventory response:', response.data);
      return response.data.results || response.data;
    },
  });

  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: async () => {
      console.log('Fetching wishlist...');
      const response = await apiClient.get('/wishlist/items/');
      console.log('Wishlist response:', response.data);
      return response.data.results || response.data;
    },
  });

  const isLoading = overviewLoading || cardsLoading || inventoryLoading;

  // Calculate enhanced statistics
  const stats = {
    totalCards: cardsData?.length || 0,
    ownedCards: inventoryData?.filter((item: any) => item.has_card).length || 0,
    missingCards: 0,
    completionPercentage: 0,
    totalValue: 0,
    wishlistCount: wishlistData?.length || 0,
    recentAdditions: [],
    topRarity: { common: 0, uncommon: 0, rare: 0 },
    seriesProgress: { part1: 0, part2: 0, part3: 0 }
  };

  if (cardsData && inventoryData) {
    stats.missingCards = stats.totalCards - stats.ownedCards;
    stats.completionPercentage = stats.totalCards > 0 ? (stats.ownedCards / stats.totalCards) * 100 : 0;
    
    // Calculate total value
    const ownedItems = inventoryData.filter((item: any) => item.has_card);
    stats.totalValue = ownedItems.reduce((sum: number, item: any) => {
      const price = parseFloat(item.card?.base_price_rub || 0);
      const quantity = item.quantity || 0;
      return sum + (price * quantity);
    }, 0);

    // Calculate rarity distribution
    ownedItems.forEach((item: any) => {
      const rarity = item.card?.rarity;
      if (rarity === 'o') stats.topRarity.common++;
      else if (rarity === 'ск') stats.topRarity.uncommon++;
      else if (rarity === 'ук') stats.topRarity.rare++;
    });

    // Calculate series progress
    const part1Cards = cardsData.filter((card: any) => card.number >= 1 && card.number <= 275);
    const part2Cards = cardsData.filter((card: any) => card.number >= 276 && card.number <= 550);
    const part3Cards = cardsData.filter((card: any) => card.number >= 551 && card.number <= 825);

    stats.seriesProgress.part1 = part1Cards.filter((card: any) => 
      ownedItems.some((item: any) => item.card?.id === card.id)
    ).length;
    stats.seriesProgress.part2 = part2Cards.filter((card: any) => 
      ownedItems.some((item: any) => item.card?.id === card.id)
    ).length;
    stats.seriesProgress.part3 = part3Cards.filter((card: any) => 
      ownedItems.some((item: any) => item.card?.id === card.id)
    ).length;

    // Get recent additions (last 5 items)
    stats.recentAdditions = ownedItems
      .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
  }

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="loading">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕸️</div>
          <p>Загружаем вашу коллекцию...</p>
        </div>
      </div>
    );
  }

  if (overviewError) {
    return (
      <div className="dashboard-page">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️</div>
          <h2>Ошибка загрузки данных коллекции!</h2>
          <p>{overviewError.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      {/* Hero Section */}
      <div className="dashboard-hero">
        <div className="hero-content">
          <div className="spider-logo">🕷️</div>
          <div>
            <h1>Коллекция карточек Человек-Паук</h1>
            <p>Герои и Злодеи ждут вашего открытия!</p>
          </div>
        </div>
        <div className="hero-stats">
          <div className="hero-stat">
            <div className="hero-stat-value">{stats.totalCards}</div>
            <div className="hero-stat-label">Всего карточек</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">{stats.ownedCards}</div>
            <div className="hero-stat-label">В коллекции</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">{stats.completionPercentage.toFixed(1)}%</div>
            <div className="hero-stat-label">Завершено</div>
          </div>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Общая статистика</div>
            <div className="stat-value">{stats.totalCards}</div>
            <div className="stat-sublabel">Всего карточек</div>
          </div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">В коллекции</div>
            <div className="stat-value">{stats.ownedCards}</div>
            <div className="stat-sublabel">из {stats.totalCards}</div>
          </div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <div className="stat-label">Отсутствуют</div>
            <div className="stat-value">{stats.missingCards}</div>
            <div className="stat-sublabel">нужно найти</div>
          </div>
        </div>
        
        <div className="stat-card info">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-label">Общая стоимость</div>
            <div className="stat-value">₽{stats.totalValue.toFixed(2)}</div>
            <div className="stat-sublabel">инвестировано</div>
          </div>
        </div>
        
        <div className="stat-card secondary">
          <div className="stat-icon">💝</div>
          <div className="stat-content">
            <div className="stat-label">Список желаний</div>
            <div className="stat-value">{stats.wishlistCount}</div>
            <div className="stat-sublabel">карточек</div>
          </div>
        </div>
      </div>

      {/* Series Progress */}
      <div className="series-progress-section">
        <h2>Прогресс по сериям</h2>
        <div className="series-progress-grid">
          <div className="series-card">
            <div className="series-header">
              <h3>Часть 1 (1-275)</h3>
              <span className="series-count">{stats.seriesProgress.part1}/275</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(stats.seriesProgress.part1 / 275) * 100}%` }}
              />
            </div>
            <div className="series-percentage">
              {((stats.seriesProgress.part1 / 275) * 100).toFixed(1)}%
            </div>
          </div>
          
          <div className="series-card">
            <div className="series-header">
              <h3>Часть 2 (276-550)</h3>
              <span className="series-count">{stats.seriesProgress.part2}/275</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(stats.seriesProgress.part2 / 275) * 100}%` }}
              />
            </div>
            <div className="series-percentage">
              {((stats.seriesProgress.part2 / 275) * 100).toFixed(1)}%
            </div>
          </div>
          
          <div className="series-card">
            <div className="series-header">
              <h3>Часть 3 (551-825)</h3>
              <span className="series-count">{stats.seriesProgress.part3}/275</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(stats.seriesProgress.part3 / 275) * 100}%` }}
              />
            </div>
            <div className="series-percentage">
              {((stats.seriesProgress.part3 / 275) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Rarity Distribution */}
      <div className="rarity-section">
        <h2>Распределение по редкости</h2>
        <div className="rarity-grid">
          <div className="rarity-card common">
            <div className="rarity-icon">🟢</div>
            <div className="rarity-content">
              <div className="rarity-name">Обычные</div>
              <div className="rarity-count">{stats.topRarity.common}</div>
            </div>
          </div>
          
          <div className="rarity-card uncommon">
            <div className="rarity-icon">🟡</div>
            <div className="rarity-content">
              <div className="rarity-name">Необычные</div>
              <div className="rarity-count">{stats.topRarity.uncommon}</div>
            </div>
          </div>
          
          <div className="rarity-card rare">
            <div className="rarity-icon">🔴</div>
            <div className="rarity-content">
              <div className="rarity-name">Редкие</div>
              <div className="rarity-count">{stats.topRarity.rare}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Additions */}
      {stats.recentAdditions.length > 0 && (
        <div className="recent-section">
          <h2>Последние приобретения</h2>
          <div className="recent-grid">
            {stats.recentAdditions.map((item: any, index: number) => (
              <div key={index} className="recent-card">
                <div className="recent-card-header">
                  <h4>{item.card?.title}</h4>
                  <span className="recent-card-number">#{item.card?.number}</span>
                </div>
                <div className="recent-card-details">
                  <div className="recent-card-rarity">
                    {item.card?.rarity === 'o' ? '🟢 Обычная' : 
                     item.card?.rarity === 'ск' ? '🟡 Необычная' : '🔴 Редкая'}
                  </div>
                  <div className="recent-card-quantity">Количество: {item.quantity}</div>
                  <div className="recent-card-date">
                    {new Date(item.created_at).toLocaleDateString('ru-RU')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Быстрые действия</h2>
        <div className="actions-grid">
          <a href="/catalog" className="action-card">
            <div className="action-icon">📚</div>
            <div className="action-content">
              <h3>Каталог</h3>
              <p>Просмотреть все карточки</p>
            </div>
          </a>
          
          <a href="/portfolio" className="action-card">
            <div className="action-icon">💼</div>
            <div className="action-content">
              <h3>Портфолио</h3>
              <p>Управление коллекцией</p>
            </div>
          </a>
          
          <a href="/analytics" className="action-card">
            <div className="action-icon">📈</div>
            <div className="action-content">
              <h3>Аналитика</h3>
              <p>Детальная статистика</p>
            </div>
          </a>
          
          <a href="/wishlist" className="action-card">
            <div className="action-icon">💝</div>
            <div className="action-content">
              <h3>Список желаний</h3>
              <p>Отслеживание целей</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

// Protected route wrapper component
const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      <Navigation />
      <main className="main-content">
        {children}
      </main>
    </>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="app">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <Dashboard />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
              <Route path="/portfolio" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <SimplePortfolio />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
              <Route path="/catalog" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <CatalogGrid />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
              <Route path="/inventory" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <InventoryGrid />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
              <Route path="/wishlist" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <WishlistPage />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <AnalyticsPage />
                  </ProtectedLayout>
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </Router>
        <ReactQueryDevtools initialIsOpen={false} />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
