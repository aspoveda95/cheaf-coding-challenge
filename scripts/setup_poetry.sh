#!/bin/bash

# Flash Promos - Poetry Environment Setup Script
# This script sets up a complete development environment with Poetry

set -e

PYTHON_VERSION="3.11.7"

echo "🚀 Setting up Flash Promos development environment with Poetry..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv is not installed. Please install pyenv first."
    echo "   Visit: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ poetry is not installed. Please install poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
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

# Set local Python version
echo "🎯 Setting local Python version..."
pyenv local $PYTHON_VERSION

# Configure Poetry
echo "🔧 Configuring Poetry..."
poetry config virtualenvs.prefer-active-python true
poetry config virtualenvs.in-project true

# Install dependencies
echo "📚 Installing dependencies..."
poetry install --with dev

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
DEBUG=1
SECRET_KEY=$(poetry run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flash_promos
REDIS_URL=redis://localhost:6379/0
EOF
    echo "✅ .env file created with random SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
poetry run pre-commit install

# Run migrations if Django is available
if poetry run python -c "import django" 2>/dev/null; then
    echo "🗄️  Running database migrations..."
    poetry run python manage.py migrate
    echo "✅ Database migrations completed"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate environment: poetry shell"
echo "   2. Start development server: poetry run python manage.py runserver"
echo "   3. Run tests: poetry run pytest"
echo "   4. Run linting: poetry run flake8 src/"
echo ""
echo "🔧 Environment info:"
echo "   Python version: $(poetry run python --version)"
echo "   Poetry version: $(poetry --version)"
echo "   Virtual env: $(poetry env info --path)"
