# Changelog

## [Unreleased]

## [1.3.0] - 2024-12-09

### Changed

- Updating dependencies and removing EOL pythons.


## [1.2.1] - 2023-03-01

### Fixed

- `pylama` is now listed as a dev dependency instead of a dependency.


## [1.2.0] - 2023-02-19

### Added

- Typing support with generics. Now you can specify the type
  explicitly, your IDE or mypy will follow this annotations.

### Fixed

- https://github.com/tudborg/aiochannel/issues/13
  A `get` could hang forever in some situations.


## [1.1.1] - 2022-02-08

### Fixed

-  `InvalidStateError` when get or put futures were cancelled.


## [1.1.0] - 2022-02-05

### Removed

- Python 3.5 support.


## [1.0.0] - 2021-04-22


### Removed

- 3.4’s `@coroutine` annotations. Everything is now defined with `async`.


## [0.2.2] - 2015-12-22

### Added

- `Channel` proxies it’s `__iter__` to the underlying queue
  implementation’s `__iter__` (which by default is
  `collections.deque`), meaning that you are now able to iterate channel
  values (which also enables `list(channel)`).


## [0.2.0] - 2015-12-18

# Added

- `Channel` implements the async iterator protocol. You can use
  `async for` to iterate over the channel until it closes, without
  having to deal with `ChannelClosed` exceptions.
  See the `async for` example.


[Unreleased]: https://github.com/tudborg/aiochannel/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/tudborg/aiochannel/releases/tag/v1.3.0
[1.2.1]: https://github.com/tudborg/aiochannel/releases/tag/v1.2.1
[1.2.0]: https://github.com/tudborg/aiochannel/releases/tag/v1.2.0
[1.1.1]: https://github.com/tudborg/aiochannel/releases/tag/v1.1.1
[1.1.0]: https://github.com/tudborg/aiochannel/releases/tag/v1.1.0
[1.0.0]: https://github.com/tudborg/aiochannel/releases/tag/v1.0.0
[0.2.2]: https://github.com/tudborg/aiochannel/releases/tag/v0.2.2
[0.2.0]: https://github.com/tudborg/aiochannel/releases/tag/v0.2.0
