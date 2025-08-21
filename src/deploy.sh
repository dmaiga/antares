#!/bin/bash
set -e  # Stop on any error

echo "=== Démarrage du déploiement ==="

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Application des migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# Création du superuser avec EMAIL uniquement
echo "👤 Vérification du superuser..."
if ! python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Création du superuser...')
    User.objects.create_superuser(
        email='dadi@antares.net', 
        password='$SUPERUSER_PASSWORD'
    )
    print('Superuser créé !')
else:
    print('Superuser existe déjà')
"; then
    echo "⚠️  Impossible de vérifier/créer le superuser"
fi

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Déploiement terminé avec succès !"