#!/bin/bash
# Быстрый деплой на Timeweb Cloud
set -e

SERVER_IP="82.97.243.150"
SERVER_USER="root"
APP_DIR="/opt/cardapp"

echo "🚀 Начинаем деплой на Timeweb Cloud..."
echo "📡 Сервер: $SERVER_IP"

# Проверка подключения
echo "📡 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo 'OK'" > /dev/null 2>&1; then
    echo "❌ Не удается подключиться к серверу"
    echo "💡 Выполните: ssh-copy-id $SERVER_USER@$SERVER_IP"
    exit 1
fi

echo "✅ Подключение установлено"

# Создаем архив для отправки
echo "📦 Создаем архив для отправки..."
cd backend
tar -czf /tmp/backend_deploy.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    --exclude='staticfiles' \
    .

echo "📤 Загружаем файлы на сервер..."
scp /tmp/backend_deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

echo "⚙️  Настройка сервера..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
set -e

echo "📂 Создаем директории..."
mkdir -p /opt/cardapp
cd /opt/cardapp

echo "📦 Распаковка файлов..."
tar -xzf /tmp/backend_deploy.tar.gz
rm /tmp/backend_deploy.tar.gz

echo "🐍 Установка Python и зависимостей..."
apt update -qq
apt install -y python3 python3-venv python3-pip nginx supervisor > /dev/null 2>&1

echo "🔧 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "📚 Установка Python пакетов..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo "🗄️  Настройка базы данных..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "👤 Создание суперпользователя (admin/admin123)..."
python manage.py shell << 'ENDPYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✅ Суперпользователь создан: admin / admin123")
else:
    print("✅ Суперпользователь уже существует")
ENDPYTHON

echo "📝 Создание конфигурации Supervisor для бота..."
cat > /etc/supervisor/conf.d/telegram-bot.conf << 'EOF'
[program:telegram_bot]
directory=/opt/cardapp
command=/opt/cardapp/venv/bin/python manage.py run_new_bot
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/telegram_bot.err.log
stdout_logfile=/var/log/telegram_bot.out.log
environment=PATH="/opt/cardapp/venv/bin"
EOF

echo "📝 Создание конфигурации Supervisor для Django..."
cat > /etc/supervisor/conf.d/django-app.conf << 'EOF'
[program:django_app]
directory=/opt/cardapp
command=/opt/cardapp/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/django_app.err.log
stdout_logfile=/var/log/django_app.out.log
environment=PATH="/opt/cardapp/venv/bin"
EOF

echo "📝 Создание конфигурации Nginx..."
cat > /etc/nginx/sites-available/cardapp << 'EOF'
server {
    listen 80;
    server_name 82.97.243.150;
    client_max_body_size 20M;

    location /static/ {
        alias /opt/cardapp/staticfiles/;
    }

    location /media/ {
        alias /opt/cardapp/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cardapp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "🔄 Запуск сервисов..."
supervisorctl reread
supervisorctl update
supervisorctl restart all
nginx -t && systemctl restart nginx

echo ""
echo "✅ ================================================"
echo "✅          ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "✅ ================================================"
echo ""
echo "🌐 Ваше приложение доступно:"
echo "   API/Admin: http://82.97.243.150/admin/"
echo "   Логин: admin"
echo "   Пароль: admin123"
echo ""
echo "🤖 Telegram Bot: @cardloginbot"
echo ""
echo "📊 Проверка статуса:"
echo "   supervisorctl status"
echo ""
echo "📋 Просмотр логов:"
echo "   tail -f /var/log/telegram_bot.out.log"
echo "   tail -f /var/log/django_app.out.log"
echo ""
ENDSSH

echo ""
echo "✅ ================================================"
echo "✅          ДЕПЛОЙ ЗАВЕРШЕН!"
echo "✅ ================================================"
echo ""
echo "🌐 Откройте в браузере: http://82.97.243.150/admin/"
echo "👤 Логин: admin"
echo "🔑 Пароль: admin123"
echo ""
echo "🤖 Проверьте бота в Telegram: @cardloginbot"
echo ""
echo "📊 Для просмотра статуса на сервере:"
echo "   ssh root@82.97.243.150 'supervisorctl status'"
echo ""

