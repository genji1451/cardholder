import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        {/* Основная информация */}
        <div className="footer-section">
          <h3>ИП Клопот Илья Алексеевич</h3>
          <p className="footer-text">
            <strong>ИНН:</strong> 891105545387
          </p>
          <p className="footer-text">
            Продажа коллекционных карточек и авторских картин
          </p>
        </div>

        {/* Юридические документы */}
        <div className="footer-section">
          <h3>Документы</h3>
          <ul className="footer-links">
            <li><Link to="/legal/offer">Публичная оферта</Link></li>
            <li><Link to="/legal/privacy">Политика конфиденциальности</Link></li>
            <li><Link to="/legal/delivery">Доставка и оплата</Link></li>
            <li><Link to="/legal/return">Возврат и обмен</Link></li>
          </ul>
        </div>

        {/* Контакты */}
        <div className="footer-section">
          <h3>Контакты</h3>
          <ul className="footer-contacts">
            <li>
              <a href="mailto:rextestudo@gmail.com">rextestudo@gmail.com</a>
            </li>
            <li>
              <a href="https://t.me/rex_testudo" target="_blank" rel="noopener noreferrer">
                @rex_testudo
              </a>
            </li>
            <li>
              <Link to="/contacts">Все контакты</Link>
            </li>
          </ul>
        </div>

        {/* Быстрые ссылки */}
        <div className="footer-section">
          <h3>Покупателям</h3>
          <ul className="footer-links">
            <li><Link to="/shop">Магазин</Link></li>
            <li><Link to="/cart">Корзина</Link></li>
            <li><Link to="/legal/payment">Способы оплаты</Link></li>
            <li><Link to="/legal/guarantee">Гарантии</Link></li>
          </ul>
        </div>
      </div>

      {/* Copyright */}
      <div className="footer-bottom">
        <div className="footer-container">
          <p className="copyright">
            © 2025 ИП Клопот Илья Алексеевич. ИНН: 891105545387. Все права защищены.
          </p>
          <p className="footer-disclaimer">
            Продолжая использовать сайт, вы соглашаетесь с <Link to="/legal/offer">условиями оферты</Link> и <Link to="/legal/privacy">политикой конфиденциальности</Link>.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

