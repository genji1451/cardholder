#!/bin/bash
# Автоматическая настройка SSL для portfolio.cards
set -e

DOMAIN="cards.portfolio.cards"
EMAIL="admin@portfolio.cards"  # Измените если нужно
SERVER_IP="82.97.243.150"

echo "🔒 Настройка HTTPS для $DOMAIN"
echo "================================"

# Проверка DNS
echo "📡 Проверка DNS записи..."
RESOLVED_IP=$(dig +short $DOMAIN @8.8.8.8 | tail -1)
if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo "⚠️  Внимание: DNS еще не обновился"
    echo "   Текущий IP: $RESOLVED_IP"
    echo "   Ожидаемый: $SERVER_IP"
    echo "   Продолжаем настройку, но SSL может не установиться сразу..."
    echo "   DNS обновляется 5-30 минут"
    sleep 3
else
    echo "✅ DNS настроен правильно!"
fi

ssh root@$SERVER_IP << ENDSSH
set -e

echo ""
echo "📦 Установка Certbot..."
apt update -qq
apt install -y certbot python3-certbot-nginx > /dev/null 2>&1

echo "📝 Обновление конфигурации Nginx..."
cat > /etc/nginx/sites-available/cardapp << 'EOF'
server {
    listen 80;
    server_name cards.portfolio.cards;
    client_max_body_size 20M;

    location /static/ {
        alias /opt/cardapp/staticfiles/;
    }

    location /media/ {
        alias /opt/cardapp/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "✅ Nginx конфигурация обновлена"

echo "🔄 Перезагрузка Nginx..."
nginx -t && systemctl reload nginx

echo ""
echo "🔒 Получение SSL сертификата от Let's Encrypt..."
echo "   Домен: cards.portfolio.cards"
echo "   Email: $EMAIL"
echo ""

# Получаем SSL сертификат
if certbot --nginx -d cards.portfolio.cards \
    --non-interactive \
    --agree-tos \
    --redirect \
    --email $EMAIL 2>&1 | tee /tmp/certbot.log; then
    
    echo ""
    echo "✅ SSL сертификат успешно установлен!"
    
    # Обновляем Django settings для HTTPS
    echo ""
    echo "⚙️  Настройка Django для HTTPS..."
    
    # Обновляем .env
    sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=cards.portfolio.cards,portfolio.cards,82.97.243.150,localhost,127.0.0.1/' /opt/cardapp/.env
    sed -i 's|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=https://cards.portfolio.cards,http://cards.portfolio.cards,http://82.97.243.150|' /opt/cardapp/.env
    
    # Включаем HTTPS настройки в settings.py
    cat > /tmp/enable_https.py << 'PYEOF'
with open("/opt/cardapp/config/settings.py", "r") as f:
    content = f.read()

# Убираем старые комментарии и добавляем новые настройки
if "# Production HTTPS Settings" not in content:
    content += """

# Production HTTPS Settings (после установки SSL)
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
"""

with open("/opt/cardapp/config/settings.py", "w") as f:
    f.write(content)

print("✅ Django настроен для HTTPS")
PYEOF
    
    python3 /tmp/enable_https.py
    
    echo ""
    echo "🔄 Перезапуск приложения..."
    supervisorctl restart all
    
    echo ""
    echo "✅ ================================================"
    echo "✅           SSL УСПЕШНО НАСТРОЕН!"
    echo "✅ ================================================"
    echo ""
    echo "🌐 Ваши ссылки:"
    echo "   🔒 Админка: https://cards.portfolio.cards/admin/"
    echo "   🤖 Telegram бот: @cardloginbot"
    echo ""
    echo "📋 Логин: admin"
    echo "🔑 Пароль: admin123"
    echo ""
    echo "🔒 SSL сертификат автоматически обновляется!"
    echo "   Certbot настроен на автопродление."
    echo ""
    
else
    echo ""
    echo "⚠️  SSL сертификат не удалось установить"
    echo ""
    echo "Возможные причины:"
    echo "1. DNS еще не обновился (подождите 5-30 минут)"
    echo "2. Домен недоступен из интернета"
    echo "3. Порты 80/443 закрыты"
    echo ""
    echo "📋 Логи Certbot:"
    cat /tmp/certbot.log
    echo ""
    echo "🔄 Попробуйте запустить скрипт снова через 10-15 минут"
    echo "   Когда DNS полностью обновится"
    echo ""
    exit 1
fi

ENDSSH

echo ""
echo "✅ Готово! Откройте в браузере:"
echo "   https://cards.portfolio.cards/admin/"
echo ""

