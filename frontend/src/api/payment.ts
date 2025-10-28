import apiClient from './client';

export interface OrderItem {
  product_id: number;
  product_title: string;
  product_description: string;
  product_image: string;
  price: number;
  quantity: number;
  has_case?: boolean;
  film_type?: 'none' | 'holographic' | 'metallic';
}

export interface CreateOrderRequest {
  email: string;
  phone?: string;
  delivery_address?: string;
  delivery_method?: string;
  delivery_cost?: number;
  items: OrderItem[];
}

export interface PaymentResponse {
  order_id: string;
  payment_id: number;
  amount: number;
  robokassa_url: string;
  payment_data: Record<string, string>;
  signature: string;
}

export interface PaymentStatus {
  order_id: string;
  status: 'pending' | 'success' | 'failed' | 'cancelled';
  amount: number;
  paid_at?: string;
}

export const paymentApi = {
  // Создание заказа и получение данных для оплаты
  createOrder: async (orderData: CreateOrderRequest): Promise<PaymentResponse> => {
    const response = await apiClient.post('/payment/create-order/', orderData);
    return response.data;
  },

  // Проверка статуса платежа
  getPaymentStatus: async (orderId: string): Promise<PaymentStatus> => {
    const response = await apiClient.get(`/payment/status/${orderId}/`);
    return response.data;
  },

  // Создание формы для оплаты через Robokassa
  createPaymentForm: (paymentData: PaymentResponse): HTMLFormElement => {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = paymentData.robokassa_url;
    form.style.display = 'none';

    Object.entries(paymentData.payment_data).forEach(([key, value]) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = key;
      input.value = value;
      form.appendChild(input);
    });

    document.body.appendChild(form);
    return form;
  },

  // Отправка формы оплаты
  submitPayment: (paymentData: PaymentResponse): void => {
    const form = paymentApi.createPaymentForm(paymentData);
    form.submit();
  }
};
