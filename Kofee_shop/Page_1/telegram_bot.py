from telegram import Bot
from django.core.mail import send_mail
from Kofee_shop import settings


TG_TOKEN = "986558864:AAHJPC7FOFosKl88BfKaqgAgHGoZr1tGllA"
CHAT_ID = '824438148'

def send_telegram_notification(text_message):
    bot = Bot(token=TG_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text_message)
  
    
def send_email_notification(text):
    subject = 'New Order'
    message = text
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['zzzorgjb@gmail.com']
    send_mail( subject, message, email_from, recipient_list )



