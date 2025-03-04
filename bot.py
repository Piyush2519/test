import logging
import gspread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ✅ Define Telegram Bot Token (Replace with your actual bot token)
TOKEN = "7617606700:AAGr17iUe2Noxkqza4b7WhXO15JyiT3APfQ"

# ✅ Google Sheets Authentication
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("your-google-credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)

# ✅ Open Google Sheet
SHEET_ID = "1hzhaoPaVjHkQY0Xqa8_JFFWrsIvglAXkH8IHkFDY0oU"  # Replace with actual Google Sheet ID
SHEET_NAME = "Sheet1"  # Make sure this sheet exists
sheet = CLIENT.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /check <Beam No.> to see details.")

# ✅ Check Beam Details Command
async def check_beam(update: Update, context: CallbackContext):
    """Fetch beam details from Google Sheets"""
    try:
        command_parts = update.message.text.split()
        if len(command_parts) < 2:
            await update.message.reply_text("Please provide a beam number. Example: /check 1")
            return

        beam_no = command_parts[1]  # Get beam number from user input
        data = sheet.get_all_records()

        for row in data:
            if str(row.get("Beam No.")) == beam_no:
                message = (f"Beam {beam_no} Details:\n"
                           f"Bottom Steel: {row.get('Bottom Steel', 'N/A')}\n"
                           f"Top Steel: {row.get('Top Steel', 'N/A')}\n"
                           f"Curtal Bar: {row.get('Curtal Bar', 'N/A')}")
                await update.message.reply_text(message)
                return

        await update.message.reply_text(f"Beam {beam_no} not found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ✅ Update Beam Details Command
async def update_beam(update: Update, context: CallbackContext):
    """Update beam details in Google Sheets"""
    try:
        command_parts = update.message.text.split(":", 1)
        if len(command_parts) < 2:
            await update.message.reply_text("Use format: /update <Beam No.>: <Field> - <Value>")
            return

        beam_no, update_data = command_parts[0].split()[1], command_parts[1]
        field_name, field_value = [x.strip() for x in update_data.split("-", 1)]

        # Locate the row containing the beam number
        data = sheet.get_all_records()
        row_num = None

        for i, row in enumerate(data, start=2):  # Data starts from row 2
            if str(row.get("Beam No.")) == beam_no:
                row_num = i
                break

        if row_num:
            # Define column mapping
            col_map = {"Bottom Steel": 2, "Top Steel": 3, "Curtal Bar": 4}
            col_num = col_map.get(field_name)

            if col_num:
                sheet.update_cell(row_num, col_num, field_value)
                await update.message.reply_text(f"Updated Beam {beam_no}: {field_name} - {field_value}")
            else:
                await update.message.reply_text("Invalid field. Use 'Bottom Steel', 'Top Steel', or 'Curtal Bar'.")
        else:
            await update.message.reply_text(f"Beam {beam_no} not found.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ✅ Main Function
def main():
    """Main function to run the bot"""
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_beam))
    app.add_handler(CommandHandler("update", update_beam))

    # Run the bot
    app.run_polling()

# ✅ Run the bot
if __name__ == "__main__":
    main()
