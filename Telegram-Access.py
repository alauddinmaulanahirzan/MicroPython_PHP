# Firebase Section
from FirebaseHandler import FirebaseHandler
# Telegram Bot Section
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Additional Section
from datetime import datetime
import csv
import time
import os

# Logging Config
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hyper Parameters
ref = None
chat_id = None

# Millis
def current_milli_time():
    return round(time.time() * 1000)

# --- Firebase Code --- #
def connectFirebase():
    print("==> Connecting to Firebase",end="",flush=True)
    ref = FirebaseHandler.connectDB() # Connect Once
    print(" > [CONNECTED]")
    return ref

# --- Telegram Bot Code --- #
def start(update: Update, context: CallbackContext) -> None:
    global chat_id
    chat_id = update.effective_chat.id
    start_mil = current_milli_time()
    message = ">> ===========================================\n"
    message += ">> Bot : Pemantauan Kolam Ikan Arwana\n"
    message += ">> Bot : Perintah Tersedia :\n"
    message += ">> ===========================================\n"
    message += "1. /check_valid | Cek Validitas Blok\n"
    message += "2. /ph_statistic | Cek Statistika PH\n"
    message += "3. /retrieve_data | Unduh Data Dalam CSV\n"
    message += ">> ===========================================\n"
    message += "x. Bot Secara Otomatis Cek Error 30 Menit Terakhir\n"
    message += ">> ===========================================\n"
    message += f">> {chat_id} Terdaftar Program Otomatis\n"
    message += ">> ===========================================\n"
    end_mil = current_milli_time()
    message += f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyBlocks(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Memerika Validitas Blockchain"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total_blocks = 0
    valid = 0
    invalid = 0
    curHash = None
    # Fetch Machine
    db = ref.child("Device").get()
    if(db is not None):
        # Iterate per Machine
        for block in db.keys():
            block_data = db[block]
            total_blocks += 1
            # Compare Data
            previous = block_data["01-Previous"]
            hash = block_data["05-Hash"]
            if(previous == "None" and total_blocks == 1):
                valid += 1
            else:
                if(curHash == previous):
                    valid += 1
                else:
                    invalid += 1
            curHash = hash

        message = f">> Bot : Menemukan {total_blocks} blok\n"
        message += f"==>> Blok Valid : {valid}\n"
        message += f"==>> Blok Invalid : {invalid}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Database Kosong"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetPHStatistic(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Memerika Statistika PH Terpantau\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    average_ph, average_volt = 0,0
    min_ph,min_volt = 15,6 # Intended Value (Max Value PH 14 and 5V)
    max_ph,max_volt = 0,0
    sample_ph,sample_volt = 0,0
    total_blocks = 0
    db = ref.child("Device").get()
    # Iterate per Machine
    if(db is not None):
        for block in db.keys():
            block_data = db[block]
            total_blocks += 1
            # Get Data
            ph = float(block_data["02-PH"])
            volt = float(block_data["03-Volt"])
            sample_ph += ph
            sample_volt += volt
            # Find Min PH
            if(ph < min_ph):
                min_ph = ph
            # Find Max PH
            if(ph > max_ph):
                max_ph = ph
            # Find Min Volt
            if(volt < min_volt):
                min_volt = volt
            # Find Max Volt
            if(volt > min_volt):
                max_volt = volt
            
        # Get Average
        average_ph = sample_ph/total_blocks
        average_volt = sample_volt/total_blocks

        message = f">> Bot : Menemukan {total_blocks} blok\n"
        message += f"==> PH Terendah : {min_ph}\n"
        message += f"==> PH Tertinggi : {max_ph}\n"
        message += f"====>> Rerata PH : {average_ph}\n"
        message += f"==> Voltase Terendah : {min_volt}\n"
        message += f"==> Voltase Tertinggi : {max_volt}\n"
        message += f"====>> Rerata Voltase : {average_volt}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Database Kosong"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botExportData(update: Update, context: CallbackContext) -> None:
    total_blocks = 0
    start_mil = current_milli_time()
    message = f">> Bot: Ekspor Data Dilakukan"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    db = ref.child("Device").get()
    if(db is not None):
        data_rows = []
        for block in db.keys():
            total_blocks += 1
            block_data = db[block]
            # Insert into Row
            row = []
            row.append(total_blocks)
            row.append(block)
            row.append(block_data["01-Previous"])
            row.append(block_data["02-PH"])
            row.append(block_data["03-Volt"])
            row.append(block_data["04-Datetime"])
            row.append(block_data["05-Hash"])
            data_rows.append(row)

        # Write to CSV
        message = f">> Bot : Menyimpan Data di file"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        filename = "exported_data.csv"
        if os.path.isfile(filename):
            os.remove(filename)
        # Set Header CSV
        header = ["No","BlockID","Previous","PH","Volt","Datetime","Hash"]
        with open(filename,"w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for input_row in data_rows:
                writer.writerow(input_row)
        message = f">> Bot : File sudah tersimpan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Database Kosong"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botAutoCheckInterrupt(context: CallbackContext) -> None:
    if(chat_id is not None):
        start_mil = current_milli_time()
        interrupted_blocks = 0
        interrupted_list = []
        curHash = None
        total_blocks = 0
        message = f">> Bot: Pengecekan Otomatis Berjalan\n"
        # Cek Data
        db = ref.child("Device").get()
        if(db is not None):
            for block in db.keys():
                total_blocks += 1
                block_data = db[block]
                # Compare Data
                previous = block_data["01-Previous"]
                hash = block_data["05-Hash"]
                if(previous == "None" and total_blocks == 1):
                    pass # Ignore
                else:
                    if(curHash == previous):
                        pass # Ignore
                    else:
                        block_data_datetime = block_data["04-Datetime"]
                        interrupted_blocks += 1
                        interrupted_list.append(block+" saat "+block_data_datetime)
                curHash = hash

            interrupted_list = interrupted_list[-3:]
            message += f">> Bot : Menemukan {interrupted_blocks} interupsi dari {total_blocks} blok\n"
            for interrupt in interrupted_list:
                message += f"==>> Interupsi {interrupt}\n"
            end_mil = current_milli_time()
            message += f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
            context.bot.send_message(chat_id=chat_id, text=message)
        
        if(interrupted_blocks == 0):
            end_mil = current_milli_time()
            message = f">> ==>> []\nBot : Selesai ({(end_mil-start_mil)/1000}s)"
            context.bot.send_message(chat_id=chat_id, text=message)

# --- Main Code --- #
def main():
    global ref,bucket
    ref = connectFirebase()
    updater = Updater(token="1901469256:AAHz0864vwPsAS6HWu68GZ4uoQ8k_FS0YU8",request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
    dispatcher = updater.dispatcher
    jq = updater.job_queue
    # Perintah
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check_valid", botVerifyBlocks))
    dispatcher.add_handler(CommandHandler("ph_statistic", botGetPHStatistic))
    dispatcher.add_handler(CommandHandler("retrieve_data", botExportData))
    jq.run_repeating(botAutoCheckInterrupt,interval=60)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()