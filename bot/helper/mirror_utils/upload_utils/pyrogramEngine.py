import logging

from os import remove as osremove, walk, path as ospath, rename as osrename
from time import time, sleep
from pyrogram.errors import FloodWait, RPCError
from PIL import Image
from threading import RLock
from bot import app, DOWNLOAD_DIR, AS_DOCUMENT, AS_DOC_USERS, AS_MEDIA_USERS, CUSTOM_FILENAME, LEECH_LOG, BOT_PM, LEECH_LOG_ALT, IMAGE_LEECH
from bot.helper.ext_utils.fs_utils import take_ss, get_media_info, get_video_resolution, get_path_size
from bot.helper.ext_utils.bot_utils import get_readable_file_size
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

VIDEO_SUFFIXES = ("MKV", "MP4", "MOV", "WMV", "3GP", "MPG", "WEBM", "AVI", "FLV", "M4V", "GIF")
AUDIO_SUFFIXES = ("MP3", "M4A", "M4B", "FLAC", "WAV", "AIF", "OGG", "AAC", "DTS", "MID", "AMR", "MKA")
IMAGE_SUFFIXES = ("JPG", "JPX", "PNG", "WEBP", "CR2", "TIF", "BMP", "JXR", "PSD", "ICO", "HEIC", "JPEG")
TEXT_SUFFIXES = ("TXT", "NFO", "HTML")


class TgUploader:

    def __init__(self, name=None, listener=None):
        self.name = name
        self.uploaded_bytes = 0
        self._last_uploaded = 0
        self.__listener = listener
        self.__start_time = time()
        self.__is_cancelled = False
        self.__as_doc = AS_DOCUMENT
        self.__image_leech = IMAGE_LEECH
        self.__thumb = f"Thumbnails/{listener.message.from_user.id}.jpg"
        self.__sent_msg = ''
        self.__msgs_dict = {}
        self.__corrupted = 0
        self.__resource_lock = RLock()
        self.__user_settings()
        self.__app = app
        self.__chat_id = listener.message.chat.id
        self.__message_id = listener.uid
        self.__user_id = listener.message.from_user.id
        self.__leech_log = LEECH_LOG.copy()  # copy then pop to keep the original var as it is
        self.__leech_log_alt = LEECH_LOG_ALT.copy()  # copy then pop to keep the original var as it is

    def upload(self):
        path = f"{DOWNLOAD_DIR}{self.__listener.uid}"
        size = get_readable_file_size(get_path_size(path))
        for dirpath, subdir, files in sorted(walk(path)):
            for file_ in sorted(files):
                if self.__is_cancelled:
                    return
                if file_.endswith('.torrent'):
                    continue
                up_path = ospath.join(dirpath, file_)
                fsize = ospath.getsize(up_path)
                if fsize <= 1024*100:
                    LOGGER.error(f"{up_path} size is zero, telegram don't upload zero size files")
                    self.__corrupted += 1
                    continue
                self.__upload_file(up_path, file_, dirpath)
                if self.__is_cancelled:
                    return
                self.__msgs_dict[file_] = self.__sent_msg.message_id
                self._last_uploaded = 0
                sleep(1)
        if len(self.__msgs_dict) <= self.__corrupted:
            return self.__listener.onUploadError('Files Corrupted. Check logs')
        LOGGER.info(f"Leech Completed: {self.name}")
        self.__listener.onUploadComplete(None, size, self.__msgs_dict, None, self.__corrupted, self.name)

    def __upload_file(self, up_path, file_, dirpath):
        if self.__sent_msg == '':
            self.__sent_msg = app.get_messages(self.__listener.message.chat.id, self.__listener.uid)
        else:
            self.__sent_msg = app.get_messages(self.__sent_msg.chat.id, self.__sent_msg.message_id)
        if CUSTOM_FILENAME is not None:
            cap_mono = f"{CUSTOM_FILENAME} <code>{file_}</code>"
            file_ = f"{CUSTOM_FILENAME} {file_}"
            new_path = ospath.join(dirpath, file_)
            osrename(up_path, new_path)
            up_path = new_path
        else:
            cap_mono = f"<code>{file_}</code>"
        notMedia = False
        thumb = self.__thumb
        try:
            if not self.__as_doc:
                duration = 0
                if file_.upper().endswith(VIDEO_SUFFIXES):
                    duration = get_media_info(up_path)[0]
                    if thumb is None:
                        thumb = take_ss(up_path)
                        if self.__is_cancelled:
                            if self.__thumb is None and thumb is not None and ospath.lexists(thumb):
                                osremove(thumb)
                            return
                    if thumb is not None:
                        img = Image.open(thumb)
                        width, height = img.size
                    else:
                        width, height = get_video_resolution(up_path)
                    if not file_.upper().endswith(("MKV", "MP4")):
                        file_ = ospath.splitext(file_)[0] + '.mp4'
                        new_path = ospath.join(dirpath, file_)
                        osrename(up_path, new_path)
                        up_path = new_path
                    for i in self.__leech_log:
                        self.__sent_msg = self.__app.send_video(chat_id=i,
                                                              video=up_path,
                                                              caption=cap_mono,
                                                              parse_mode="html",
                                                              duration=duration,
                                                              width=width,
                                                              height=height,
                                                              thumb=thumb,
                                                              supports_streaming=True,
                                                              disable_notification=True,
                                                              progress=self.__upload_progress)
                        if BOT_PM:
                            try:
                                app.send_video(chat_id=self.__user_id, video=self.__sent_msg.video.file_id, caption=cap_mono)
                            except Exception as err:
                                LOGGER.error(f"Failed To Send Video in PM:\n{err}")
                        if LEECH_LOG_ALT:
                            try:
                                for i in self.__leech_log_alt:
                                    app.send_video(chat_id=i, video=self.__sent_msg.video.file_id,
                                               caption=cap_mono)
                            except Exception as err:
                                LOGGER.error(f"Failed to send Video in Alt Leech Log:\n{err}")
                elif file_.upper().endswith(AUDIO_SUFFIXES):
                    duration , artist, title = get_media_info(up_path)
                    for i in self.__leech_log:
                        self.__sent_msg = self.__app.send_audio(chat_id=i,
                                                              audio=up_path,
                                                              caption=cap_mono,
                                                              parse_mode="html",
                                                              duration=duration,
                                                              performer=artist,
                                                              title=title,
                                                              thumb=thumb,
                                                              disable_notification=True,
                                                              progress=self.__upload_progress)
                        if BOT_PM:
                            try:
                                app.send_audio(chat_id=self.__user_id, audio=self.__sent_msg.audio.file_id, caption=cap_mono)
                            except Exception as err:
                                LOGGER.error(f"Failed To Send Audio in PM:\n{err}")
                        if LEECH_LOG_ALT:
                            try:
                                for i in self.__leech_log_alt:
                                    app.send_audio(chat_id=i, audio=self.__sent_msg.audio.file_id, caption=cap_mono)
                            except Exception as err:
                                LOGGER.error(f"Failed to send Audio in Alt Leech Log:\n{err}")

                elif file_.upper().endswith(IMAGE_SUFFIXES):
                    if IMAGE_LEECH is True:
                        try:
                            for i in self.__leech_log:
                                self.__sent_msg = self.__app.send_photo(chat_id=i,
                                                          photo=up_path,
                                                          caption=cap_mono,
                                                          parse_mode="html",
                                                          disable_notification=True,
                                                          progress=self.__upload_progress)
                            if BOT_PM:
                                try:
                                    app.send_photo(chat_id=self.__user_id, photo=self.__sent_msg.photo.file_id,
                                            caption=cap_mono)
                                except Exception as err:
                                    LOGGER.error(f"Failed To Send Image in PM:\n{err}")
                            if LEECH_LOG_ALT:
                                try:
                                    app.send_photo(chat_id=i, photo=self.__sent_msg.photo.file_id,
                                            caption=cap_mono)
                                except Exception as err:
                                    LOGGER.error(f"Failed To Send Image in Alt Leech Log:\n{err}")
                        except Exception as err:
                            LOGGER.warning(f"Image Leech is Blocked by Owner:\n{err}")
                    else:
                        LOGGER.warning(f"Image Leech is Blocked by Owner")
                        pass

                elif file_.upper().endswith(TEXT_SUFFIXES):
                    LOGGER.warning("Useless Text/Html file found, Not Uploading")
                    pass

                else:
                    notMedia = True
            if self.__as_doc or notMedia:
                if file_.upper().endswith(VIDEO_SUFFIXES) and thumb is None:
                    thumb = take_ss(up_path)
                    if self.__is_cancelled:
                        if self.__thumb is None and thumb is not None and ospath.lexists(thumb):
                            osremove(thumb)
                        return
                for i in self.__leech_log:
                    self.__sent_msg = self.__app.send_document(chat_id=i,
                                                             document=up_path,
                                                             thumb=thumb,
                                                             caption=cap_mono,
                                                             parse_mode="html",
                                                             disable_notification=True,
                                                             progress=self.__upload_progress)
                    if BOT_PM:
                        try:
                            app.send_document(chat_id=self.__user_id, document=self.__sent_msg.document.file_id, caption=cap_mono)
                        except Exception as err:
                            LOGGER.error(f"Failed To Send Document in PM:\n{err}")
                    if LEECH_LOG_ALT:
                        try:
                            for i in self.__leech_log_alt:
                                app.send_document(chat_id=i, document=self.__sent_msg.document.file_id, caption=cap_mono)
                        except Exception as err:
                            LOGGER.error(f"Failed To Send Document in Alt Leech Log:\n{err}")
        except FloodWait as f:
            LOGGER.warning(str(f))
            sleep(f.x)
        except RPCError as e:
            LOGGER.error(f"RPCError: {e} File: {up_path}")
            self.__corrupted += 1
        except Exception as err:
            LOGGER.error(f"{err} File: {up_path}")
            self.__corrupted += 1
        if self.__thumb is None and thumb is not None and ospath.lexists(thumb):
            osremove(thumb)
        if not self.__is_cancelled:
            osremove(up_path)

    def __upload_progress(self, current, total):
        if self.__is_cancelled:
            app.stop_transmission()
            return
        with self.__resource_lock:
            chunk_size = current - self._last_uploaded
            self._last_uploaded = current
            self.uploaded_bytes += chunk_size

    def __user_settings(self):
        if self.__listener.message.from_user.id in AS_DOC_USERS:
            self.__as_doc = True
        elif self.__listener.message.from_user.id in AS_MEDIA_USERS:
            self.__as_doc = False
        if not ospath.lexists(self.__thumb):
            self.__thumb = None

    @property
    def speed(self):
        with self.__resource_lock:
            try:
                return self.uploaded_bytes / (time() - self.__start_time)
            except ZeroDivisionError:
                return 0

    def cancel_download(self):
        self.__is_cancelled = True
        LOGGER.info(f"Cancelling Upload: {self.name}")
        self.__listener.onUploadError('your upload has been stopped!')
