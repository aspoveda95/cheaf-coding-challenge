#!/bin/bash

# Flash Promos - Environment Setup Script
# This script sets up a complete development environment with pyenv

set -e

ENV_NAME="flash-promos-env"
PYTHON_VERSION="3.11.7"

echo "🚀 Setting up Flash Promos development environment..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv is not installed. Please install pyenv first."
    echo "   Visit: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Install Python version if not available
echo "📦 Checking Python $PYTHON_VERSION..."
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
else
    echo "✅ Python $PYTHON_VERSION already installed"
fi

# Create virtual environment
echo "🔧 Creating virtual environment '$ENV_NAME'..."
if pyenv versions | grep -q "$ENV_NAME"; then
    echo "⚠️  Virtual environment '$ENV_NAME' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        pyenv uninstall -f $ENV_NAME
        pyenv virtualenv $PYTHON_VERSION $ENV_NAME
    fi
else
    pyenv virtualenv $PYTHON_VERSION $ENV_NAME
fi

# Set local environment
echo "🎯 Setting local environment..."
pyenv local $ENV_NAME

# Activate environment
echo "⚡ Activating environment..."
pyenv activate $ENV_NAME

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements/development.txt" ]; then
    pip install -r requirements/development.txt
else
    echo "⚠️  requirements/development.txt not found, installing base requirements..."
    pip install -r requirements/base.txt
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
DEBUG=1
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flash_promos
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
EOF
    echo "✅ .env file created with random SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

# Run migrations if Django is available
if python -c "import django" 2>/dev/null; then
    echo "🗄️  Running database migrations..."
    python manage.py migrate
    echo "✅ Database migrations completed"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate environment: pyenv activate $ENV_NAME"
echo "   2. Start development server: python manage.py runserver"
echo "   3. Run tests: pytest"
echo "   4. Install pre-commit: pre-commit install"
echo ""
echo "🔧 Environment info:"
echo "   Python version: $(python --version)"
echo "   Environment: $ENV_NAME"
echo "   Location: $(which python)"
