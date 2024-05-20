1.1.2 - 2024-04-20
==================
- New MalformedError for strict_parse when there are warnings. [67308ce](https://github.com/GatienBouyer/fastgedcom/commit/67308ce18aa599e73055ede1ce03b898b381512f)
- Add a case for LevelInconsistencyWarning: for line with the wrong parent level. [de936b5](https://github.com/GatienBouyer/fastgedcom/commit/de936b53644b5abed62c33ae134b3e8f128a9308)
- Fix guess_encoding which was detecting BOM marks of UTF-16 instead of UTF-32. [62b74a3](https://github.com/GatienBouyer/fastgedcom/commit/62b74a3edfffa18eed6a0b725c42b70deefa7c70)

1.1.1 - 2024-03-20
==================

- New Line.get_source, Line.get_all_sub_lines, and Document.get_source methods. [PR #16](https://github.com/GatienBouyer/fastgedcom/pull/16)
- Deprecated 2 functions of the helpers module. [PR #16](https://github.com/GatienBouyer/fastgedcom/pull/16)
- Fix type error when ansel isn't installed. [f7aa409](https://github.com/GatienBouyer/fastgedcom/commit/f7aa40991fcdbe655e3af1bda138ac4e8b0dc4fc)

1.1.0 - 2024-03-08
==================

- Improve encoding guessing. [PR #12](https://github.com/GatienBouyer/fastgedcom/pull/12)
- Optionnal ansel dependency. [PR #13](https://github.com/GatienBouyer/fastgedcom/pull/13)
- Add Python 3.12 support. [PR #13](https://github.com/GatienBouyer/fastgedcom/pull/13)

1.0.0 - 2023-07-28
==================
- Initial Release
