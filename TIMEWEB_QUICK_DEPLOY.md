# ⚡ Быстрый деплой на Timeweb - Команды

## 🎯 Подготовка (5 команд)

```bash
# 1. Подключиться к серверу
ssh root@your-timeweb-ip

# 2. Обновить систему
apt update && apt upgrade -y

# 3. Установить все необходимое
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx git supervisor

# 4. Проверить установку
python3.11 --version
psql --version
nginx -v
```

---

## 🗄️ PostgreSQL (4 команды)

```bash
# 1. Войти в PostgreSQL
sudo -u postgres psql

# 2. Создать БД и пользователя (в psql)
CREATE DATABASE cardholder_db;
CREATE USER cardholder_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';
ALTER ROLE cardholder_user SET client_encoding TO 'utf8';
ALTER ROLE cardholder_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cardholder_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cardholder_db TO cardholder_user;
\q

# 3. Протестировать подключение
psql -U cardholder_user -d cardholder_db -h localhost

# 4. Выйти
\q
```

---

## 📦 Django App (10 команд)

```bash
# 1. Создать директорию
mkdir -p /var/www/cardholder && cd /var/www/cardholder

# 2. Клонировать репозиторий
git clone https://github.com/genji1451/cardholder.git .

# 3. Создать venv
python3.11 -m venv venv

# 4. Активировать venv
source venv/bin/activate

# 5. Установить зависимости
cd backend
pip install -r requirements.txt
pip install psycopg2-binary gunicorn

# 6. Создать .env файл
nano .env
# Скопировать содержимое из раздела "Содержимое .env" ниже

# 7. Запустить миграции
python manage.py migrate

# 8. Собрать статику
python manage.py collectstatic --noinput

# 9. Создать суперпользователя
python manage.py createsuperuser

# 10. Протестировать запуск
python manage.py runserver 0.0.0.0:8000
# Ctrl+C для остановки
```

---

## 📄 Содержимое .env

```env
DJANGO_SECRET_KEY=generate-your-secret-key-here-use-django-secret-key-generator
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-timeweb-ip

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cardholder_db
DB_USER=cardholder_user
DB_PASSWORD=YOUR_STRONG_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://*.vercel.app

# Telegram (если нужно)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHANNEL_ID=@your-channel
```

---

## 🔧 Gunicorn Service (3 команды)

```bash
# 1. Создать systemd service
nano /etc/systemd/system/cardholder.service
# Скопировать содержимое ниже

# 2. Создать директории и установить права
mkdir -p /var/log/cardholder
chown -R www-data:www-data /var/www/cardholder
chown -R www-data:www-data /var/log/cardholder

# 3. Запустить service
systemctl daemon-reload
systemctl start cardholder
systemctl enable cardholder
systemctl status cardholder
```

### Содержимое /etc/systemd/system/cardholder.service:

```ini
[Unit]
Description=Cardholder Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/cardholder/backend
Environment="PATH=/var/www/cardholder/venv/bin"
ExecStart=/var/www/cardholder/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 30 \
    --access-logfile /var/log/cardholder/gunicorn_access.log \
    --error-logfile /var/log/cardholder/gunicorn_error.log \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🌐 Nginx (4 команды)

```bash
# 1. Создать конфиг
nano /etc/nginx/sites-available/cardholder
# Скопировать содержимое ниже

# 2. Активировать конфиг
ln -s /etc/nginx/sites-available/cardholder /etc/nginx/sites-enabled/

# 3. Протестировать конфиг
nginx -t

# 4. Перезапустить Nginx
systemctl restart nginx
```

### Содержимое /etc/nginx/sites-available/cardholder:

```nginx
upstream cardholder_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 10M;
    
    location /static/ {
        alias /var/www/cardholder/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/cardholder/backend/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://cardholder_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## 🔒 SSL (1 команда)

```bash
# Установить SSL сертификат
certbot --nginx -d your-domain.com -d www.your-domain.com --non-interactive --agree-tos -m your-email@example.com
```

---

## 🔄 Deploy Script (2 команды)

```bash
# 1. Создать deploy скрипт
nano /var/www/cardholder/deploy.sh
# Скопировать содержимое ниже

# 2. Сделать исполняемым
chmod +x /var/www/cardholder/deploy.sh
```

### Содержимое /var/www/cardholder/deploy.sh:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying Cardholder Backend..."

cd /var/www/cardholder

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate venv
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate --noinput

# Collect static
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart cardholder

# Check status
sleep 2
if systemctl is-active --quiet cardholder; then
    echo "✅ Deployment complete! Service is running."
else
    echo "❌ Service failed to start!"
    systemctl status cardholder
    exit 1
fi
```

---

## 📊 Полезные команды

```bash
# Смотреть логи Django
journalctl -u cardholder -f

# Смотреть логи Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Смотреть логи Gunicorn
tail -f /var/log/cardholder/gunicorn_error.log

# Перезапустить сервис
systemctl restart cardholder

# Проверить статус
systemctl status cardholder

# Обновить приложение
cd /var/www/cardholder && ./deploy.sh

# Создать backup БД
pg_dump -U cardholder_user cardholder_db > backup_$(date +%Y%m%d).sql

# Восстановить backup
psql -U cardholder_user cardholder_db < backup_20231018.sql
```

---

## ✅ Тестирование

```bash
# 1. Проверить что Django работает
curl http://localhost:8000/api/health/

# 2. Проверить через Nginx
curl http://your-domain.com/api/health/

# 3. Проверить HTTPS
curl https://your-domain.com/api/health/

# Должен вернуть JSON с статусом
```

---

## 🎯 Что дальше?

После успешного деплоя на Timeweb:

1. **Обновить frontend:**
   ```typescript
   // frontend/src/api/client.ts
   const baseURL = 'https://your-domain.com/api';
   ```

2. **Обновить vercel.json:**
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://your-domain.com/api/:path*"
       }
     ]
   }
   ```

3. **Закоммитить и задеплоить:**
   ```bash
   git add .
   git commit -m "🚀 Migrate backend to Timeweb"
   git push origin main
   ```

4. **Протестировать полную интеграцию**

---

## 🆘 Если что-то пошло не так

1. **Service не запускается:**
   ```bash
   journalctl -u cardholder -n 100
   ```

2. **502 Bad Gateway:**
   ```bash
   systemctl status cardholder
   tail -f /var/log/cardholder/gunicorn_error.log
   ```

3. **База данных не подключается:**
   ```bash
   # Проверить PostgreSQL
   systemctl status postgresql
   
   # Проверить подключение
   psql -U cardholder_user -d cardholder_db -h localhost
   ```

4. **CORS ошибки:**
   ```bash
   # Проверить settings.py
   nano /var/www/cardholder/backend/config/settings.py
   # Убедиться что CORS_ALLOWED_ORIGINS правильно настроен
   ```

---

**Готовы начать? Скопируйте команды и выполните по порядку! 🚀**

