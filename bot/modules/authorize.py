from bot import AUTHORIZED_CHATS, SUDO_USERS, dispatcher, DB_URI, LEECH_LOG
from bot.helper.telegram_helper.message_utils import sendMessage
from telegram.ext import CommandHandler
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.db_handler import DbManger


def authorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            msg = 'User Already Authorized!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            msg = 'User Authorized'
    elif reply_message is None:
        # Trying to authorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            msg = 'Chat Already Authorized!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(chat_id)
            AUTHORIZED_CHATS.add(chat_id)
        else:
            AUTHORIZED_CHATS.add(chat_id)
            msg = 'Chat Authorized'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            msg = 'User Already Authorized!'
        elif DB_URI is not None:
            msg = DbManger().user_auth(user_id)
            AUTHORIZED_CHATS.add(user_id)
        else:
            AUTHORIZED_CHATS.add(user_id)
            msg = 'User Authorized'
    sendMessage(msg, context.bot, update.message)

def unauthorize(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = 'User Unauthorized'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = 'User Already Unauthorized!'
    elif reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(chat_id)
            else:
                msg = 'Chat Unauthorized'
            AUTHORIZED_CHATS.remove(chat_id)
        else:
            msg = 'Chat Already Unauthorized!'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in AUTHORIZED_CHATS:
            if DB_URI is not None:
                msg = DbManger().user_unauth(user_id)
            else:
                msg = 'User Unauthorized'
            AUTHORIZED_CHATS.remove(user_id)
        else:
            msg = 'User Already Unauthorized!'
    sendMessage(msg, context.bot, update.message)

def addleechlog(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in LEECH_LOG:
            msg = 'User Already in Leech Log!'
        elif DB_URI is not None:
            msg = DbManger().addleech_log(user_id)
            LEECH_LOG.add(user_id)
        else:
            LEECH_LOG.add(user_id)
            msg = 'User Added in Leech Logs'
    elif reply_message is None:
        # Trying to authorize a chat
        chat_id = update.effective_chat.id
        if chat_id in LEECH_LOG:
            msg = 'Chat Already in Leech Logs'
        elif DB_URI is not None:
            msg = DbManger().addleech_log(chat_id)
            LEECH_LOG.add(chat_id)
        else:
            LEECH_LOG.add(chat_id)
            msg = 'Chat Added to Leech Logs'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in LEECH_LOG:
            msg = 'Chat Already in Leech Logs'
        elif DB_URI is not None:
            msg = DbManger().addleech_log(user_id)
            LEECH_LOG.add(user_id)
        else:
            LEECH_LOG.add(user_id)
            msg = 'Chat Added to Leech Logs'
    sendMessage(msg, context.bot, update.message)


def rmleechlog(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in LEECH_LOG:
            if DB_URI is not None:
                msg = DbManger().rmleech_log(user_id)
            else:
                msg = 'User removed from leech logs'
            LEECH_LOG.remove(user_id)
        else:
            msg = 'User does not exist in leech logs!'
    elif reply_message is None:
        # Trying to unauthorize a chat
        chat_id = update.effective_chat.id
        if chat_id in LEECH_LOG:
            if DB_URI is not None:
                msg = DbManger().rmleech_log(chat_id)
            else:
                msg = 'Chat removed from leech logs!'
            LEECH_LOG.remove(chat_id)
        else:
            msg = 'Chat does not exist in leech logs!'
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in LEECH_LOG:
            if DB_URI is not None:
                msg = DbManger().rmleech_log(user_id)
            else:
                msg = 'User removed from leech logs!'
            LEECH_LOG.remove(user_id)
        else:
            msg = 'User does not exist in leech logs!'
    sendMessage(msg, context.bot, update.message)

def addSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            msg = 'Already Sudo!'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            msg = 'Promoted as Sudo'
    elif reply_message is None:
        msg = "Give ID or Reply To message of whom you want to Promote."
    else:
        # Trying to authorize someone by replying
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            msg = 'Already Sudo!'
        elif DB_URI is not None:
            msg = DbManger().user_addsudo(user_id)
            SUDO_USERS.add(user_id)
        else:
            SUDO_USERS.add(user_id)
            msg = 'Promoted as Sudo'
    sendMessage(msg, context.bot, update.message)

def removeSudo(update, context):
    reply_message = None
    message_ = None
    reply_message = update.message.reply_to_message
    message_ = update.message.text.split(' ')
    if len(message_) == 2:
        user_id = int(message_[1])
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = 'Demoted'
            SUDO_USERS.remove(user_id)
        else:
            msg = 'Not sudo user to demote!'
    elif reply_message is None:
        msg = "Give ID or Reply To message of whom you want to remove from Sudo"
    else:
        user_id = reply_message.from_user.id
        if user_id in SUDO_USERS:
            if DB_URI is not None:
                msg = DbManger().user_rmsudo(user_id)
            else:
                msg = 'Demoted'
            SUDO_USERS.remove(user_id)
        else:
            msg = 'Not sudo user to demote!'
    sendMessage(msg, context.bot, update.message)

def sendAuthChats(update, context):
    user = sudo = leechlog = ''
    user += '\n'.join(f"<code>{uid}</code>" for uid in AUTHORIZED_CHATS)
    sudo += '\n'.join(f"<code>{uid}</code>" for uid in SUDO_USERS)
    leechlog += '\n'.join(f"<code>{uid}</code>" for uid in LEECH_LOG)
    sendMessage(f'<b><u>Authorized Chats:</u></b>\n{user}\n<b><u>Sudo Users:</u></b>\n{sudo}\n<b><u>Leech Log:</u></b>\n{leechlog}\n', context.bot, update.message)


send_auth_handler = CommandHandler(command=BotCommands.AuthorizedUsersCommand, callback=sendAuthChats,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
authorize_handler = CommandHandler(command=BotCommands.AuthorizeCommand, callback=authorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
unauthorize_handler = CommandHandler(command=BotCommands.UnAuthorizeCommand, callback=unauthorize,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
addsudo_handler = CommandHandler(command=BotCommands.AddSudoCommand, callback=addSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)
removesudo_handler = CommandHandler(command=BotCommands.RmSudoCommand, callback=removeSudo,
                                    filters=CustomFilters.owner_filter, run_async=True)
addleechlog_handler = CommandHandler(command=BotCommands.AddleechlogCommand, callback=addleechlog,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
rmleechlog_handler = CommandHandler(command=BotCommands.RmleechlogCommand, callback=rmleechlog,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
dispatcher.add_handler(send_auth_handler)
dispatcher.add_handler(authorize_handler)
dispatcher.add_handler(unauthorize_handler)
dispatcher.add_handler(addsudo_handler)
dispatcher.add_handler(removesudo_handler)
dispatcher.add_handler(addleechlog_handler)
dispatcher.add_handler(rmleechlog_handler)