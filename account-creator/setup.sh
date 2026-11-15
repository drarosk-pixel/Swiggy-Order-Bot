#!/bin/bash

echo "🚀 Setting up Swiggy Account Creator Bot..."
echo "============================================"

# Create virtual environment
echo "1. Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "2. Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "3. Creating .env file from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env file with your Telegram bot token"
    echo "   ⚠️  For real accounts, add SMS_ACTIVATE_API_KEY"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file:"
echo "   - Add TELEGRAM_BOT_TOKEN (from @BotFather)"
echo "   - Add SMS_ACTIVATE_API_KEY (optional, for real numbers)"
echo ""
echo "2. Run the bot:"
echo "   source venv/bin/activate"
echo "   python bot.py"
echo ""
echo "ℹ️  Note: Without SMS_ACTIVATE_API_KEY, bot uses mock provider"
echo "   (generates fake numbers/OTPs for testing)"