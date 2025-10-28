import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import Footer from '../components/Footer';
import CheckoutForm from '../components/CheckoutForm';
import './CartPage.css';

interface DeliveryForm {
  fullName: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  postalCode: string;
  country: string;
  comment: string;
}

const CartPage = () => {
  const { cart, removeFromCart, updateQuantity, getTotalPrice, clearCart } = useCart();
  const navigate = useNavigate();
  const [step, setStep] = useState<'cart' | 'delivery' | 'payment'>('cart');
  const [showCheckout, setShowCheckout] = useState(false);
  const [deliveryForm, setDeliveryForm] = useState<DeliveryForm>({
    fullName: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    postalCode: '',
    country: 'Россия',
    comment: '',
  });
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'sbp' | 'ozon'>('card');
  const [isProcessing, setIsProcessing] = useState(false);

  const deliveryPrice = 500; // Стоимость доставки
  const totalPrice = getTotalPrice();
  const finalPrice = totalPrice + deliveryPrice;

  const handleQuantityChange = (productId: number, change: number) => {
    const item = cart.find(item => item.id === productId);
    if (item) {
      updateQuantity(productId, item.quantity + change);
    }
  };

  const handleFormChange = (field: keyof DeliveryForm, value: string) => {
    setDeliveryForm(prev => ({ ...prev, [field]: value }));
  };

  const isDeliveryFormValid = () => {
    return (
      deliveryForm.fullName.trim() !== '' &&
      deliveryForm.phone.trim() !== '' &&
      deliveryForm.email.trim() !== '' &&
      deliveryForm.address.trim() !== '' &&
      deliveryForm.city.trim() !== ''
    );
  };

  const handleProceedToPayment = () => {
    if (!isDeliveryFormValid()) {
      alert('Пожалуйста, заполните все обязательные поля');
      return;
    }
    setStep('payment');
    window.scrollTo(0, 0);
  };

  const handlePayment = async () => {
    setIsProcessing(true);
    
    // Здесь будет интеграция с платежной системой
    // Например: Stripe, YooKassa, Tinkoff
    
    // Имитация обработки платежа
    setTimeout(() => {
      // Создаем данные заказа
      const orderData = {
        items: cart,
        delivery: deliveryForm,
        paymentMethod,
        totalPrice: finalPrice,
        orderDate: new Date().toISOString(),
      };

      // Отправляем в Telegram или на email
      const message = `
🛍️ НОВЫЙ ЗАКАЗ

📦 Товары:
${cart.map(item => `- ${item.title} x${item.quantity} = ₽${(item.price * item.quantity).toLocaleString()}`).join('\n')}

💰 Стоимость товаров: ₽${totalPrice.toLocaleString()}
🚚 Доставка: ₽${deliveryPrice.toLocaleString()}
💳 ИТОГО: ₽${finalPrice.toLocaleString()}

👤 Покупатель:
Имя: ${deliveryForm.fullName}
Телефон: ${deliveryForm.phone}
Email: ${deliveryForm.email}

📍 Адрес доставки:
Страна: ${deliveryForm.country}
Город: ${deliveryForm.city}
Адрес: ${deliveryForm.address}
Индекс: ${deliveryForm.postalCode}

💬 Комментарий: ${deliveryForm.comment || 'Нет'}

💳 Способ оплаты: ${paymentMethod === 'card' ? 'Банковская карта' : paymentMethod === 'sbp' ? 'СБП' : 'OZON Pay'}
      `.trim();

      console.log('Order:', orderData);
      console.log('Telegram message:', message);

      // В реальном приложении здесь будет:
      // 1. Отправка на бэкенд
      // 2. Создание платежа через API
      // 3. Редирект на страницу оплаты

      alert(`Заказ оформлен!\n\nСпасибо за покупку! Мы свяжемся с вами для подтверждения.\n\nДетали заказа отправлены на email: ${deliveryForm.email}`);
      
      clearCart();
      navigate('/shop');
      setIsProcessing(false);
    }, 2000);
  };

  if (cart.length === 0 && step === 'cart') {
    return (
      <div className="cart-page">
        <nav className="shop-nav">
          <Link to="/" className="shop-nav-logo">
            🕷️ Portfolio Cards
          </Link>
          <div className="shop-nav-links">
            <Link to="/shop" className="shop-nav-link">🛍️ Магазин</Link>
            <Link to="/" className="shop-nav-link">🏠 Главная</Link>
          </div>
        </nav>

        <div className="empty-cart">
          <div className="empty-cart-icon">🛒</div>
          <h2>Корзина пуста</h2>
          <p>Добавьте товары из магазина</p>
          <Link to="/shop" className="btn-primary">
            🛍️ Перейти в магазин
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <nav className="shop-nav">
        <Link to="/" className="shop-nav-logo">
          🕷️ Portfolio Cards
        </Link>
        <div className="shop-nav-links">
          <Link to="/shop" className="shop-nav-link">🛍️ Магазин</Link>
          <Link to="/" className="shop-nav-link">🏠 Главная</Link>
        </div>
      </nav>

      <div className="cart-container">
        {/* Progress Steps */}
        <div className="checkout-steps">
          <div className={`step ${step === 'cart' ? 'active' : 'completed'}`}>
            <div className="step-number">1</div>
            <div className="step-label">Корзина</div>
          </div>
          <div className={`step ${step === 'delivery' ? 'active' : step === 'payment' ? 'completed' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Доставка</div>
          </div>
          <div className={`step ${step === 'payment' ? 'active' : ''}`}>
            <div className="step-number">3</div>
            <div className="step-label">Оплата</div>
          </div>
        </div>

        {/* Cart Step */}
        {step === 'cart' && (
          <div className="cart-content">
            <div className="cart-items">
              <h2>Корзина ({cart.length})</h2>
              {cart.map(item => (
                <div key={item.id} className="cart-item">
                  <img src={item.image} alt={item.title} className="cart-item-image" />
                  <div className="cart-item-info">
                    <h3>{item.title}</h3>
                    <p className="cart-item-category">
                      {item.category === 'original' ? '⭐ Оригинальная серия' : 
                       item.category === 'meme' ? '😄 Мемная серия' :
                       item.category === 'art' ? '🎨 Картина' : '✨ Дизайнерская карточка'}
                    </p>
                    {item.isLimited && item.limitedInfo && (
                      <span className="limited-tag">
                        ⭐ {item.limitedInfo}
                      </span>
                    )}
                    {item.options && (
                      <div className="cart-item-options">
                        {item.options.hasCase && (
                          <span className="option-badge">📦 В кейсе</span>
                        )}
                        {item.options.filmType && item.options.filmType !== 'none' && (
                          <span className="option-badge">
                            {item.options.filmType === 'holographic' ? '✨ Голографическая' : '⚙️ Металлическая'}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="cart-item-quantity">
                    <button 
                      onClick={() => handleQuantityChange(item.id, -1)}
                      className="qty-btn"
                    >
                      −
                    </button>
                    <span>{item.quantity}</span>
                    <button 
                      onClick={() => handleQuantityChange(item.id, 1)}
                      className="qty-btn"
                    >
                      +
                    </button>
                  </div>
                  <div className="cart-item-price">
                    ₽{(item.price * item.quantity).toLocaleString()}
                  </div>
                  <button 
                    onClick={() => removeFromCart(item.id)}
                    className="cart-item-remove"
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>

            <div className="cart-summary">
              <h3>Итого</h3>
              <div className="summary-row">
                <span>Товары:</span>
                <span>₽{totalPrice.toLocaleString()}</span>
              </div>
              <div className="summary-row">
                <span>Доставка:</span>
                <span>₽{deliveryPrice.toLocaleString()}</span>
              </div>
              <div className="summary-total">
                <span>Итого:</span>
                <span>₽{finalPrice.toLocaleString()}</span>
              </div>
              <button onClick={() => setShowCheckout(true)} className="btn-checkout">
                💳 Оплатить через Robokassa
              </button>
              <Link to="/shop" className="btn-continue-shopping">
                ← Продолжить покупки
              </Link>
            </div>
          </div>
        )}

        {/* Delivery Step */}
        {step === 'delivery' && (
          <div className="delivery-form">
            <h2>📦 Данные доставки</h2>
            
            <div className="form-grid">
              <div className="form-group">
                <label>ФИО *</label>
                <input
                  type="text"
                  value={deliveryForm.fullName}
                  onChange={(e) => handleFormChange('fullName', e.target.value)}
                  placeholder="Иванов Иван Иванович"
                  required
                />
              </div>

              <div className="form-group">
                <label>Телефон *</label>
                <input
                  type="tel"
                  value={deliveryForm.phone}
                  onChange={(e) => handleFormChange('phone', e.target.value)}
                  placeholder="+7 (999) 123-45-67"
                  required
                />
              </div>

              <div className="form-group full-width">
                <label>Email *</label>
                <input
                  type="email"
                  value={deliveryForm.email}
                  onChange={(e) => handleFormChange('email', e.target.value)}
                  placeholder="example@mail.ru"
                  required
                />
              </div>

              <div className="form-group">
                <label>Страна *</label>
                <input
                  type="text"
                  value={deliveryForm.country}
                  onChange={(e) => handleFormChange('country', e.target.value)}
                  placeholder="Россия"
                  required
                />
              </div>

              <div className="form-group">
                <label>Город *</label>
                <input
                  type="text"
                  value={deliveryForm.city}
                  onChange={(e) => handleFormChange('city', e.target.value)}
                  placeholder="Москва"
                  required
                />
              </div>

              <div className="form-group full-width">
                <label>Адрес доставки *</label>
                <input
                  type="text"
                  value={deliveryForm.address}
                  onChange={(e) => handleFormChange('address', e.target.value)}
                  placeholder="ул. Ленина, д. 10, кв. 25"
                  required
                />
              </div>

              <div className="form-group">
                <label>Индекс</label>
                <input
                  type="text"
                  value={deliveryForm.postalCode}
                  onChange={(e) => handleFormChange('postalCode', e.target.value)}
                  placeholder="123456"
                />
              </div>

              <div className="form-group full-width">
                <label>Комментарий к заказу</label>
                <textarea
                  value={deliveryForm.comment}
                  onChange={(e) => handleFormChange('comment', e.target.value)}
                  placeholder="Дополнительная информация..."
                  rows={3}
                />
              </div>
            </div>

            <div className="form-actions">
              <button onClick={() => setStep('cart')} className="btn-back">
                ← Назад к корзине
              </button>
              <button onClick={handleProceedToPayment} className="btn-next">
                Продолжить к оплате →
              </button>
            </div>
          </div>
        )}

        {/* Payment Step */}
        {step === 'payment' && (
          <div className="payment-section">
            <h2>💳 Способ оплаты</h2>

            <div className="payment-methods">
              <div 
                className={`payment-method ${paymentMethod === 'card' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('card')}
              >
                <div className="payment-icon">💳</div>
                <div className="payment-info">
                  <h3>Банковская карта</h3>
                  <p>Visa, MasterCard, МИР</p>
                </div>
                <div className="payment-radio">
                  {paymentMethod === 'card' && '✓'}
                </div>
              </div>

              <div 
                className={`payment-method ${paymentMethod === 'sbp' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('sbp')}
              >
                <div className="payment-icon">📱</div>
                <div className="payment-info">
                  <h3>СБП (Система Быстрых Платежей)</h3>
                  <p>Оплата по номеру телефона</p>
                </div>
                <div className="payment-radio">
                  {paymentMethod === 'sbp' && '✓'}
                </div>
              </div>

              <div 
                className={`payment-method ${paymentMethod === 'ozon' ? 'selected' : ''}`}
                onClick={() => setPaymentMethod('ozon')}
              >
                <div className="payment-icon">🛒</div>
                <div className="payment-info">
                  <h3>OZON Pay</h3>
                  <p>Быстрая оплата через OZON</p>
                </div>
                <div className="payment-radio">
                  {paymentMethod === 'ozon' && '✓'}
                </div>
              </div>
            </div>

            <div className="order-summary-final">
              <h3>Детали заказа</h3>
              <div className="summary-items">
                {cart.map(item => (
                  <div key={item.id} className="summary-item">
                    <span>{item.title} x{item.quantity}</span>
                    <span>₽{(item.price * item.quantity).toLocaleString()}</span>
                  </div>
                ))}
              </div>
              <div className="summary-row">
                <span>Доставка:</span>
                <span>₽{deliveryPrice.toLocaleString()}</span>
              </div>
              <div className="summary-total">
                <span>К оплате:</span>
                <span>₽{finalPrice.toLocaleString()}</span>
              </div>
            </div>

            <div className="form-actions">
              <button onClick={() => setStep('delivery')} className="btn-back">
                ← Изменить данные
              </button>
              <button 
                onClick={handlePayment} 
                className="btn-pay"
                disabled={isProcessing}
              >
                {isProcessing ? 'Обработка...' : `Оплатить ₽${finalPrice.toLocaleString()}`}
              </button>
            </div>

            <div className="security-note">
              <div className="security-icon">🔒</div>
              <p>Безопасная оплата. Ваши данные защищены.</p>
            </div>
          </div>
        )}
      </div>

      {showCheckout && (
        <CheckoutForm onClose={() => setShowCheckout(false)} />
      )}

      <Footer />
    </div>
  );
};

export default CartPage;

