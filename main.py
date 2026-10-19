import datetime import logging
import pytz from telegram import Update from telegram.ext import ( Application, CommandHandler, ContextTypes, MessageHandler, filters, )
logging.basicConfig( format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, )
TIMEZONE = pytz.timezone("Asia/Tashkent")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): welcome_text = ( "Assalomu alaykum! Men sizning shaxsiy eslatuvchi botingizman. ⏰\n\n" "Eslatma o'rnatish uchun buyruqlar:\n" "1. /set HH:MM Matn - Vaqtga eslatma (masalan: /set 18:30 Bozorga borish)\n" "2. /in daqiqa Matn - Bir necha daqiqadan keyinga (masalan: /in 15 Choyni o'chirish)\n" "3. /list - Barcha faol eslatmalarni ko'rish" ) await update.message.reply_text(welcome_text, parse_mode="Markdown")
async def alarm(context: ContextTypes.DEFAULT_TYPE): job = context.job await context.bot.send_message( chat_id=job.chat_id, text=f"🔔 ESLATMA!\n\n📌 {job.data}", parse_mode="Markdown", )
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE): chat_id = update.effective_message.chat_id try: time_str = context.args[0] text = " ".join(context.args[1:]) if len(context.args) > 1 else "Eslatma!"
    now = datetime.datetime.now(TIMEZONE)
    target_time = datetime.datetime.strptime(time_str, "%H:%M").time()

    run_date = datetime.datetime.combine(
        now.date(), target_time, tzinfo=TIMEZONE
    )

    if run_date <= now:
        run_date += datetime.timedelta(days=1)

    job_name = f"{chat_id}_{run_date.strftime('%Y%m%d%H%M')}"

    context.job_queue.run_once(
        alarm, run_date, chat_id=chat_id, name=job_name, data=text
    )

    await update.message.reply_text(
        f"✅ **Eslatma o'rnatildi!**\n\n⏰ Vaqti: `{run_date.strftime('%Y-%m-%d %H:%M')}`\n📌 Matn: {text}",
        parse_mode="Markdown",
    )

except (IndexError, ValueError):
    await update.message.reply_text(
        "❌ **Xatolik!** Tog'ri formatda yozing:\n`/set 14:30 Majlis bor`",
        parse_mode="Markdown",
    )
async def set_in_minutes(update: Update, context: ContextTypes.DEFAULT_TYPE): chat_id = update.effective_message.chat_id try: minutes = int(context.args[0]) text = " ".join(context.args[1:]) if len(context.args) > 1 else "Eslatma!"
    context.job_queue.run_once(
        alarm, minutes * 60, chat_id=chat_id, data=text
    )

    await update.message.reply_text(
        f"✅ **Eslatma o'rnatildi!**\n\n⏰ {minutes} daqiqadan keyin sizga xabar yuboraman.",
        parse_mode="Markdown",
    )

except (IndexError, ValueError):
    await update.message.reply_text(
        "❌ Xatolik! Tog'ri formatda yozing:\n`/in 10 Suv ichish`",
        parse_mode="Markdown",
    )
async def list_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE): current_jobs = context.job_queue.jobs() if not current_jobs: await update.message.reply_text("Hozircha hech qanday faol eslatma yo'q.") return
text = "📋 **Faol eslatmalaringiz:**\n\n"
for idx, job in enumerate(current_jobs, start=1):
    next_t = job.next_t.astimezone(TIMEZONE).strftime("%H:%M (%d-%b)")
    text += f"{idx}. ⏰ {next_t} — {job.data}\n"

await update.message.reply_text(text, parse_mode="Markdown")
def main(): # SHU YERGA TOKENINGIZNI YOZING TOKEN = "8654890400:AAGkKDuDRJYGxOn2PVlolZaurdDV9CZYmug"
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("set", set_timer))
app.add_handler(CommandHandler("in", set_in_minutes))
app.add_handler(CommandHandler("list", list_jobs))

print("Bot ishga tushdi...")
app.run_polling()
if name == "main": main()
