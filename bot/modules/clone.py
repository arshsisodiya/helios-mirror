from random import SystemRandom
from string import ascii_letters, digits
from telegram.ext import CommandHandler
from threading import Thread
from time import sleep

from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage, auto_delete_message, auto_delete_upload_message
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import bot, dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval, BOT_PM, MIRROR_LOGS, AUTO_DELETE_UPLOAD_MESSAGE_DURATION
from bot.helper.ext_utils.bot_utils import get_readable_file_size, is_gdrive_link, is_gdtot_link, new_thread, is_appdrive_link
from bot.helper.mirror_utils.download_utils.direct_link_generator import gdtot, appdrive
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from telegram import InlineKeyboardMarkup, ParseMode
from bot.helper.telegram_helper.button_build import ButtonMaker
def _clone(message, bot, multi=0):
    buttons = ButtonMaker()
    if AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1:
        reply_to = message.reply_to_message
        if reply_to is not None:
            reply_to.delete()
    if BOT_PM:
        try:
            msg1 = f'Added your Requested link to Download\n'
            send = bot.sendMessage(message.from_user.id, text=msg1)
            send.delete()
        except Exception as e:
            LOGGER.warning(e)
            bot_d = bot.get_me()
            b_uname = bot_d.username
            uname = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            botstart = f"http://t.me/{b_uname}"
            buttons.buildbutton("Click Here to Start Me", f"{botstart}")
            startwarn = f"Dear {uname},\n\n<b>I found that you haven't started me in PM (Private Chat) yet.</b>\n\nFrom now on i will give link and leeched files in PM and log channel only"
            message = sendMarkup(startwarn, bot, message, InlineKeyboardMarkup(buttons.build_menu(2)))
            Thread(target=auto_delete_message, args=(bot, message, message)).start()
            return
    args = message.text.split(" ", maxsplit=1)
    reply_to = message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1]
        if link.isdigit():
            multi = int(link)
            link = ''
        elif message.from_user.username:
            tag = f"@{message.from_user.username}"
        else:
            tag = message.from_user.mention_html(message.from_user.first_name)
    if reply_to is not None:
        if len(link) == 0:
            link = reply_to.text
        if reply_to.from_user.username:
            tag = f"@{reply_to.from_user.username}"
        else:
            tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)
    is_gdtot = is_gdtot_link(link)
    is_appdrive = is_appdrive_link(link)
    if is_gdtot:
        try:
            msg = sendMessage(f"Processing: <code>{link}</code>", bot, message)
            link = gdtot(link)
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_appdrive:
        msg = sendMessage(f"Processing: <code>{link}</code>", bot, message)
        try:
            apdict = appdrive(link)
            link = apdict.get('gdrive_link')
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_gdrive_link(link):
        gd = GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            return sendMessage(res, bot, message)
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "File/Folder is already available in Drive.\nHere are the search results:"
                return sendMarkup(msg3, bot, message, button)
        if CLONE_LIMIT is not None:
            LOGGER.info('Checking File/Folder Size...')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'Failed, Clone limit is {CLONE_LIMIT}GB.\nYour File/Folder size is {get_readable_file_size(size)}.'
                return sendMessage(msg2, bot, message)
        if multi > 1:
            sleep(4)
            nextmsg = type('nextmsg', (object, ), {'chat_id': message.chat_id, 'message_id': message.reply_to_message.message_id + 1})
            nextmsg = sendMessage(args[0], bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            multi -= 1
            sleep(4)
            Thread(target=_clone, args=(nextmsg, bot, multi)).start()
        if files <= 20:
            msg = sendMessage(f"Cloning: <code>{link}</code>", bot, message)
            result, button = gd.clone(link)
            deleteMessage(bot, msg)
        else:
            drive = GoogleDriveHelper(name)
            gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=12))
            clone_status = CloneStatus(drive, size, message, gid)
            with download_dict_lock:
                download_dict[message.message_id] = clone_status
            sendStatusMessage(message, bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        cc = f'\n\n<b>cc: </b>{tag}'
        if button in ["cancelled", ""]:
            sendMessage(f"{tag} {result}", bot, message)
        else:
            msg = sendMarkup(result + cc, bot, message, button)
            LOGGER.info(f'Cloning Done: {name}')
            Thread(target=auto_delete_upload_message, args=(bot, message, msg)).start()
        if is_gdtot:
            gd.deletefile(link)
        elif is_appdrive:
            if apdict.get('link_type') == 'login':
                LOGGER.info(f"Deleting: {link}")
                gd.deletefile(link)
        if MIRROR_LOGS:
            try:
                for chatid in MIRROR_LOGS:
                    bot.sendMessage(chat_id=chatid, text=result + cc, reply_markup=button, parse_mode=ParseMode.HTML)
            except Exception as e:
                LOGGER.warning(e)
        if BOT_PM and message.chat.type != 'private':
            try:
                bot.sendMessage(message.from_user.id, text=result, reply_markup=button,
                                parse_mode=ParseMode.HTML)
            except Exception as e:
                LOGGER.warning(e)
                return
    else:
        sendMessage('Send Gdrive or gdtot or appdrive link along with command or by replying to the link by command', bot, message)

@new_thread
def cloneNode(update, context):
    _clone(update.message, context.bot)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
