#!/bin/bash
# Проверка статуса сервера
SERVER_IP="82.97.243.150"
SERVER_USER="root"

echo "📊 Статус сервисов:"
ssh $SERVER_USER@$SERVER_IP 'supervisorctl status'

echo ""
echo "📋 Последние логи бота:"
ssh $SERVER_USER@$SERVER_IP 'tail -n 20 /var/log/telegram_bot.out.log'

echo ""
echo "📋 Последние логи Django:"
ssh $SERVER_USER@$SERVER_IP 'tail -n 20 /var/log/django_app.out.log'

