import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

# Load Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Example: "@your_channel"
UPI_ID = os.getenv("UPI_ID")

bot = telebot.TeleBot(BOT_TOKEN)

# Notify Channel that Bot is Online (ONE TIME ONLY)
bot.send_message(CHANNEL_ID, "Hey, I'm Telbot 🤖✨—Your Trusted One-Stop Solution for CVs 📄 | Art 🎨 | Logos 🔥! 🚀💼 Let’s create something amazing for you!")


# Function to generate the main menu as an inline keyboard
def generate_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🖌️ AI Art", callback_data="menu_ai_art"),
        InlineKeyboardButton("📄 CV Creation", callback_data="menu_cv"),
        InlineKeyboardButton("🔥 Logo Design", callback_data="menu_logo")
    )
    return markup

# Start command - Sends "Start Now" button (ONE TIME PER USER)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Start Now", callback_data="start_now"))
    bot.send_message(message.chat.id, "Hey, I'm Telbot 🤖✨—Your Trusted One-Stop Solution for CVs 📄 | Art 🎨 | Logos 🔥! 🚀💼 Let’s create something amazing for you!", reply_markup=markup)

# "Start Now" button - Bot sends main menu privately
@bot.callback_query_handler(func=lambda call: call.data == "start_now")
def start_now(call):
    bot.send_message(
        call.message.chat.id,
        "Hello! Welcome to AlphaZone ⚡\nWhat do you need today?",
        reply_markup=generate_main_menu()
    )

# Handling menu selections
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def show_samples(call):
    if call.data == "menu_ai_art":
        samples_text = "✨ **AI Art Samples** ✨\n\n1️⃣ **Artistic** - ₹3,000\n2️⃣ **Fantasy** - ₹4,500\n3️⃣ **Ultra-Realistic** - ₹12,000\n\nSelect a type:"
        sample_type = "ai_art"
    elif call.data == "menu_cv":
        samples_text = "📄 **CV Samples** 📄\n\n1️⃣ **Professional CV** (50% Acceptance) - ₹2,500\n2️⃣ **Executive CV** (99% Acceptance) - ₹4,500\n\nSelect a type:"
        sample_type = "cv"
    elif call.data == "menu_logo":
        samples_text = "🔥 **Logo Design** 🔥\nPrice: ₹2,000\n\nClick below to continue:"
        sample_type = "logo"

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Choose", callback_data=f"choose_{sample_type}")
    )
    bot.send_message(call.message.chat.id, samples_text, reply_markup=markup)

# After selecting an option, show watermarked preview
@bot.callback_query_handler(func=lambda call: call.data.startswith("choose_"))
def show_preview(call):
    product_type = call.data.split("_")[1]
    preview_text = f"🖼️ Here is your **{product_type.replace('_', ' ').title()}** preview (Watermarked).\nClick below to proceed."

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔄 Regenerate", callback_data=f"regenerate_{product_type}"),
        InlineKeyboardButton("✅ Done", callback_data=f"done_{product_type}")
    )
    bot.send_message(call.message.chat.id, preview_text, reply_markup=markup)

# Handle "Regenerate" - Generate a new sample
@bot.callback_query_handler(func=lambda call: call.data.startswith("regenerate_"))
def regenerate_preview(call):
    product_type = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, f"🔄 Generating a new **{product_type.title()}** sample...")

    show_preview(call)  # Resend preview with new sample

# Handle "Done" - Ask for payment
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def ask_payment(call):
    product_type = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, f"✅ Great! To proceed, please send a payment screenshot.\n\n💳 **UPI ID**: `{UPI_ID}`")

# Handling payment screenshots
@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, "📥 Payment received! Delivering your product now...")

    # Save transaction details
    transaction_data = {
        "user_id": message.chat.id,
        "file_id": file_id
    }
    save_transaction(transaction_data)

    bot.send_message(message.chat.id, "🎉 Your product has been delivered! Thank you.")

# Function to store transactions in JSON
def save_transaction(data):
    file_path = "transactions.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            transactions = json.load(file)
    else:
        transactions = []

    transactions.append(data)

    with open(file_path, "w") as file:
        json.dump(transactions, file, indent=4)

# Run the bot
bot.polling()
