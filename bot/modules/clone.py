from random import SystemRandom
from string import ascii_letters, digits
from telegram.ext import CommandHandler
from threading import Thread
from time import sleep
from bot import bot, dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval, BOT_PM, \
                MIRROR_LOGS, FSUB, FSUB_CHANNEL_ID, CHANNEL_USERNAME, TITLE_NAME
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot.helper.ext_utils.bot_utils import get_readable_file_size, is_gdrive_link, is_gdtot_link, new_thread, is_appdrive_link
from bot.helper.mirror_utils.download_utils.direct_link_generator import gdtot, appdrive
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from telegram import InlineKeyboardMarkup, ParseMode
from bot.helper.telegram_helper.button_build import ButtonMaker

def _clone(message, bot, multi=0):
    buttons = ButtonMaker()

    if FSUB:
        try:
            uname = message.from_user.mention_html(message.from_user.first_name)
            user = bot.get_chat_member(FSUB_CHANNEL_ID, message.from_user.id)
            if user.status not in ['member', 'creator', 'administrator']:
                buttons.buildbutton(f"{TITLE_NAME}", f"https://t.me/{CHANNEL_USERNAME}")
                reply_markup = InlineKeyboardMarkup(buttons.build_menu(1))
                return sendMarkup(f"<b>Dear {uname}️,\n\nI found that you haven't joined our Updates Channel yet.\n\nJoin and Use Bots Without Restrictions.</b>", bot, message, reply_markup)
        except Exception as e:
            LOGGER.info(str(e))

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
            buttons.buildbutton("➦Click Here to Start Me", f"{botstart}")
            startwarn = f"Dear {uname},\n\n<b>I found that you haven't started me in PM (Private Chat) yet.</b>\n\nFrom now on i will give link and leeched files in PM and log channel only"
            message = sendMarkup(startwarn, bot, message, InlineKeyboardMarkup(buttons.build_menu(2)))
            return

    args = message.text.split()
    reply_to = message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1].strip()
        if link.strip().isdigit():
            multi = int(link)
            link = ''
        elif message.from_user.username:
            tag = f"@{message.from_user.username}"
        else:
            tag = message.from_user.mention_html(message.from_user.first_name)
    if reply_to:
        if len(link) == 0:
            link = reply_to.text.split(maxsplit=1)[0].strip()
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
            LOGGER.info(f"Processing GdToT Link: {link}")
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_appdrive:
        msg = sendMessage(f"Processing: <code>{link}</code>", bot, message)
        try:
            apdict = appdrive(link)
            link = apdict.get('gdrive_link')
            LOGGER.info(f"Processing AppDrive Link: {link}")
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
                msg3 = "➦ Already available !\n➦ Drive you go:"
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
        cc = f'\n\n<b>➦ User </b>{tag}<b> ➦ Your file successfully...</b>\n\n<b>➦ Repo-By ✤ <i>{TITLE_NAME}</i></b>'
        if button in ["cancelled", ""]:
            sendMessage(f"{tag} {result}", bot, message)
        else:
            sendMarkup(result + cc, bot, message, button)
            LOGGER.info(f'Cloning Done: {name}')
        if (is_gdtot or is_appdrive):
            gd.deletefile(link)
    else:
        sendMessage('Send Gdrive or GDToT/AppDrive/DriveApp link along with command or by replying to the link by command', bot, message)

@new_thread
def cloneNode(update, context):
    _clone(update.message, context.bot)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)