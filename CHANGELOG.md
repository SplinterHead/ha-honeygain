# CHANGELOG

## v1.2.1 (2024-09-28)

### Build

* build(deps): update black and format with new rules. update homeassistant to 2024 ([`62e8931`](https://github.com/SplinterHead/ha-honeygain/commit/62e893179f28ac0f911cf718df5633822f527e9b))

### Fix

* fix(sensor): update the megabyte unit of information to the current ENum ([`4b8e20b`](https://github.com/SplinterHead/ha-honeygain/commit/4b8e20b8a44086ff4751f5da8f7d937de0b54d52))

## v1.2.0 (2024-09-27)

### Ci

* ci: grant more permissions to the release process and clone all history ([`ddf1e72`](https://github.com/SplinterHead/ha-honeygain/commit/ddf1e723a7ede35c38b78d4611895e0c815efe2e))

* ci: replace node semantic-release with python-semantic-release ([`040abd9`](https://github.com/SplinterHead/ha-honeygain/commit/040abd9bcb9db13f1b6ef7c422b937a4608c7bef))

* ci: update actions/checkout to v4 ([`9960578`](https://github.com/SplinterHead/ha-honeygain/commit/9960578150ec09de5e5d04f6ee8f6aa39e3dfe62))

* ci: remove semantic-release-python plugin for deploying to PyPi ([`574167d`](https://github.com/SplinterHead/ha-honeygain/commit/574167d1b5a7abd30557f65f2e420bdb3447952f))

* ci: add the `GITHUB_TOKEN` to the pipeline (#8)

expose the GH_TOKEN to the pipeline for creating releases ([`ccd7e3a`](https://github.com/SplinterHead/ha-honeygain/commit/ccd7e3aa45c399510692120f58b72f93192642d4))

* ci: semantic release (#7)

* ci: create a semantic release for the repo
* ci: run npx non-interactively in the pipeline
* ci: set up a compatible version of NodeJS for creating a release
* ci: run the release job after the validation
* ci: only run the release job if the commit is on the main branch ([`e54fac9`](https://github.com/SplinterHead/ha-honeygain/commit/e54fac923cbe4e31e180cb341738ee95c8faef75))

### Documentation

* docs: add automation example to the readme ([`48b3f08`](https://github.com/SplinterHead/ha-honeygain/commit/48b3f081481f623a8e24a76461dccd10782bf906))

### Feature

* feat: add sensors for current day stats

* today&#39;s credits
* today&#39;s bandwidth
* today&#39;s referral credits
* today&#39;s lucky pot earnings ([`8c82d9c`](https://github.com/SplinterHead/ha-honeygain/commit/8c82d9cfa083eae61a24c0c8ddf5a9e5f1b9da2c))

### Unknown

* Merge pull request #10 from SplinterHead/feat/today_stats

feat: add sensors for current day stats ([`b7c1cec`](https://github.com/SplinterHead/ha-honeygain/commit/b7c1cec29c8a0debe46d6e3c58f84b94eb812042))

* Merge pull request #9 from SplinterHead/ci/semantic-release

ci: remove semantic-release-python plugin for deploying to PyPi ([`1eafb14`](https://github.com/SplinterHead/ha-honeygain/commit/1eafb14a2589b40cec933bf749625f2f8f4c186a))

## v1.1.0 (2023-12-19)

### Feature

* feat: add button for opening the daily pot ([`a4e93be`](https://github.com/SplinterHead/ha-honeygain/commit/a4e93be06dc77a3dec115eb3bd00717a21d756f7))

## v1.0.1 (2023-12-19)

### Fix

* fix: call sensor value with the Honeygain data object ([`09d098f`](https://github.com/SplinterHead/ha-honeygain/commit/09d098f0a7e080720a6a9e622d1abd790189dfac))

## v1.0.0 (2023-12-19)

### Build

* build: add pylint to the dev process ([`77b41e8`](https://github.com/SplinterHead/ha-honeygain/commit/77b41e8a1d5e57cf723cb7ef13a73840e861cf51))

### Chore

* chore: Initialise the codebase ([`2be967c`](https://github.com/SplinterHead/ha-honeygain/commit/2be967c275193abe75aec823bb3ca727ed3c650f))

### Documentation

* docs: update the README to reflect the integration ([`ae7f09f`](https://github.com/SplinterHead/ha-honeygain/commit/ae7f09ff92c279667195786b4fdda6665061a487))

### Feature

* feat: add iot_class to the manifest ([`5a613ef`](https://github.com/SplinterHead/ha-honeygain/commit/5a613efc30b7c2c932ae673c5504ae9df65824e6))

* feat: add hacs.json manifest ([`0b2604a`](https://github.com/SplinterHead/ha-honeygain/commit/0b2604afcda79d51ae5471444538e955fd719224))

* feat: porting from HA-core to native repo ([`254fcdc`](https://github.com/SplinterHead/ha-honeygain/commit/254fcdcedc007cca48c12afe668d8c76e18eed99))

### Unknown

* Initial commit ([`c63e3ea`](https://github.com/SplinterHead/ha-honeygain/commit/c63e3ea192c3b234fa754985a71645dd522702ed))
