#!/bin/bash
# Быстрое обновление приложения на сервере
set -e

SERVER_IP="82.97.243.150"
SERVER_USER="root"

echo "🔄 Обновление приложения на сервере..."

cd backend
tar -czf /tmp/backend_update.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    --exclude='.env' \
    .

scp /tmp/backend_update.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/cardapp
tar -xzf /tmp/backend_update.tar.gz
source venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --noinput
python manage.py collectstatic --noinput
supervisorctl restart all
echo "✅ Обновление завершено!"
ENDSSH

echo "✅ Приложение обновлено!"

