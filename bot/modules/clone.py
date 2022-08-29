from random import SystemRandom
from string import ascii_letters, digits
from telegram.ext import CommandHandler
from threading import Thread
from time import sleep

from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage, sendMarkup, auto_delete_message, auto_delete_upload_message
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import bot, dispatcher, LOGGER, STOP_DUPLICATE, download_dict, download_dict_lock, Interval, MIRROR_LOGS, BOT_PM, AUTO_DELETE_UPLOAD_MESSAGE_DURATION, CLONE_LIMIT, FORCE_BOT_PM
from bot.helper.ext_utils.bot_utils import is_gdrive_link, new_thread, is_appdrive_link, is_gdtot_link, get_readable_file_size
from bot.helper.mirror_utils.download_utils.direct_link_generator import appdrive, gdtot
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.button_build import ButtonMaker
def _clone(message, bot):
    buttons = ButtonMaker()
    if AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1:
        reply_to = message.reply_to_message
        if reply_to is not None:
            reply_to.delete()
    if BOT_PM and message.chat.type != 'private':
        try:
            msg1 = f'Added your Requested link to Download\n'
            send = bot.sendMessage(message.from_user.id, text=msg1)
            send.delete()
        except Exception as e:
            LOGGER.warning(e)
            bot_d = bot.get_me()
            b_uname = bot_d.username
            uname = message.from_user.mention_html(message.from_user.first_name)
            botstart = f"http://t.me/{b_uname}"
            buttons.buildbutton("Click Here to Start Me", f"{botstart}")
            startwarn = f"<b>Dear {uname}, Start me in PM to use me.</b>"
            mesg = sendMarkup(startwarn, bot, message, buttons.build_menu(2))
            sleep(15)
            mesg.delete()
            message.delete()
            return
    args = message.text.split()
    reply_to = message.reply_to_message
    link = ''
    multi=1
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
    is_appdrive = is_appdrive_link(link)
    is_gdtot = is_gdtot_link(link)
    if is_appdrive:
        msg = sendMessage(f"Processing: <code>{link}</code>", bot, message)
        try:
            link = appdrive(link)
            deleteMessage(bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(bot, msg)
            return sendMessage(str(e), bot, message)
    if is_gdtot:
        try:
            msg = sendMessage(f"Processing: <code>{link}</code>", bot, message)
            link = gdtot(link)
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
            nextmsg = sendMessage(message.text.replace(str(multi), str(multi - 1), 1), bot, nextmsg)
            nextmsg.from_user.id = message.from_user.id
            sleep(4)
            Thread(target=_clone, args=(nextmsg, bot)).start()
        if files <= 20:
            msg = sendMessage(f"Cloning: <code>{link}</code>", bot, message)
            result, button = gd.clone(link)
            deleteMessage(bot, msg)
            if BOT_PM and FORCE_BOT_PM:
                botpm = f"\n\n<b>Hey {tag}!, I have sent your cloned links in PM.</b>\n"
                buttons = ButtonMaker()
                b_uname = bot.get_me().username
                botstart = f"http://t.me/{b_uname}"
                buttons.buildbutton("View links in PM", f"{botstart}")
                sendMarkup(result + botpm, bot, message, buttons.build_menu(2))
                message.delete()
                reply_to = message.reply_to_message
                if reply_to is not None and AUTO_DELETE_UPLOAD_MESSAGE_DURATION == -1:
                    reply_to.delete()


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
                    if BOT_PM and FORCE_BOT_PM:
                        botpm = f"\n\n<b>Hey {tag}!, I have sent your cloned links in PM.</b>\n"
                        buttons = ButtonMaker()
                        b_uname = bot.get_me().username
                        botstart = f"http://t.me/{b_uname}"
                        buttons.buildbutton("View links in PM", f"{botstart}")
                        sendMarkup(result + botpm, bot, message, buttons.build_menu(2))
                        message.delete()
                        reply_to = message.reply_to_message
                        if reply_to is not None and AUTO_DELETE_UPLOAD_MESSAGE_DURATION == -1:
                            reply_to.delete()

                else:
                    update_all_messages()
            except IndexError:
                pass
        cc = f'\n\n<b>cc: </b>{tag}'
        if button in ["cancelled", ""]:
            sendMessage(f"{tag} {result}", bot, message)
        else:
            LOGGER.info(f'Cloning Done: {name}')
            if FORCE_BOT_PM is False:
                upldmsg = sendMarkup(result + cc, bot, message, button)
                Thread(target=auto_delete_upload_message, args=(bot, message, upldmsg)).start()
        if is_gdtot:
            LOGGER.info(f"Deleting: {link}")
            gd.deletefile(link)
        elif is_appdrive:
            LOGGER.info(f"Deleting: {link}")
            gd.deletefile(link)
        if MIRROR_LOGS:
            try:
                for chatid in MIRROR_LOGS:
                    bot.sendMessage(chat_id=chatid, text=result + cc, reply_markup=button, parse_mode='HTML')
            except Exception as e:
                LOGGER.warning(e)
        if BOT_PM and message.chat.type != 'private':
            try:
                bot.sendMessage(message.from_user.id, text=result + cc, reply_markup=button, parse_mode='HTML')
            except Exception as e:
                LOGGER.warning(e)
                return
    else:
        sendMessage("Send Gdrive or Gdtot or Appdrive link along with command or by replying to the link by command\n\n<b>Multi links only by replying to first link/file:</b>\n<code>/cmd</code> 10(number of links/files)", bot, message)

@new_thread
def cloneNode(update, context):
    _clone(update.message, context.bot)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
