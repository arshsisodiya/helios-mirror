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
        self.StartCommand = getCommand('START_COMMAND', 'start')
        self.MirrorCommand = getCommand('MIRROR_COMMAND', 'mirror')
        self.UnzipMirrorCommand = getCommand('UNZIP_COMMAND', 'unzipmirror')
        self.ZipMirrorCommand = getCommand('ZIP_COMMAND', 'zipmirror')
        self.CancelMirror = getCommand('CANCEL_COMMAND', 'cancel')
        self.CancelAllCommand = getCommand('CANCEL_ALL_COMMAND', 'cancelall')
        self.ListCommand = getCommand('LIST_COMMAND', 'list')
        self.SearchCommand = getCommand('SEARCH_COMMAND', 'search')
        self.StatusCommand = getCommand('STATUS_COMMAND', 'status')
        self.AuthorizedUsersCommand =  getCommand('USERS_COMMAND', 'users')
        self.AuthorizeCommand =  getCommand('AUTH_COMMAND', 'authorize')
        self.UnAuthorizeCommand = getCommand('UNAUTH_COMMAND','unauthorize')
        self.AddSudoCommand = getCommand('ADDSUDO_COMMAND', 'addsudo')
        self.RmSudoCommand = getCommand('RMSUDO_COMMAND', 'rmsudo')
        self.AddModCommand = getCommand('ADDMOD_COMMAND', 'addmod')
        self.RmModCommand = getCommand('RMMOD_COMMAND', 'rmmod')
        self.PingCommand =  getCommand('PING_COMMAND','ping')
        self.RestartCommand =  getCommand('RESTART_COMMAND', 'restart')
        self.StatsCommand = getCommand('STATS_COMMAND', 'stats')
        self.HelpCommand = getCommand('HELP_COMMAND', 'help')
        self.LogCommand = getCommand('LOG_COMMAND' , 'log')
        self.SpeedCommand = getCommand('SPEEDTEST_COMMAND', 'speedtest')
        self.CloneCommand = getCommand('CLONE_COMMAND', 'clone')
        self.CountCommand = getCommand('COUNT_COMMAND', 'count')
        self.WatchCommand = getCommand('WATCH_COMMAND', 'watch')
        self.ZipWatchCommand = getCommand('ZIPWATCH_COMMAND', 'zipwatch')
        self.QbMirrorCommand = getCommand('QBMIRROR_COMMAND', 'qbmirror')
        self.QbUnzipMirrorCommand = getCommand('QBUNZIP_COMMAND', 'qbunzipmirror')
        self.QbZipMirrorCommand = getCommand('QBZIP_COMMAND', 'qbzipmirror')
        self.DeleteCommand = getCommand('DELETE_COMMAND', 'del')
        self.ShellCommand = getCommand('SHELL_COMMAND', 'shell')
        self.ExecHelpCommand = getCommand('EXEHELP_COMMAND', 'exechelp')
        self.LeechSetCommand = getCommand('LEECHSET_COMMAND', 'leechset')
        self.SetThumbCommand = getCommand('SETTHUMB_COMMAND', 'setthumb')
        self.LeechCommand = getCommand('LEECH_COMMAND', 'leech')
        self.UnzipLeechCommand = getCommand('UNZIPLEECH_COMMAND', 'unzipleech')
        self.ZipLeechCommand = getCommand('ZIPLEECH_COMMAND', 'zipleech')
        self.QbLeechCommand = getCommand('QBLEECH_COMMAND', 'qbleech')
        self.QbUnzipLeechCommand = getCommand('QBUNZIPLEECH_COMMAND', 'qbunzipleech')
        self.QbZipLeechCommand = getCommand('QBZIPLEECH_COMMAND', 'qbzipleech')
        self.LeechWatchCommand = getCommand('LEECHWATCH_COMMAND', 'leechwatch')
        self.LeechZipWatchCommand = getCommand('LEECHZIPWATCH_COMMAND', 'leechzipwatch')
        self.TorrentSearchCommand = getCommand('TOR_COMMAND', 'ts')
        self.RssListCommand = getCommand('RSSLIST_COMMAND', 'rsslist')
        self.RssGetCommand = getCommand('RSSGET_COMMAND', 'rssget')
        self.RssSubCommand = getCommand('RSSSUB_COMMAND', 'rsssub')
        self.RssUnSubCommand = getCommand('RSSUNSUB_COMMAND', 'rssunsub')
        self.RssUnSubAllCommand = getCommand('RSSUNSUBALL_COMMAND', 'rssunsuball')
        self.AddleechlogCommand = getCommand('ADDLEECHLOG_COMMAND', 'addll')
        self.RmleechlogCommand = getCommand('RMLEECHLOG_COMMAND', 'rmll')
        self.AddleechlogaltCommand = getCommand('ADDLEECHLOGALT_COMMAND', 'addleechlog')
        self.RmleechlogaltCommand = getCommand('RMLEECHLOGALT_COMMAND', 'rmleechlog')


BotCommands = _BotCommands()
