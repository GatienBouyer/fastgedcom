1.2.0 - 2026-11-08
==================
- Add type literals for `HEAD` (the gedcom header) and `TRLR` (end of the gedcom) records. [b8ce519](https://github.com/GatienBouyer/fastgedcom/pull/21/changes/b8ce519400cc106e612dda4ab8615c469b2ecf5d)
- Add the possibility to set multi-line payload with `payload_with_cont` on `TrueLine`. [d7c4ef2](https://github.com/GatienBouyer/fastgedcom/pull/21/changes/d7c4ef2158c9e208cac0484a131fc206fec29689)
- Fix `Document.get_records` for shared note records. [5d4ebdf](https://github.com/GatienBouyer/fastgedcom/pull/21/changes/5d4ebdf8feb5ec2ac5540a6e6a802445f14b2e80)
- Add methods `Document.get_or_create` and `TrueLine.get_sub_line_or_create` to create the record or sub-line when it is not present. [1b4b8d0](https://github.com/GatienBouyer/fastgedcom/pull/21/changes/1b4b8d0aa0360dfec99784ae3a7537d4289e49df)

1.1.4 - 2025-11-10
==================
- Add Python 3.14 support. [e251c1b](https://github.com/GatienBouyer/fastgedcom/pull/20/commits/e251c1bf0571c56a8e964b62eb2b8b0da90bb7ab)
- Improve line_to_datetime to also handle date range BET-AND and FROM-TO. [5c40026](https://github.com/GatienBouyer/fastgedcom/pull/20/commits/5c400269d5e43bf2e7d75ad58dbaec0994726650)

1.1.3 - 2024-10-30
==================
- Add Python 3.13 support. [abf7c80](https://github.com/GatienBouyer/fastgedcom/commit/abf7c802f10b7e56a11502130eecfe4f602f58d6)
- Implement Line.__iter__ to iterate over sub-lines [c25c157](https://github.com/GatienBouyer/fastgedcom/commit/c25c157072a57f4f17cb892aa8fd2807ad442018).
- Add Document.all_lines to iterate over every single lines [a420c01](https://github.com/GatienBouyer/fastgedcom/commit/a420c010c33646ebba60e91042870a17781399ce).

1.1.2 - 2024-04-20
==================
- New MalformedError for strict_parse when there are warnings. [67308ce](https://github.com/GatienBouyer/fastgedcom/commit/67308ce18aa599e73055ede1ce03b898b381512f)
- Add a case for LevelInconsistencyWarning: for line with the wrong parent level. [de936b5](https://github.com/GatienBouyer/fastgedcom/commit/de936b53644b5abed62c33ae134b3e8f128a9308)
- Fix guess_encoding which was detecting BOM marks of UTF-16 instead of UTF-32. [62b74a3](https://github.com/GatienBouyer/fastgedcom/commit/62b74a3edfffa18eed6a0b725c42b70deefa7c70)

1.1.1 - 2024-03-20
==================

- New Line.get_source, Line.get_all_sub_lines, and Document.get_source methods. [PR #16](https://github.com/GatienBouyer/fastgedcom/pull/16)
- Deprecate get_source and get_all_sub_lines of the helpers module. [PR #16](https://github.com/GatienBouyer/fastgedcom/pull/16)
- Fix type error when ansel isn't installed. [f7aa409](https://github.com/GatienBouyer/fastgedcom/commit/f7aa40991fcdbe655e3af1bda138ac4e8b0dc4fc)

1.1.0 - 2024-03-08
==================

- Improve encoding guessing. [PR #12](https://github.com/GatienBouyer/fastgedcom/pull/12)
- Optionnal ansel dependency. [PR #13](https://github.com/GatienBouyer/fastgedcom/pull/13)
- Add Python 3.12 support. [PR #13](https://github.com/GatienBouyer/fastgedcom/pull/13)

1.0.0 - 2023-07-28
==================
- Initial Release
