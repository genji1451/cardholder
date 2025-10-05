# 📤 Загрузка проекта на GitHub

## 🔧 ШАГ 1: Создание репозитория на GitHub

### 1.1 Создайте новый репозиторий
1. Зайдите на [github.com](https://github.com)
2. Нажмите зеленую кнопку "New" или "+" → "New repository"
3. Заполните форму:
   - **Repository name**: `spiderman-cards-portfolio`
   - **Description**: `🕷️ Spider-Man Cards Collection Portfolio - Modern platform for card collectors with Telegram authentication`
   - **Visibility**: Public ✅
   - **Initialize**: НЕ ставьте галочки (у нас уже есть код)

### 1.2 Скопируйте URL репозитория
После создания вы увидите что-то вроде:
```
https://github.com/yourusername/spiderman-cards-portfolio.git
```

## 🔧 ШАГ 2: Загрузка кода

### 2.1 Добавьте remote origin
```bash
cd /Users/rex/Documents/cards
git remote add origin https://github.com/yourusername/spiderman-cards-portfolio.git
```

### 2.2 Загрузите код
```bash
git branch -M main
git push -u origin main
```

## 🔧 ШАГ 3: Проверка загрузки

После загрузки проверьте:
1. ✅ Все файлы загружены
2. ✅ README.md отображается
3. ✅ Структура проекта правильная
4. ✅ .gitignore работает (не видно venv/, node_modules/, etc.)

## 🔧 ШАГ 4: Настройка для Vercel

### 4.1 Подключение к Vercel
1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Выберите "Import Git Repository"
4. Найдите ваш репозиторий `spiderman-cards-portfolio`
5. Нажмите "Import"

### 4.2 Настройка проекта в Vercel
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 4.3 Переменные окружения
В Settings → Environment Variables добавьте:
```
VITE_API_URL = https://your-backend-url.herokuapp.com/api
```

## 🔧 ШАГ 5: Настройка Telegram бота

### 5.1 Получите URL вашего приложения
После развертывания на Vercel вы получите URL вида:
```
https://spiderman-cards-portfolio.vercel.app
```

### 5.2 Настройте домен в @BotFather
1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/setdomain`
3. Выберите бота `@cardloginbot`
4. Введите домен: `spiderman-cards-portfolio.vercel.app`

## 🧪 Тестирование

### 1. Откройте сайт
```
https://spiderman-cards-portfolio.vercel.app/auth
```

### 2. Протестируйте авторизацию
1. Убедитесь, что переключены на режим Telegram
2. Нажмите "Login with Telegram"
3. Авторизуйтесь через Telegram
4. Проверьте дашборд

## 📋 Структура проекта

```
spiderman-cards-portfolio/
├── README.md                    # Описание проекта
├── VERCEL_SETUP.md             # Инструкция для Vercel
├── TELEGRAM_SETUP.md           # Настройка Telegram
├── DEPLOY_TO_VERCEL.md         # Полная инструкция развертывания
├── .gitignore                  # Игнорируемые файлы
├── vercel.json                 # Конфигурация Vercel
├── backend/                    # Django API
│   ├── apps/
│   │   ├── core/              # Авторизация, пользователи
│   │   ├── cards/             # Модели карточек
│   │   ├── inventory/         # Инвентарь
│   │   └── analytics/         # Аналитика
│   └── config/                # Настройки Django
├── frontend/                   # React приложение
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/            # Страницы
│   │   ├── contexts/         # AuthContext
│   │   └── api/              # API клиент
│   └── package.json          # Зависимости
└── scripts/                   # Скрипты развертывания
    ├── deploy_to_vercel.sh   # Автоматическое развертывание
    ├── setup_ngrok.sh        # Локальное тестирование
    └── setup_https.sh        # HTTPS сертификаты
```

## 🎯 Готово к развертыванию!

После загрузки на GitHub:
1. ✅ Код в репозитории
2. ✅ README с описанием
3. ✅ Инструкции для Vercel
4. ✅ Все зависимости указаны
5. ✅ Конфигурация готова

**Следующий шаг**: Развертывание на Vercel! 🚀
