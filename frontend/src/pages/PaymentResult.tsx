import { Link } from 'react-router-dom';
import Footer from '../components/Footer';
import './PaymentResult.css';

interface PaymentResultProps {
  success: boolean;
}

const PaymentResult = ({ success }: PaymentResultProps) => {
  const orderId = new URLSearchParams(window.location.search).get('InvId');

  return (
    <div className="payment-result-page">
      <div className="payment-result-container">
        <div className={`result-icon ${success ? 'success' : 'error'}`}>
          {success ? '✅' : '❌'}
        </div>
        
        <h1 className={`result-title ${success ? 'success' : 'error'}`}>
          {success ? 'Оплата прошла успешно!' : 'Ошибка оплаты'}
        </h1>
        
        <p className="result-message">
          {success 
            ? 'Ваш заказ успешно оплачен. Мы свяжемся с вами для подтверждения деталей доставки.'
            : 'Произошла ошибка при обработке платежа. Пожалуйста, попробуйте еще раз или свяжитесь с нами.'
          }
        </p>
        
        {orderId && (
          <div className="order-info">
            <p><strong>Номер заказа:</strong> {orderId}</p>
          </div>
        )}
        
        <div className="result-actions">
          <Link to="/shop" className="btn-primary">
            🛍️ Вернуться в магазин
          </Link>
          
          <Link to="/contacts" className="btn-secondary">
            📞 Связаться с нами
          </Link>
        </div>
        
        {success && (
          <div className="success-details">
            <h3>Что дальше?</h3>
            <ul>
              <li>📧 Мы отправим подтверждение на ваш email</li>
              <li>📦 Подготовим ваш заказ к отправке</li>
              <li>🚚 Свяжемся с вами для уточнения деталей доставки</li>
              <li>⏰ Обычно доставка занимает 2-7 дней</li>
            </ul>
          </div>
        )}
      </div>
      
      <Footer />
    </div>
  );
};

export default PaymentResult;
