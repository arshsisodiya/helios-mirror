from bot import CMD_INDEX
import os
def getCommand(name: str, command: str):
    try:
        if len(os.environ[name]) == 0:
            raise KeyError
        return os.environ[name]
    except KeyError:
        return command


class _BotCommands:
    def __init__(self):
        self.StartCommand = getCommand(f'START_CMD', f'start{CMD_INDEX}')
        self.MirrorCommand = getCommand('MIRROR_CMD', f'mirror{CMD_INDEX}')
        self.UnzipMirrorCommand = getCommand('UNZIP_CMD', f'unzipmirror{CMD_INDEX}')
        self.ZipMirrorCommand = getCommand('ZIP_CMD', f'zipmirror{CMD_INDEX}')
        self.QbMirrorCommand = getCommand('QBMIRROR_CMD', f'qbmirror{CMD_INDEX}')
        self.QbUnzipMirrorCommand = getCommand('QBUNZIP_CMD', f'qbunzipmirror{CMD_INDEX}')
        self.QbZipMirrorCommand = getCommand('QBZIP_CMD', f'qbzipmirror{CMD_INDEX}')
        self.YtdlCommand =  getCommand('YTDL_CMD', f'ytdl{CMD_INDEX}')
        self.YtdlZipCommand = getCommand('YTDLZIP_CMD', f'ytdlzip{CMD_INDEX}')
        self.LeechCommand = getCommand('LEECH_CMD', f'leech{CMD_INDEX}')
        self.UnzipLeechCommand = getCommand('UNZIPLEECH_CMD', f'unzipleech{CMD_INDEX}')
        self.ZipLeechCommand = getCommand('ZIPLEECH_CMD', f'zipleech{CMD_INDEX}')
        self.QbLeechCommand = getCommand('QBLEECH_CMD', f'qbleech{CMD_INDEX}')
        self.QbUnzipLeechCommand = getCommand('QBZIPLEECH_CMD', f'qbunzipleech{CMD_INDEX}')
        self.QbZipLeechCommand = getCommand('QBUNZIPLEECH_CMD', f'qbzipleech{CMD_INDEX}')
        self.YtdlLeechCommand =getCommand('YTDLLEECH_CMD',  f'ytdlleech{CMD_INDEX}')
        self.YtdlZipLeechCommand = getCommand('YTDLZIPLEECH_CMD', f'ytdlzipleech{CMD_INDEX}')
        self.CloneCommand = getCommand('CLONE_CMD', f'clone{CMD_INDEX}')
        self.CountCommand = getCommand('COUNT_CMD', f'count{CMD_INDEX}')
        self.DeleteCommand = getCommand('DELETE_CMD', f'del{CMD_INDEX}')
        self.CancelMirror = getCommand('CANCEL_CMD', f'cancel{CMD_INDEX}')
        self.CancelAllCommand = getCommand('CANCEL_ALL_CMD', f'cancelall{CMD_INDEX}')
        self.ListCommand = getCommand('LIST_CMD', f'list{CMD_INDEX}')
        self.SearchCommand = getCommand('SEARCH_CMD', f'search{CMD_INDEX}')
        self.StatusCommand = getCommand('STATUS_CMD', f'status{CMD_INDEX}')
        self.AuthorizedUsersCommand = f'users{CMD_INDEX}'
        self.AuthorizeCommand = f'authorize{CMD_INDEX}'
        self.UnAuthorizeCommand = f'unauthorize{CMD_INDEX}'
        self.AddSudoCommand = f'addsudo{CMD_INDEX}'
        self.RmSudoCommand = f'rmsudo{CMD_INDEX}'
        self.PingCommand = f'ping{CMD_INDEX}'
        self.RestartCommand = f'restart{CMD_INDEX}'
        self.StatsCommand = f'stats{CMD_INDEX}'
        self.HelpCommand = f'help{CMD_INDEX}'
        self.LogCommand = f'log{CMD_INDEX}'
        self.ShellCommand = f'shell{CMD_INDEX}'
        self.EvalCommand = f'eval{CMD_INDEX}'
        self.ExecCommand = f'exec{CMD_INDEX}'
        self.ClearLocalsCommand = f'clearlocals{CMD_INDEX}'
        self.LeechSetCommand = f'leechset{CMD_INDEX}'
        self.SetThumbCommand = f'setthumb{CMD_INDEX}'
        self.BtSelectCommand = f'btsel{CMD_INDEX}'
        self.RssListCommand = getCommand('RSSLIST_CMD', f'rsslist{CMD_INDEX}')
        self.RssGetCommand = getCommand('RSSGET_CMD', f'rssget{CMD_INDEX}')
        self.RssSubCommand = getCommand('RSSSUB_CMD', f'rsssub{CMD_INDEX}')
        self.RssUnSubCommand = getCommand('RSSUNSUB_CMD', f'rssunsub{CMD_INDEX}')
        self.RssSettingsCommand = getCommand('RSSSET_CMD', f'rssset{CMD_INDEX}')
        self.AddleechlogCommand = getCommand('ADDLEECHLOG_CMD', f'addleechlog{CMD_INDEX}')
        self.RmleechlogCommand = getCommand('RMLEECHLOG_CMD', f'rmleechlog{CMD_INDEX}')
BotCommands = _BotCommands()
