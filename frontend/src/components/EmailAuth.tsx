import React, { useState } from 'react';
import './EmailAuth.css';

interface EmailAuthProps {
  onAuth: (authData: any) => void;
  isLoading?: boolean;
}

const EmailAuth: React.FC<EmailAuthProps> = ({ onAuth, isLoading = false }) => {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (isRegisterMode) {
      // Validation for registration
      if (!formData.username.trim()) {
        newErrors.username = 'Логин обязателен';
      } else if (formData.username.length < 3) {
        newErrors.username = 'Логин должен быть не менее 3 символов';
      }

      if (!formData.email.trim()) {
        newErrors.email = 'Email обязателен';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Некорректный email';
      }

      if (!formData.password) {
        newErrors.password = 'Пароль обязателен';
      } else if (formData.password.length < 8) {
        newErrors.password = 'Пароль должен быть не менее 8 символов';
      }

      if (formData.password !== formData.password2) {
        newErrors.password2 = 'Пароли не совпадают';
      }
    } else {
      // Validation for login
      if (!formData.email.trim()) {
        newErrors.email = 'Email или логин обязателен';
      }

      if (!formData.password) {
        newErrors.password = 'Пароль обязателен';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    if (isRegisterMode) {
      // Registration data
      onAuth({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password2: formData.password2,
        first_name: formData.first_name,
        last_name: formData.last_name,
        mode: 'register'
      });
    } else {
      // Login data (email or username)
      onAuth({
        login: formData.email, // Can be email or username
        password: formData.password,
        mode: 'login'
      });
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setFormData({
      username: '',
      email: '',
      password: '',
      password2: '',
      first_name: '',
      last_name: '',
    });
    setErrors({});
  };

  return (
    <div className="email-auth">
      <div className="email-auth-header">
        <h2>{isRegisterMode ? '📝 Регистрация' : '🔐 Вход'}</h2>
        <p>
          {isRegisterMode 
            ? 'Создайте аккаунт для доступа к сервису' 
            : 'Войдите с помощью email или логина'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="email-auth-form">
        {isRegisterMode && (
          <>
            <div className="form-group">
              <label htmlFor="username">Логин *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Введите логин"
                disabled={isLoading}
                className={errors.username ? 'error' : ''}
              />
              {errors.username && <span className="error-text">{errors.username}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="example@email.com"
                disabled={isLoading}
                className={errors.email ? 'error' : ''}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">Имя</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="Имя"
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Фамилия</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="Фамилия"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">Пароль *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Минимум 8 символов"
                disabled={isLoading}
                className={errors.password ? 'error' : ''}
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="password2">Подтвердите пароль *</label>
              <input
                type="password"
                id="password2"
                name="password2"
                value={formData.password2}
                onChange={handleInputChange}
                placeholder="Повторите пароль"
                disabled={isLoading}
                className={errors.password2 ? 'error' : ''}
              />
              {errors.password2 && <span className="error-text">{errors.password2}</span>}
            </div>
          </>
        )}

        {!isRegisterMode && (
          <>
            <div className="form-group">
              <label htmlFor="email">Email или Логин *</label>
              <input
                type="text"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email или логин"
                disabled={isLoading}
                className={errors.email ? 'error' : ''}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="password">Пароль *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Введите пароль"
                disabled={isLoading}
                className={errors.password ? 'error' : ''}
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>
          </>
        )}

        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="loading-spinner-small"></span>
          ) : (
            isRegisterMode ? 'Зарегистрироваться' : 'Войти'
          )}
        </button>
      </form>

      <div className="auth-toggle">
        <button 
          type="button"
          onClick={toggleMode}
          className="toggle-mode-button"
          disabled={isLoading}
        >
          {isRegisterMode 
            ? 'Уже есть аккаунт? Войти' 
            : 'Нет аккаунта? Зарегистрироваться'}
        </button>
      </div>
    </div>
  );
};

export default EmailAuth;
