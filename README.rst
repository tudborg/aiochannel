|Build Status|

aiochannel - AsyncIO Channel
============================

Channel concept for asyncio.

*requires* Python 3.6+

`PyPI link <https://pypi.python.org/pypi/aiochannel>`__

Install
-------

::

   pip install aiochannel

Usage
-----

Basics
~~~~~~

Most of the ``Channel`` code is from ``asyncio.Queue``, and the API is
very similar. The key difference is that a channel is only considered
"done" when it has been both closed and drained, so calling ``.join()``
on a channel will wait for it to be both closed and drained (Unlike
``Queue`` which will return from ``.join()`` once the queue is empty).

*NOTE* Closing a channel is permanent. You cannot open it again.

.. code:: py


       import asyncio
       from aiochannel import Channel

       # ...

       # A Channel takes a max queue size and an loop
       # both optional
       my_channel = Channel(100, asyncio.get_event_loop())

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


       # You can wait for the channel to be closed and drained:
       await my_channel.join()
       # Note that this requires someone else to close and drain
       # the channel.

       # Lastly, you can close a channel with
       my_channel.close()
       # Every call to .put() after .close() will fail with
       # a ChannelClosed.
       # you can check if a channel is marked for closing with
       if my_channel.closed():
           print ("Channel is closed")

Like the ``asyncio.Queue`` you can also call non-async get and put:

.. code:: py

       
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

.. code:: py

       
       # the channel might contain data here
       async for item in channel:
           print(item)
       # the channel is closed and empty here

which is functionally equivalent to

.. code:: py


       while True:
           try:
               data = yield from channel.get()
           except ChannelClosed:
               break
           
           # process data here

Noteworthy changes
~~~~~~~~~~~~~~~~~~

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


.. |Build Status| image:: https://github.com/tbug/aiochannel/actions/workflows/test.yml/badge.svg
   :target: https://github.com/tbug/aiochannel/actions/workflows/test.yml
