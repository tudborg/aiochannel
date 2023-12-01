from .channel import Channel
from .errors import ChannelClosed, ChannelFull, ChannelEmpty

import importlib.metadata
__version__ = importlib.metadata.version("aiochannel")


__all__ = [
    "Channel", "ChannelClosed", "ChannelFull", "ChannelEmpty", "__version__"
]
