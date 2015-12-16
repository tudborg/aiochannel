[![Build Status](https://travis-ci.org/tbug/aiochannel.svg?branch=master)](https://travis-ci.org/tbug/aiochannel)

aiochannel - AsyncIO Channel
============================

Channel concept for asyncio.

*requires* Python 3.4.4+ (I think)


Usage
-----------

### Basics

Channels are 90% `asyncio.Queue`, and the API is very similar.
The key difference is that a channel is only considered "done"
when it has been both closed and drained, so calling `.join()`
on a channel will wait for it to be both closed and drained
(Unlike `Queue` which will return from `.join()` once the queue
is empty).

*NOTE* Closing a channel is permanent. You cannot open it again.

```py

    import asyncio
    from aiochannel import Channel

    # ...

    # A Channel takes a max queue size and an loop
    # both optional
    my_channel = Channel(100, asyncio.get_event_loop())

    # You add items to the channel with
    yield from my_channel.put("my item")
    # Note that this can throw ChannelClosed if the channel
    # is closed, during the attempt at adding the item
    # to the channel. Also note that .put() will block until
    # it can successfully add the item.


    # Retrieving is done with
    my_item = yield from my_channel.get()
    # Note that this can also throw ChannelClosed if the
    # channel is closed before or during retrival.
    # .get() will block until an item can be retrieved.


    # You can wait for the channel to be closed and drained:
    yield from my_channel.join()
    # Note that this requires someone else to close and drain
    # the channel.

    # Lastly, you can close a channel with
    my_channel.close()
    # Every call to .put() after .close() will fail with
    # a ChannelClosed.
    # you can check if a channel is marked for closing with
    if my_channel.closed():
        print ("Channel is closed")
```

Like the `asyncio.Queue` you can also call non-coroutine get and put:

```py
    
    # non-coroutine version of put
    my_channel.put_nowait(item)
    # This either returns None,
    # or raises ChannelClosed or ChannelFull

    # non-coroutine version of get
    my_channel.get_nowait()
    # This either returns the next item from the channel
    # or raises ChannelEmpty or ChannelClosed
    # (Note that ChannelClosed emplies that the channel
    # is empty, but also that is will never fill again)
```