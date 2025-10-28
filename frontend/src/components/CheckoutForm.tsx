import { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { paymentApi, type CreateOrderRequest } from '../api/payment';
import './CheckoutForm.css';

interface CheckoutFormProps {
  onClose: () => void;
}

const CheckoutForm = ({ onClose }: CheckoutFormProps) => {
  const { cart, clearCart, getTotalPrice } = useCart();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    delivery_address: '',
    delivery_method: 'Ozon',
    delivery_cost: 0
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const calculateDeliveryCost = (method: string) => {
    const total = getTotalPrice();
    if (total >= 1000) return 0; // Бесплатная доставка от 1000₽
    
    switch (method) {
      case 'Ozon': return 99;
      case 'Яндекс Доставка': return 300;
      case 'Почта России': return 100;
      default: return 0;
    }
  };

  const handleDeliveryMethodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const method = e.target.value;
    const cost = calculateDeliveryCost(method);
    setFormData(prev => ({
      ...prev,
      delivery_method: method,
      delivery_cost: cost
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Подготавливаем данные заказа
      const orderData: CreateOrderRequest = {
        email: formData.email,
        phone: formData.phone,
        delivery_address: formData.delivery_address,
        delivery_method: formData.delivery_method,
        delivery_cost: formData.delivery_cost,
        items: cart.map(item => ({
          product_id: item.id,
          product_title: item.title,
          product_description: item.description,
          product_image: item.image,
          price: item.price,
          quantity: item.quantity,
          has_case: item.options?.hasCase,
          film_type: item.options?.filmType || 'none'
        }))
      };

      // Создаем заказ и получаем данные для оплаты
      const paymentData = await paymentApi.createOrder(orderData);
      
      // Очищаем корзину
      clearCart();
      
      // Перенаправляем на оплату
      paymentApi.submitPayment(paymentData);
      
    } catch (err: any) {
      console.error('Ошибка создания заказа:', err);
      setError(err.response?.data?.message || 'Произошла ошибка при создании заказа');
    } finally {
      setIsLoading(false);
    }
  };

  const totalAmount = getTotalPrice() + formData.delivery_cost;

  return (
    <div className="checkout-overlay" onClick={onClose}>
      <div className="checkout-modal" onClick={(e) => e.stopPropagation()}>
        <button className="checkout-close" onClick={onClose}>✕</button>
        
        <div className="checkout-header">
          <h2>Оформление заказа</h2>
          <p>Заполните данные для доставки и оплаты</p>
        </div>

        <form onSubmit={handleSubmit} className="checkout-form">
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Телефон</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              placeholder="+7 (999) 123-45-67"
            />
          </div>

          <div className="form-group">
            <label htmlFor="delivery_method">Способ доставки</label>
            <select
              id="delivery_method"
              name="delivery_method"
              value={formData.delivery_method}
              onChange={handleDeliveryMethodChange}
            >
              <option value="Ozon">Ozon - от 99₽</option>
              <option value="Яндекс Доставка">Яндекс Доставка - 300₽</option>
              <option value="Почта России">Почта России - от 100₽</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="delivery_address">Адрес доставки</label>
            <textarea
              id="delivery_address"
              name="delivery_address"
              value={formData.delivery_address}
              onChange={handleInputChange}
              placeholder="Укажите полный адрес доставки"
              rows={3}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="checkout-summary">
            <div className="summary-row">
              <span>Товары ({cart.length}):</span>
              <span>₽{getTotalPrice().toLocaleString()}</span>
            </div>
            <div className="summary-row">
              <span>Доставка:</span>
              <span>
                {formData.delivery_cost === 0 ? 'Бесплатно' : `₽${formData.delivery_cost}`}
              </span>
            </div>
            <div className="summary-row total">
              <span>Итого:</span>
              <span>₽{totalAmount.toLocaleString()}</span>
            </div>
          </div>

          <button 
            type="submit" 
            className="checkout-button"
            disabled={isLoading || cart.length === 0}
          >
            {isLoading ? 'Обработка...' : '💳 Оплатить через Robokassa'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CheckoutForm;
