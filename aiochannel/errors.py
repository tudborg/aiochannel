class ChannelError(Exception):
    pass


class ChannelClosed(ChannelError):
    pass


class ChannelFull(ChannelError):
    pass


class ChannelEmpty(ChannelError):
    pass
