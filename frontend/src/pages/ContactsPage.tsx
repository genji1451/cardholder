import { Link } from 'react-router-dom';
import Footer from '../components/Footer';
import './ContactsPage.css';

const ContactsPage = () => {
  return (
    <div className="contacts-page">
      <nav className="shop-nav">
        <Link to="/" className="shop-nav-logo">
          🕷️ Portfolio Cards
        </Link>
        <div className="shop-nav-links">
          <Link to="/shop" className="shop-nav-link">🛍️ Магазин</Link>
          <Link to="/" className="shop-nav-link">🏠 Главная</Link>
        </div>
      </nav>

      <div className="contacts-container">
        <h1>Контактная информация</h1>

        <div className="contacts-grid">
          {/* Юридическая информация */}
          <div className="contact-card">
            <div className="contact-icon">🏢</div>
            <h2>Юридическая информация</h2>
            <div className="contact-details">
              <p><strong>Индивидуальный предприниматель</strong></p>
              <p>Клопот Илья Алексеевич</p>
              <p><strong>ИНН:</strong> 891105545387</p>
              <p><strong>Деятельность:</strong> Продажа коллекционных карточек и авторских картин</p>
            </div>
          </div>

          {/* Связь */}
          <div className="contact-card">
            <div className="contact-icon">✉️</div>
            <h2>Связь с нами</h2>
            <div className="contact-details">
              <p>
                <strong>Email:</strong><br />
                <a href="mailto:rextestudo@gmail.com">rextestudo@gmail.com</a>
              </p>
              <p>
                <strong>Telegram:</strong><br />
                <a href="https://t.me/rex_testudo" target="_blank" rel="noopener noreferrer">
                  @rex_testudo
                </a>
              </p>
              <p className="response-time">
                ⏱️ Среднее время ответа: 2-4 часа
              </p>
            </div>
          </div>

          {/* График работы */}
          <div className="contact-card">
            <div className="contact-icon">🕐</div>
            <h2>График работы</h2>
            <div className="contact-details">
              <p><strong>Прием заказов:</strong> Круглосуточно через сайт</p>
              <p><strong>Поддержка:</strong> Пн-Вс: 10:00 - 22:00 (МСК)</p>
              <p><strong>Обработка заказов:</strong> Ежедневно</p>
              <p><strong>Отправка:</strong> В течение 1-3 рабочих дней</p>
            </div>
          </div>

          {/* Способы оплаты */}
          <div className="contact-card">
            <div className="contact-icon">💳</div>
            <h2>Способы оплаты</h2>
            <div className="contact-details">
              <p>✅ Банковские карты (Visa, MasterCard, МИР)</p>
              <p>✅ Система Быстрых Платежей (СБП)</p>
              <p className="secure-note">
                🔒 Все платежи защищены и проходят через безопасные платежные шлюзы
              </p>
            </div>
          </div>

          {/* Доставка */}
          <div className="contact-card">
            <div className="contact-icon">📦</div>
            <h2>Доставка</h2>
            <div className="contact-details">
              <p><strong>По России:</strong></p>
              <p>• Ozon: от 99₽ (2-7 дней)</p>
              <p>• Яндекс Доставка: 300₽ (1-3 дня)</p>
              <p>• Почта России: от 100₽ (7-14 дней)</p>
              <p><strong>🎁 Бесплатная доставка</strong> при заказе от 1000₽</p>
              <p className="info-note">
                <Link to="/legal/delivery">Подробнее о доставке →</Link>
              </p>
            </div>
          </div>

          {/* Гарантии */}
          <div className="contact-card">
            <div className="contact-icon">✅</div>
            <h2>Гарантии</h2>
            <div className="contact-details">
              <p>✅ Подлинность всех карточек</p>
              <p>✅ Качественная упаковка</p>
              <p>✅ Возврат в течение 14 дней</p>
              <p>✅ Отслеживание посылки</p>
              <p className="info-note">
                <Link to="/legal/return">Условия возврата →</Link>
              </p>
            </div>
          </div>
        </div>

        {/* Форма обратной связи */}
        <div className="feedback-section">
          <h2>Остались вопросы?</h2>
          <p>Свяжитесь с нами любым удобным способом</p>
          <div className="feedback-buttons">
            <a 
              href="https://t.me/rex_testudo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-telegram"
            >
              ✈️ Написать в Telegram
            </a>
            <a 
              href="mailto:rextestudo@gmail.com"
              className="btn-email"
            >
              ✉️ Отправить Email
            </a>
          </div>
        </div>

        {/* Юридическая информация */}
        <div className="legal-info">
          <h3>Правовая информация</h3>
          <div className="legal-links">
            <Link to="/legal/offer">Публичная оферта</Link>
            <Link to="/legal/privacy">Политика конфиденциальности</Link>
            <Link to="/legal/delivery">Доставка и оплата</Link>
            <Link to="/legal/return">Возврат и обмен</Link>
            <Link to="/legal/guarantee">Гарантии</Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default ContactsPage;

