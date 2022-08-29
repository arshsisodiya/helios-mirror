from requests import utils as rutils
from threading import Thread
from re import search as re_search
from time import sleep
from os import path as ospath, remove as osremove, listdir, walk
from subprocess import Popen
from html import escape
from bot import bot, Interval, INDEX_URL, VIEW_LINK, aria2, DOWNLOAD_DIR, download_dict, download_dict_lock, \
                LEECH_SPLIT_SIZE, LOGGER, DB_URI, INCOMPLETE_TASK_NOTIFIER, MAX_SPLIT_SIZE, MIRROR_LOGS, BOT_PM, SOURCE_LINK, AUTO_DELETE_UPLOAD_MESSAGE_DURATION, FORCE_BOT_PM, LEECH_LOG
from bot.helper.ext_utils.fs_utils import get_base_name, get_path_size, split_file, clean_download, clean_target
from bot.helper.ext_utils.exceptions import NotSupportedExtractionArchive
from bot.helper.mirror_utils.status_utils.extract_status import ExtractStatus
from bot.helper.mirror_utils.status_utils.zip_status import ZipStatus
from bot.helper.mirror_utils.status_utils.split_status import SplitStatus
from bot.helper.mirror_utils.status_utils.upload_status import UploadStatus
from bot.helper.mirror_utils.status_utils.tg_upload_status import TgUploadStatus
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.mirror_utils.upload_utils.pyrogramEngine import TgUploader
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, delete_all_messages, update_all_messages, auto_delete_upload_message
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.ext_utils.telegraph_helper import telegraph
from bot.helper.ext_utils.bot_utils import is_url, is_magnet
class MirrorLeechListener:
    def __init__(self, bot, message, isZip=False, extract=False, isQbit=False, isLeech=False, pswd=None, tag=None, select=False, seed=False):
        self.bot = bot
        self.message = message
        self.uid = message.message_id
        self.extract = extract
        self.isZip = isZip
        self.isQbit = isQbit
        self.isLeech = isLeech
        self.pswd = pswd
        self.tag = tag
        self.seed = seed
        self.newDir = ""
        self.dir = f"{DOWNLOAD_DIR}{self.uid}"
        self.select = select
        self.isPrivate = message.chat.type in ['private', 'group']
        self.suproc = None
        self.user_id = self.message.from_user.id

    def clean(self):
        try:
            Interval[0].cancel()
            Interval.clear()
            aria2.purge()
            delete_all_messages()
        except:
            pass

    def onDownloadStart(self):
        if not self.isPrivate and INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().add_incomplete_task(self.message.chat.id, self.message.link, self.tag)

    def onDownloadComplete(self):
        with download_dict_lock:
            download = download_dict[self.uid]
            name = str(download.name()).replace('/', '')
            gid = download.gid()
        LOGGER.info(f"Download completed: {name}")
        if name == "None" or self.isQbit or not ospath.exists(f"{self.dir}/{name}"):
            name = listdir(f"{self.dir}")[-1]
        m_path = f'{self.dir}/{name}'
        size = get_path_size(m_path)
        if self.isZip:
            if self.seed and self.isLeech:
                self.newDir = f"{self.dir}10000"
                path = f"{self.newDir}/{name}.zip"
            else:
                path = f"{m_path}.zip"
            with download_dict_lock:
                download_dict[self.uid] = ZipStatus(name, size, gid, self)
            if self.pswd is not None:
                if self.isLeech and int(size) > LEECH_SPLIT_SIZE:
                    LOGGER.info(f'Zip: orig_path: {m_path}, zip_path: {path}.0*')
                    self.suproc = Popen(["7z", f"-v{LEECH_SPLIT_SIZE}b", "a", "-mx=0", f"-p{self.pswd}", path, m_path])
                else:
                    LOGGER.info(f'Zip: orig_path: {m_path}, zip_path: {path}')
                    self.suproc = Popen(["7z", "a", "-mx=0", f"-p{self.pswd}", path, m_path])
            elif self.isLeech and int(size) > LEECH_SPLIT_SIZE:
                LOGGER.info(f'Zip: orig_path: {m_path}, zip_path: {path}.0*')
                self.suproc = Popen(["7z", f"-v{LEECH_SPLIT_SIZE}b", "a", "-mx=0", path, m_path])
            else:
                LOGGER.info(f'Zip: orig_path: {m_path}, zip_path: {path}')
                self.suproc = Popen(["7z", "a", "-mx=0", path, m_path])
            self.suproc.wait()
            if self.suproc.returncode == -9:
                return
            elif not self.seed:
                clean_target(m_path)
        elif self.extract:
            try:
                if ospath.isfile(m_path):
                    path = get_base_name(m_path)
                LOGGER.info(f"Extracting: {name}")
                with download_dict_lock:
                    download_dict[self.uid] = ExtractStatus(name, size, gid, self)
                if ospath.isdir(m_path):
                    if self.seed:
                        self.newDir = f"{self.dir}10000"
                        path = f"{self.newDir}/{name}"
                    else:
                        path = m_path
                    for dirpath, subdir, files in walk(m_path, topdown=False):
                        for file_ in files:
                            if re_search(r'\.part0*1\.rar$|\.7z\.0*1$|\.zip\.0*1$|\.zip$|\.7z$|^.(?!.*\.part\d+\.rar)(?=.*\.rar$)', file_):
                                f_path = ospath.join(dirpath, file_)
                                if self.seed:
                                    t_path = dirpath.replace(self.dir, self.newDir)
                                else:
                                    t_path = dirpath
                                if self.pswd is not None:
                                    self.suproc = Popen(["7z", "x", f"-p{self.pswd}", f_path, f"-o{t_path}", "-aot"])
                                else:
                                    self.suproc = Popen(["7z", "x", f_path, f"-o{t_path}", "-aot"])
                                self.suproc.wait()
                                if self.suproc.returncode == -9:
                                    return
                                elif self.suproc.returncode != 0:
                                    LOGGER.error('Unable to extract archive splits!')
                        if not self.seed and self.suproc is not None and self.suproc.returncode == 0:
                            for file_ in files:
                                if re_search(r'\.r\d+$|\.7z\.\d+$|\.z\d+$|\.zip\.\d+$|\.zip$|\.rar$|\.7z$', file_):
                                    del_path = ospath.join(dirpath, file_)
                                    try:
                                        osremove(del_path)
                                    except:
                                        return
                else:
                    if self.seed and self.isLeech:
                        self.newDir = f"{self.dir}10000"
                        path = path.replace(self.dir, self.newDir)
                    if self.pswd is not None:
                        self.suproc = Popen(["7z", "x", f"-p{self.pswd}", m_path, f"-o{path}", "-aot"])
                    else:
                        self.suproc = Popen(["7z", "x", m_path, f"-o{path}", "-aot"])
                    self.suproc.wait()
                    if self.suproc.returncode == -9:
                        return
                    elif self.suproc.returncode == 0:
                        LOGGER.info(f"Extracted Path: {path}")
                        if not self.seed:
                            try:
                                osremove(m_path)
                            except:
                                return
                    else:
                        LOGGER.error('Unable to extract archive! Uploading anyway')
                        self.newDir = ""
                        path = m_path
            except NotSupportedExtractionArchive:
                LOGGER.info("Not any valid archive, uploading file as it is.")
                self.newDir = ""
                path = m_path
        else:
            path = m_path
        up_dir, up_name = path.rsplit('/', 1)
        size = get_path_size(up_dir)
        if self.isLeech:
            m_size = []
            o_files = []
            if not self.isZip:
                checked = False
                for dirpath, subdir, files in walk(up_dir, topdown=False):
                    for file_ in files:
                        f_path = ospath.join(dirpath, file_)
                        f_size = ospath.getsize(f_path)
                        if f_size > LEECH_SPLIT_SIZE:
                            if not checked:
                                checked = True
                                with download_dict_lock:
                                    download_dict[self.uid] = SplitStatus(up_name, size, gid, self)
                                LOGGER.info(f"Splitting: {up_name}")
                            res = split_file(f_path, f_size, file_, dirpath, LEECH_SPLIT_SIZE, self)
                            if not res:
                                return
                            if res == "errored":
                                if f_size <= MAX_SPLIT_SIZE:
                                    continue
                                else:
                                    try:
                                        osremove(f_path)
                                    except:
                                        return
                            elif not self.seed or self.newDir:
                                try:
                                    osremove(f_path)
                                except:
                                    return
                            elif self.seed and res != "errored":
                                m_size.append(f_size)
                                o_files.append(file_)

            size = get_path_size(up_dir)
            for s in m_size:
                size = size - s
            LOGGER.info(f"Leech Name: {up_name}")
            tg = TgUploader(up_name, up_dir, size, self)
            tg_upload_status = TgUploadStatus(tg, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = tg_upload_status
            update_all_messages()
            tg.upload(o_files)
        else:
            up_path = f'{up_dir}/{up_name}'
            size = get_path_size(up_path)
            LOGGER.info(f"Upload Name: {up_name}")
            drive = GoogleDriveHelper(up_name, up_dir, size, self)
            upload_status = UploadStatus(drive, size, gid, self)
            with download_dict_lock:
                download_dict[self.uid] = upload_status
            update_all_messages()
            drive.upload(up_name)

    def onUploadComplete(self, link: str, size, files, folders, typ, name):
        if not self.isPrivate and INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)
        mesg = self.message.text.split('\n')
        message_args = mesg[0].split(' ', maxsplit=1)
        reply_to = self.message.reply_to_message
        if self.message.chat.type != 'private' and AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1 and reply_to is not None:
            try:
                reply_to.delete()
            except exception as err:
                pass
        if self.isLeech:
            uptype = "files"
        else:
            uptype = "links"
        msg = f"<b>Name: </b><code>{escape(name)}</code>\n\n<b>Size: </b>{size}"
        if BOT_PM and FORCE_BOT_PM and not self.isPrivate:
            botpm = f"<b>\n\nHey {self.tag}!, I have sent your {uptype} in PM.</b>\n"
            buttons = ButtonMaker()
            b_uname = bot.get_me().username
            botstart = f"http://t.me/{b_uname}"
            buttons.buildbutton(f"View {uptype} in PM", f"{botstart}")
            sendMarkup(msg + botpm, self.bot, self.message, buttons.build_menu(2))
            self.message.delete()
            reply_to = self.message.reply_to_message
            if reply_to is not None and AUTO_DELETE_UPLOAD_MESSAGE_DURATION == -1:
                reply_to.delete()

        if self.isLeech:
            buttons = ButtonMaker()
            if SOURCE_LINK is True:
                try:
                    source_link = message_args[1]
                    if is_magnet(source_link):
                        link = telegraph.create_page(
                        title='Helios-Mirror Source Link',
                        content=source_link,
                    )["path"]
                        buttons.buildbutton(f"🔗 Source Link", f"https://graph.org/{link}")
                    else:
                        buttons.buildbutton(f"🔗 Source Link", source_link)
                except Exception as e:
                    LOGGER.warning(e)
                pass
                if reply_to is not None:
                    try:
                        reply_text = reply_to.text
                        if is_url(reply_text):
                            source_link = reply_text.strip()
                            if is_magnet(source_link):
                                link = telegraph.create_page(
                                    title='Helios-Mirror Source Link',
                                    content=source_link,
                                )["path"]
                                buttons.buildbutton(f"🔗 Source Link", f"https://graph.org/{link}")
                            else:
                                buttons.buildbutton(f"🔗 Source Link", source_link)
                    except Exception as e:
                        LOGGER.warning(e)
                        pass
            if BOT_PM is True and FORCE_BOT_PM is False:
                b_name = bot.get_me().username
                botstart = f"http://t.me/{b_name}"
                buttons.buildbutton("View file in PM", f"{botstart}")
            msg += f'\n<b>Total Files: </b>{folders}'
            if typ != 0:
                msg += f'\n<b>Corrupted Files: </b>{typ}'
            msg += f'\n<b>cc: </b>{self.tag}\n\n'
            if not files:
                sendMessage(msg, self.bot, self.message)
            else:
                fmsg = ''
                for index, (link, name) in enumerate(files.items(), start=1):
                    fmsg += f"{index}. <a href='{link}'>{name}</a>\n"
                    if len(fmsg.encode() + msg.encode()) > 4000:
                        if FORCE_BOT_PM is False:
                            upldmsg = sendMarkup(msg + fmsg, self.bot, self.message, buttons.build_menu(1))
                            Thread(target=auto_delete_upload_message, args=(self.bot, self.message, upldmsg)).start()
                        sleep(1)
                        fmsg = ''
                if fmsg != '':
                    if FORCE_BOT_PM is False:
                        upldmsg = sendMarkup(msg + fmsg, self.bot, self.message, buttons.build_menu(1))
                        Thread(target=auto_delete_upload_message, args=(self.bot, self.message, upldmsg)).start()
                if LEECH_LOG and FORCE_BOT_PM:
                    try:
                        for chatid in LEECH_LOG:
                            bot.sendMessage(chat_id=chatid, text=msg + fmsg,
                                            reply_markup=(buttons.build_menu(2)),
                                            parse_mode='HTML', disable_web_page_preview=True)
                    except Exception as e:
                        LOGGER.warning(e)
            if self.seed:
                if self.newDir:
                    clean_target(self.newDir)
                return
        else:
            msg += f'\n\n<b>Type: </b>{typ}'
            if typ == "Folder":
                msg += f'\n<b>SubFolders: </b>{folders}'
                msg += f'\n<b>Files: </b>{files}'
            buttons = ButtonMaker()
            msg += f'\n\n<b>cc: </b>{self.tag}'
            buttons.buildbutton("☁️ Drive Link", link)
            LOGGER.info(f'Done Uploading {name}')
            if INDEX_URL is not None:
                url_path = rutils.quote(f'{name}')
                share_url = f'{INDEX_URL}/{url_path}'
                if typ == "Folder":
                    share_url += '/'
                    buttons.buildbutton("⚡ Index Link", share_url)
                else:
                    buttons.buildbutton("⚡ Index Link", share_url)
                    if VIEW_LINK:
                        share_urls = f'{INDEX_URL}/{url_path}?a=view'
                        buttons.buildbutton("🌐 View Link", share_urls)
                    if SOURCE_LINK is True:
                        try:
                            mesg = message_args[1]
                            if is_magnet(mesg):
                                link = telegraph.create_page(
                                    title='Helios-Mirror Source Link',
                                    content=mesg,
                                )["path"]
                                buttons.buildbutton(f"🔗 Source Link", f"https://graph.org/{link}")
                            elif is_url(mesg):
                                source_link = mesg
                                if source_link.startswith(("|", "pswd: ")):
                                    pass
                                else:
                                    buttons.buildbutton(f"🔗 Source Link", source_link)
                            else:
                                pass
                        except Exception as e:
                            LOGGER.warning(e)
                            pass
                    if reply_to is not None:
                        try:
                            reply_text = reply_to.text
                            if is_url(reply_text):
                                source_link = reply_text.strip()
                                if is_magnet(source_link):
                                    link = telegraph.create_page(
                                        title='Helios-Mirror Source Link',
                                        content=source_link,
                                    )["path"]
                                    buttons.buildbutton(f"🔗 Source Link", f"https://graph.org/{link}")
                                else:
                                    buttons.buildbutton(f"🔗 Source Link", source_link)
                        except Exception as e:
                            LOGGER.warning(e)
                            pass
            if FORCE_BOT_PM is False or self.message.chat.type == 'private' :
                upldmsg = sendMarkup(msg, self.bot, self.message, buttons.build_menu(2))
                Thread(target=auto_delete_upload_message, args=(self.bot, self.message, upldmsg)).start()
            if MIRROR_LOGS:
                try:
                    for chatid in MIRROR_LOGS:
                        bot.sendMessage(chat_id=chatid, text=msg,
                                        reply_markup=(buttons.build_menu(2)),
                                        parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    LOGGER.warning(e)
            if BOT_PM and self.message.chat.type != 'private':
                try:
                    bot.sendMessage(chat_id=self.user_id, text=msg,
                                    reply_markup=(buttons.build_menu(2)),
                                    parse_mode='HTML', disable_web_page_preview=True)
                except Exception as e:
                    LOGGER.warning(e)
                    return
            if self.seed:
                if self.isZip:
                    clean_target(f"{self.dir}/{name}")
                elif self.newDir:
                    clean_target(self.newDir)
                return
        clean_download(self.dir)
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onDownloadError(self, error):
        reply_to = self.message.reply_to_message
        try:
            if AUTO_DELETE_UPLOAD_MESSAGE_DURATION != -1 and reply_to is not None:
                reply_to.delete()
            else:
                pass
        except:
            pass
        error = error.replace('<', ' ').replace('>', ' ')
        clean_download(self.dir)
        if self.newDir:
            clean_download(self.newDir)
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        msg = f"{self.tag} your download has been stopped due to: {error}"
        errmsg = sendMessage(msg, self.bot, self.message)
        Thread(target=auto_delete_upload_message, args=(self.bot, self.message, errmsg)).start()
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        if not self.isPrivate and INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)

    def onUploadError(self, error):
        e_str = error.replace('<', '').replace('>', '')
        clean_download(self.dir)
        if self.newDir:
            clean_download(self.newDir)
        with download_dict_lock:
            try:
                del download_dict[self.uid]
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        errmsg = sendMessage(f"{self.tag} {e_str}", self.bot, self.message)
        Thread(target=auto_delete_upload_message, args=(self.bot, self.message, errmsg)).start()
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        if not self.isPrivate and INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
            DbManger().rm_complete_task(self.message.link)
