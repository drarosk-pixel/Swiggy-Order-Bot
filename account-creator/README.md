# 🚀 Swiggy Account Creator Bot

A Telegram bot that automatically creates fresh Swiggy accounts without manual OTP entry.

## ✨ Features

- ✅ **Automatic account creation** - One-click account generation
- ✅ **Virtual number handling** - Uses SMS-Activate.org for OTP reception
- ✅ **No manual OTP** - Fully automated process
- ✅ **JSON export** - Export account details as JSON file
- ✅ **Mock mode** - Test without real SMS API key
- ✅ **User-friendly interface** - Simple Telegram bot interface

## 📋 Requirements

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- SMS-Activate.org API key (optional, for real accounts)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Run setup script
./setup.sh

# Edit environment file
cp .env.example .env
# Add your Telegram bot token to .env
```

### 2. Install Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Bot
```bash
python bot.py
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional (for real account creation)
SMS_ACTIVATE_API_KEY=your_api_key_here
```

### Getting SMS-Activate API Key
1. Sign up at [SMS-Activate.org](https://sms-activate.org)
2. Get API key from [API Settings](https://sms-activate.org/api2)
3. Add funds to your account (required for virtual numbers)
4. Add API key to `.env` file

## 🤖 Bot Usage

### Start the Bot
Send `/start` to your bot on Telegram.

### Create Account
1. Click "✨ Create Fresh Account" button
2. Bot will:
   - Get virtual number
   - Receive OTP automatically
   - Create account with random details
   - Show account information

### Export Account
1. After account creation, click "📄 Export JSON"
2. Bot will send JSON file with account details:
   ```json
   {
     "phone": "9876512345",
     "email": "swiggy9876512345@xyz123.com",
     "password": "P@ssw0rd123",
     "name": "Aarav Sharma",
     "activation_id": "1234567",
     "status": "active"
   }
   ```

## 🔧 Technical Details

### Components
1. **SMS Provider** (`sms_provider.py`)
   - Interfaces with SMS-Activate.org API
   - Handles virtual number acquisition
   - Automatically retrieves OTP codes
   - Mock provider for testing

2. **Account Creator** (`account_creator.py`)
   - Automates Swiggy sign-up process
   - Generates random user details
   - Handles API calls to Swiggy
   - Manages account creation flow

3. **Telegram Bot** (`bot.py`)
   - User interface
   - State management
   - File export functionality
   - Error handling

### Account Creation Flow
```
1. Get virtual number (SMS-Activate)
2. Request OTP from Swiggy
3. Wait for and receive OTP
4. Verify OTP with Swiggy
5. Generate random user details
6. Complete sign-up
7. Return account credentials
```

## ⚠️ Important Notes

### Limitations
- **OTP is still required** - Bot automates OTP reception via virtual numbers
- **SMS service costs money** - Virtual numbers require paid SMS service
- **Swiggy API changes** - Endpoints may change without notice
- **Rate limiting** - Too many accounts may trigger rate limits

### Legal Disclaimer
⚠️ **This bot is for educational purposes only.**

- Creating multiple fake accounts violates Swiggy's Terms of Service
- Use responsibly and at your own risk
- The authors are not responsible for any misuse
- Always comply with applicable laws and terms of service

### Mock Mode
Without `SMS_ACTIVATE_API_KEY`, the bot runs in mock mode:
- Generates fake phone numbers
- Uses dummy OTP codes (123456)
- Creates accounts with test data
- Useful for testing bot functionality

## 🐛 Troubleshooting

### Common Issues
1. **"No numbers available"**
   - Check SMS-Activate balance
   - Try different country code
   - Service may be temporarily unavailable

2. **"Account creation failed"**
   - Swiggy API may have changed
   - Check internet connection
   - Try with mock mode first

3. **Bot not responding**
   - Check Telegram bot token
   - Verify Python dependencies
   - Check internet connection

### Debugging
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Project Structure
```
swiggy-account-creator/
├── bot.py                 # Telegram bot main file
├── account_creator.py     # Swiggy account automation
├── sms_provider.py       # SMS service interface
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── setup.sh            # Setup script
└── README.md           # This file
```

## 🔄 Updates & Maintenance

### Updating Endpoints
If Swiggy changes their API:
1. Monitor network traffic on Swiggy sign-up page
2. Update endpoints in `account_creator.py`
3. Test with mock mode first

### Adding Features
Common feature requests:
- Multiple account creation
- Account management dashboard
- Scheduled account creation
- Proxy support
- Different SMS providers

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review code comments
3. Open GitHub issue (if public repo)
4. Contact developer (if private)

## 📄 License

MIT License - See LICENSE file for details.

---

**Remember:** Use this tool responsibly and ethically. Automation should not be used for malicious purposes.