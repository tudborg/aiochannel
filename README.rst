|Build Status|
|Python Versions|

aiochannel - AsyncIO Channel
============================

Channel concept for asyncio.

*requires* Python 3.6+

`PyPI link <https://pypi.org/project/aiochannel>`__
`GitHub link <https://github.com/tbug/aiochannel>`__

Install
-------

::

   pip install aiochannel

Usage
-----

Basics
~~~~~~

``Channel`` has a very similar API to ``asyncio.Queue``.
The key difference is that a channel is only considered
"done" when it has been both closed and drained, so calling ``.join()``
on a channel will wait for it to be both closed and drained (Unlike
``Queue`` which will return from ``.join()`` once the queue is empty).

*NOTE* Closing a channel is permanent. You cannot open it again.

.. code-block:: python
       :name: test_simple

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


Like the ``asyncio.Queue`` you can also call non-async get and put:


.. code-block:: python


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

As of ``0.2.0`` ``Channel`` also implements the async iterator protocol.
You can now use ``async for`` to iterate over the channel until it
closes, without having to deal with ``ChannelClosed`` exceptions.

.. code-block:: python


       # the channel might contain data here
       async for item in channel:
           print(item)
       # the channel is closed and empty here

which is functionally equivalent to

.. code-block:: python


       while True:
           try:
               data = yield from channel.get()
           except ChannelClosed:
               break

           # process data here

Noteworthy changes
~~~~~~~~~~~~~~~~~~

1.2.0
^^^^^

Added typing support with generics. Now you can specify the type
explicitly, your IDE or mypy will follow this annotations.


.. code-block:: python

    from aiochannel import Channel

    channel: Channel[str] = Channel(100)


0.2.0
^^^^^

``Channel`` implements the async iterator protocol. You can use
``async for`` to iterate over the channel until it closes, without
having to deal with ``ChannelClosed`` exceptions.

See the ``async for`` example.

.. _section-1:

0.2.3
^^^^^

``Channel`` proxies it’s ``__iter__`` to the underlying queue
implementation’s ``__iter__`` (which by default is
``collections.deque``), meaning that you are now able to iterate channel
values (which also enables ``list(channel)``).

.. _section-2:

1.0.0
^^^^^

Dropping 3.4’s ``@coroutine`` annotations. Everything is now defined
with ``async``.


1.1.0
^^^^^

Dropping Python 3.5 support.


1.1.1
^^^^^

Fixing an ``InvalidStateError`` when get or put futures were cancelled.


.. |Build Status| image:: https://github.com/tbug/aiochannel/actions/workflows/test.yml/badge.svg
   :target: https://github.com/tbug/aiochannel/actions/workflows/test.yml

.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/aiochannel.svg
   :target: https://pypi.org/project/aiochannel/
