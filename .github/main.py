import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Get the Bot Token from Render Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any YouTube link, and I will download it for you!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ Please send a valid YouTube link.")
        return

    status_msg = await update.message.reply_text("⚡ Processing and downloading video on Render servers...")
    output_filename = f"{update.message.chat_id}_video.mp4"

    # yt-dlp Configuration (Downloads best quality up to 1080p for Telegram limits)
    ydl_opts = {
        'format': 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b',
        'outtmpl': output_filename,
        'quiet': True,
    }

    try:
        # Step 1: Download to Render Server
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        
        await status_msg.edit_text("📤 Uploading video to Telegram...")

        # Step 2: Send the video file back to the user
        with open(output_filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="✨ Here is your video!")
            
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: Something went wrong during extraction.")
        print(f"Error: {e}")
        
    finally:
        # Clean up the file from Render server storage
        if os.path.exists(output_filename):
            os.remove(output_filename)

def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN variable is missing!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
