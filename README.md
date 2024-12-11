# aiochannel - AsyncIO Channel

[![Build Status](https://github.com/tudborg/aiochannel/actions/workflows/test.yml/badge.svg)][Build Status]
[![Stable Version](https://img.shields.io/pypi/v/aiochannel?label=stable)][PyPI Releases]
[![Python Versions](https://img.shields.io/pypi/pyversions/aiochannel)][PyPI]
[![Download Stats](https://img.shields.io/pypi/dm/aiochannel)](https://pypistats.org/packages/aiochannel)

Channel concept for asyncio.


## Install

```
pip install aiochannel
```

## Changelog

[Changelog]

## Usage

### Basics

`Channel` has a very similar API to `asyncio.Queue`.
The key difference is that a channel is only considered
"done" when it has been both closed and drained, so calling `.join()`
on a channel will wait for it to be both closed and drained (Unlike
`Queue` which will return from `.join()` once the queue is empty).

**NOTE:** Closing a channel is permanent. You cannot open it again.

```python
import asyncio
from aiochannel import Channel

# ...

async def main():
    # A Channel takes a max queue size and an loop
    # both optional. loop is not recommended as
    # in asyncio is phasing out explicitly passed event-loop
    my_channel: Channel[str] = Channel(100)

    # You add items to the channel with
    await my_channel.put("my item")
    # Note that this can throw ChannelClosed if the channel
    # is closed, during the attempt at adding the item
    # to the channel. Also note that .put() will block until
    # it can successfully add the item.


    # Retrieving is done with
    my_item = await my_channel.get()
    # Note that this can also throw ChannelClosed if the
    # channel is closed before or during retrival.
    # .get() will block until an item can be retrieved.

    # Note that this requires someone else to close and drain
    # the channel.
    # Lastly, you can close a channel with `my_channel.close()`
    # In this example, the event-loop call this asynchronously
    asyncio.get_event_loop().call_later(0.1, my_channel.close)

    # You can wait for the channel to be closed and drained:
    await my_channel.join()

    # Every call to .put() after .close() will fail with
    # a ChannelClosed.
    # you can check if a channel is marked for closing with
    if my_channel.closed():
        print ("Channel is closed")

asyncio.run(main())
```

Like the `asyncio.Queue` you can also call non-async get and put:

<!--pytest.mark.skip-->

```python
    # non-async version of put
    my_channel.put_nowait(item)
    # This either returns None,
    # or raises ChannelClosed or ChannelFull

    # non-async version of get
    my_channel.get_nowait()
    # This either returns the next item from the channel
    # or raises ChannelEmpty or ChannelClosed
    # (Note that ChannelClosed emplies that the channel
    # is empty, but also that is will never fill again)
```

As of `0.2.0` `Channel` also implements the async iterator protocol.
You can now use `async for` to iterate over the channel until it
closes, without having to deal with `ChannelClosed` exceptions.

<!--pytest.mark.skip-->

```python
    # the channel might contain data here
    async for item in channel:
        print(item)
    # the channel is closed and empty here
```

which is functionally equivalent to

<!--pytest.mark.skip-->

```python
    while True:
        try:
            data = yield from channel.get()
        except ChannelClosed:
            break
        # process data here
```

  [PyPI]: https://pypi.org/project/aiochannel
  [PyPI Releases]: https://pypi.org/project/aiochannel/#history
  [Github]: https://github.com/tudborg/aiochannel
  [Changelog]: https://github.com/tudborg/aiochannel/blob/master/CHANGELOG.md
  [Issue Tracker]: https://github.com/tudborg/aiochannel/issues
  [Build Status]: https://github.com/tudborg/aiochannel/actions/workflows/test.yml
