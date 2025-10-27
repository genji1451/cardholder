# 🚀 План миграции Backend с Render на Timeweb

## 📋 Цель
Полностью перенести Django backend с Render на Timeweb сервер для:
- ✅ Полного контроля над сервером
- ✅ Лучшей производительности
- ✅ Отсутствия cold starts
- ✅ Использования PostgreSQL вместо SQLite
- ✅ Единой инфраструктуры (как telegram bot)

---

## 🎯 Этапы миграции

### Этап 1: Подготовка Timeweb сервера (30 мин)

**Задачи:**
1. Подключиться к Timeweb серверу по SSH
2. Обновить систему: `apt update && apt upgrade -y`
3. Установить базовые пакеты:
   ```bash
   apt install -y python3.11 python3.11-venv python3-pip
   apt install -y postgresql postgresql-contrib
   apt install -y nginx certbot python3-certbot-nginx
   apt install -y git supervisor
   ```

**Проверка:**
- [ ] SSH доступ работает
- [ ] Python 3.11+ установлен
- [ ] PostgreSQL работает
- [ ] Nginx установлен

---

### Этап 2: Настройка PostgreSQL (20 мин)

**Задачи:**
1. Создать базу данных:
   ```sql
   sudo -u postgres psql
   CREATE DATABASE cardholder_db;
   CREATE USER cardholder_user WITH PASSWORD 'strong_password';
   ALTER ROLE cardholder_user SET client_encoding TO 'utf8';
   ALTER ROLE cardholder_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE cardholder_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE cardholder_db TO cardholder_user;
   \q
   ```

2. Протестировать подключение:
   ```bash
   psql -U cardholder_user -d cardholder_db -h localhost
   ```

**Проверка:**
- [ ] База данных создана
- [ ] Пользователь создан
- [ ] Подключение работает

---

### Этап 3: Развертывание Django приложения (40 мин)

**Задачи:**

1. **Создать директорию проекта:**
   ```bash
   mkdir -p /var/www/cardholder
   cd /var/www/cardholder
   ```

2. **Клонировать репозиторий:**
   ```bash
   git clone https://github.com/genji1451/cardholder.git .
   ```

3. **Создать виртуальное окружение:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

4. **Установить зависимости:**
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install psycopg2-binary gunicorn
   ```

5. **Создать .env файл:**
   ```bash
   nano /var/www/cardholder/backend/.env
   ```
   
   Содержимое:
   ```env
   DJANGO_SECRET_KEY=your-super-secret-key-here
   DJANGO_DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   
   # Database
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=cardholder_db
   DB_USER=cardholder_user
   DB_PASSWORD=strong_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # CORS
   CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   
   # Telegram (если используется)
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHANNEL_ID=@your-channel
   ```

6. **Запустить миграции:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

7. **Создать суперпользователя:**
   ```bash
   python manage.py createsuperuser
   ```

**Проверка:**
- [ ] Код загружен
- [ ] Зависимости установлены
- [ ] Миграции выполнены
- [ ] Статика собрана

---

### Этап 4: Настройка Gunicorn (20 мин)

**Задачи:**

1. **Создать Gunicorn конфиг:**
   ```bash
   nano /var/www/cardholder/gunicorn_config.py
   ```
   
   Содержимое:
   ```python
   bind = "127.0.0.1:8000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   errorlog = "/var/log/cardholder/gunicorn_error.log"
   accesslog = "/var/log/cardholder/gunicorn_access.log"
   loglevel = "info"
   ```

2. **Создать systemd service:**
   ```bash
   sudo nano /etc/systemd/system/cardholder.service
   ```
   
   Содержимое:
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
       --config /var/www/cardholder/gunicorn_config.py \
       config.wsgi:application
   ExecReload=/bin/kill -s HUP $MAINPID
   KillMode=mixed
   TimeoutStopSec=5
   PrivateTmp=true
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Запустить сервис:**
   ```bash
   mkdir -p /var/log/cardholder
   chown -R www-data:www-data /var/www/cardholder
   chown -R www-data:www-data /var/log/cardholder
   
   systemctl daemon-reload
   systemctl start cardholder
   systemctl enable cardholder
   systemctl status cardholder
   ```

**Проверка:**
- [ ] Gunicorn запущен
- [ ] Service работает
- [ ] Автозапуск включен
- [ ] Логи пишутся

---

### Этап 5: Настройка Nginx (30 мин)

**Задачи:**

1. **Создать Nginx конфиг:**
   ```bash
   sudo nano /etc/nginx/sites-available/cardholder
   ```
   
   Содержимое:
   ```nginx
   upstream cardholder_backend {
       server 127.0.0.1:8000;
   }
   
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       
       client_max_body_size 10M;
       
       # Статические файлы
       location /static/ {
           alias /var/www/cardholder/backend/staticfiles/;
           expires 30d;
           add_header Cache-Control "public, immutable";
       }
       
       # Медиа файлы
       location /media/ {
           alias /var/www/cardholder/backend/media/;
           expires 7d;
       }
       
       # Проксирование на Django
       location / {
           proxy_pass http://cardholder_backend;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Host $host;
           proxy_redirect off;
           
           # CORS headers (если нужно)
           add_header 'Access-Control-Allow-Origin' '*' always;
           add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
           add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
           
           if ($request_method = 'OPTIONS') {
               return 204;
           }
       }
   }
   ```

2. **Активировать конфиг:**
   ```bash
   ln -s /etc/nginx/sites-available/cardholder /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

3. **Настроить SSL:**
   ```bash
   certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

**Проверка:**
- [ ] Nginx конфиг валиден
- [ ] HTTP работает
- [ ] SSL установлен
- [ ] HTTPS работает

---

### Этап 6: Обновление Frontend (Vercel) (20 мин)

**Задачи:**

1. **Обновить API client:**
   ```typescript
   // frontend/src/api/client.ts
   const API_BASE_URL = 'https://your-domain.com/api';
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

3. **Обновить CORS в Django:**
   ```python
   CORS_ALLOWED_ORIGINS = [
       'https://your-vercel-app.vercel.app',
       'https://your-domain.com',
   ]
   ```

4. **Закоммитить и задеплоить:**
   ```bash
   git add .
   git commit -m "Update API endpoint to Timeweb"
   git push origin main
   ```

**Проверка:**
- [ ] API URL обновлен
- [ ] Vercel задеплоил
- [ ] CORS работает
- [ ] Авторизация работает

---

### Этап 7: Автоматический деплой (30 мин)

**Задачи:**

1. **Создать deploy скрипт:**
   ```bash
   nano /var/www/cardholder/deploy.sh
   ```
   
   Содержимое:
   ```bash
   #!/bin/bash
   
   echo "🚀 Deploying Cardholder Backend..."
   
   cd /var/www/cardholder
   
   # Pull latest code
   git pull origin main
   
   # Activate venv
   source venv/bin/activate
   
   # Install dependencies
   cd backend
   pip install -r requirements.txt
   
   # Run migrations
   python manage.py migrate --noinput
   
   # Collect static
   python manage.py collectstatic --noinput
   
   # Restart service
   sudo systemctl restart cardholder
   
   echo "✅ Deployment complete!"
   ```

2. **Сделать скрипт исполняемым:**
   ```bash
   chmod +x /var/www/cardholder/deploy.sh
   ```

3. **Настроить Git hook (опционально):**
   ```bash
   # На GitHub: Settings → Webhooks → Add webhook
   # Payload URL: https://your-domain.com/deploy
   # Content type: application/json
   # Events: Just the push event
   ```

**Проверка:**
- [ ] Deploy скрипт работает
- [ ] Git hook настроен
- [ ] Автодеплой работает

---

### Этап 8: Мониторинг и Backup (20 мин)

**Задачи:**

1. **Настроить логирование:**
   ```bash
   # Смотреть логи Django
   journalctl -u cardholder -f
   
   # Смотреть логи Nginx
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

2. **Настроить backup БД:**
   ```bash
   nano /var/www/cardholder/backup.sh
   ```
   
   Содержимое:
   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/var/backups/cardholder"
   mkdir -p $BACKUP_DIR
   
   pg_dump -U cardholder_user cardholder_db > $BACKUP_DIR/backup_$DATE.sql
   
   # Keep only last 7 days
   find $BACKUP_DIR -type f -mtime +7 -delete
   ```

3. **Добавить в crontab:**
   ```bash
   crontab -e
   # Добавить:
   0 2 * * * /var/www/cardholder/backup.sh
   ```

**Проверка:**
- [ ] Логи доступны
- [ ] Backup работает
- [ ] Cron настроен

---

## 📊 Финальный чеклист

### Backend на Timeweb:
- [ ] Django запущен на Gunicorn
- [ ] PostgreSQL работает
- [ ] Nginx проксирует запросы
- [ ] SSL сертификат установлен
- [ ] Логи пишутся
- [ ] Backup настроен
- [ ] Автодеплой работает

### Frontend на Vercel:
- [ ] API URL обновлен на Timeweb
- [ ] CORS настроен правильно
- [ ] Авторизация работает
- [ ] Все endpoints доступны

### Интеграция:
- [ ] Регистрация работает
- [ ] Вход работает
- [ ] JWT токены работают
- [ ] API запросы проходят
- [ ] Нет CORS ошибок
- [ ] Нет 403/500 ошибок

---

## 🎯 Преимущества после миграции

1. **Производительность:**
   - ✅ Нет cold starts (как на Render)
   - ✅ PostgreSQL вместо SQLite
   - ✅ Dedicated сервер

2. **Контроль:**
   - ✅ Полный доступ к серверу
   - ✅ Настройка логов
   - ✅ Мониторинг ресурсов

3. **Стоимость:**
   - ✅ Фиксированная оплата
   - ✅ Нет лимитов запросов

4. **Надежность:**
   - ✅ Автозапуск при перезагрузке
   - ✅ Backup базы данных
   - ✅ SSL сертификат

---

## 📞 Troubleshooting

### Проблема: Gunicorn не запускается
```bash
journalctl -u cardholder -n 50
# Проверить логи и исправить ошибки
```

### Проблема: Nginx 502 Bad Gateway
```bash
systemctl status cardholder
# Убедиться что Gunicorn работает
```

### Проблема: CORS ошибки
```bash
# Проверить settings.py
CORS_ALLOWED_ORIGINS = ['https://your-vercel-app.vercel.app']
```

### Проблема: База данных не подключается
```bash
# Проверить .env
# Проверить PostgreSQL: systemctl status postgresql
```

---

## 🚀 Начнем?

Готовы начать миграцию? Какой у вас домен на Timeweb?

**Нужно знать:**
1. Домен для backend (например: api.cardholder.ru)
2. SSH доступ к Timeweb серверу
3. Подтвердить что Vercel app URL

После этого начнем пошаговую миграцию!

