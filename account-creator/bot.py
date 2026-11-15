import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import tempfile

from sms_provider import SMSActivateProvider, MockSMSProvider
from account_creator import SwiggyAccountCreator

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in .env file")

bot = telebot.TeleBot(BOT_TOKEN)

# Initialize SMS provider
SMS_API_KEY = os.getenv("SMS_ACTIVATE_API_KEY")

if SMS_API_KEY and SMS_API_KEY != "your_api_key_here":
    sms_provider = SMSActivateProvider(SMS_API_KEY)
    logger.info("Using real SMS-Activate provider")
else:
    sms_provider = MockSMSProvider()
    logger.info("Using mock SMS provider (for testing)")

# Initialize account creator
account_creator = SwiggyAccountCreator(sms_provider)

# User states and data
user_sessions = {}  # user_id -> {"state": "...", "data": {...}}

def get_user_session(user_id: int) -> Dict[str, Any]:
    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "idle", "data": {}}
    return user_sessions[user_id]

def set_user_state(user_id: int, state: str, data: Dict[str, Any] = None):
    if data is None:
        data = {}
    user_sessions[user_id] = {"state": state, "data": data}

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    set_user_state(user_id, "idle")
    
    welcome_text = """
    🚀 *Welcome to Swiggy Account Creator Bot* 🚀

    I can automatically create fresh Swiggy accounts for you!

    *Features:*
    ✅ Automatic account creation
    ✅ Virtual number handling
    ✅ No manual OTP required
    ✅ JSON export of account details

    Click the button below to get started!
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✨ Create Fresh Account", callback_data="create_account"))
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "create_account")
def handle_create_account(call):
    user_id = call.from_user.id
    set_user_state(user_id, "creating_account")
    
    bot.edit_message_text(
        "🔄 *Creating your Swiggy account...*\n\n"
        "This may take 1-2 minutes. Please wait...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    
    # Start account creation in background
    import threading
    
    def create_account_thread():
        try:
            account = account_creator.create_account()
            
            if account:
                # Save account to user session
                session = get_user_session(user_id)
                session["data"]["last_account"] = account
                session["state"] = "account_created"
                
                # Format account details for display
                details = f"""
✅ *Account Created Successfully!*

📱 *Phone:* `{account['phone']}`
📧 *Email:* `{account['email']}`
🔑 *Password:* `{account['password']}`
👤 *Name:* {account['name']}

Account is ready to use!
                """
                
                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton("📄 Export JSON", callback_data="export_json"),
                    InlineKeyboardButton("🔄 Create Another", callback_data="create_account")
                )
                
                bot.edit_message_text(
                    details,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                
            else:
                # Check what type of provider we're using
                if SMS_API_KEY and SMS_API_KEY != "your_api_key_here" and SMS_API_KEY != "MOCK_MODE":
                    error_msg = """
❌ *Account Creation Failed (Real SMS Mode)*

Possible reasons:
• No virtual numbers available for India
• Insufficient balance on SMS-Activate
• Swiggy API endpoints changed
• Service 'sw' not available (try 'ot')

*Fix:*
1. Check SMS-Activate balance
2. Try different country code
3. Update API endpoints
4. Contact SMS provider support
                    """
                else:
                    error_msg = """
❌ *Account Creation Failed (Mock Mode)*

Bot is running in MOCK_MODE (fake OTP).
For real account creation:

1. Get SMS-Activate API key:
   https://sms-activate.org/api2
   
2. Add funds to your account
   
3. Update .env file:
   SMS_ACTIVATE_API_KEY=your_real_key_here
   
4. Restart bot

*Note:* Mock mode only works for testing.
                    """
                
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("🔄 Try Again", callback_data="create_account"))
                
                bot.edit_message_text(
                    error_msg,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"Account creation error: {e}")
            
            bot.edit_message_text(
                f"❌ *Error:* `{str(e)}`\n\nPlease try again.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
    
    # Start thread
    thread = threading.Thread(target=create_account_thread)
    thread.start()

@bot.callback_query_handler(func=lambda call: call.data == "export_json")
def handle_export_json(call):
    user_id = call.from_user.id
    session = get_user_session(user_id)
    
    if "last_account" not in session["data"]:
        bot.answer_callback_query(call.id, "No account data to export")
        return
    
    account = session["data"]["last_account"]
    
    # Create JSON file
    json_data = json.dumps(account, indent=2, ensure_ascii=False)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_data)
        temp_file = f.name
    
    try:
        # Send file
        with open(temp_file, 'rb') as f:
            bot.send_document(
                call.message.chat.id,
                f,
                caption=f"📄 *Swiggy Account Details*\n\n"
                       f"Phone: `{account['phone']}`\n"
                       f"Email: `{account['email']}`",
                parse_mode="Markdown"
            )
        
        bot.answer_callback_query(call.id, "JSON file sent!")
        
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        bot.answer_callback_query(call.id, "Error sending file")
    
    finally:
        # Clean up temp file
        import os
        if os.path.exists(temp_file):
            os.unlink(temp_file)

@bot.callback_query_handler(func=lambda call: call.data == "create_multiple")
def handle_create_multiple(call):
    # Placeholder for multiple account creation
    bot.answer_callback_query(call.id, "Feature coming soon!")
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✨ Create Single Account", callback_data="create_account"))
    
    bot.edit_message_text(
        "📊 *Multiple Account Creation*\n\n"
        "This feature will allow creating multiple accounts at once.\n"
        "Currently available: Single account creation.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🤖 *Swiggy Account Creator Bot Help*

*Commands:*
/start - Start the bot
/help - Show this help message
/stats - Show bot statistics (coming soon)

*How it works:*
1. Click "Create Fresh Account"
2. Bot gets virtual number
3. Automatically receives OTP
4. Creates account with random details
5. Export JSON with account info

*Requirements:*
• SMS-Activate.org API key (optional, for real numbers)
• Telegram bot token

*Setup:*
1. Get SMS-Activate API key (optional)
2. Add to .env file:
   SMS_ACTIVATE_API_KEY=your_key_here
3. Bot will use mock provider if no key

*Note:* This is for educational purposes only.
    """
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    stats_text = """
📊 *Bot Statistics*

*Current Status:* Active
*Provider:* SMS-Activate.org (Mock mode)
*Accounts Created:* Not tracked
*Last Activity:* Now

*Note:* Statistics tracking coming in next update.
    """
    
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(
        message.chat.id,
        "I don't understand that command. Use /start to begin or /help for assistance."
    )

def main():
    logger.info("Starting Swiggy Account Creator Bot...")
    
    # Check if using mock provider
    if isinstance(sms_provider, MockSMSProvider):
        logger.warning("⚠️ Using MOCK SMS provider. For real accounts, set SMS_ACTIVATE_API_KEY in .env")
    
    bot.infinity_polling()

if __name__ == "__main__":
    main()