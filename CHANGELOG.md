# Changelog

<!--next-version-placeholder-->

## v0.13.0 (2021-06-08)
### Feature
* Support size definition in metadata ([`b3923ba`](https://github.com/neoave/mrack/commit/b3923baf2b4969946a935536c2509dee349bc27f))

### Fix
* Use BaseOS as variant for RHEL9.0 in Beaker ([`9908257`](https://github.com/neoave/mrack/commit/9908257f01a417a22e36d3768502530b254c7a0b))

## v0.12.0 (2021-05-13)
### Feature
* Gracefully destroy servers after traceback ([`ab22410`](https://github.com/neoave/mrack/commit/ab22410cf07785c2e430464a5e933807a6d785dc))
* Wait for provider resources up to hour ([`b9612cf`](https://github.com/neoave/mrack/commit/b9612cfaa194fe99a691529b42c5549010a21e03))
* **OpenStack:** Check openstack response for resources issue ([`328e0c9`](https://github.com/neoave/mrack/commit/328e0c9262e9a577a11817975218259ddf1ebd91))
* **Virt:** Use generated run IDs for parallel jobs ([`60292ea`](https://github.com/neoave/mrack/commit/60292eaca1ff2f83746718c2f6aa2fc25ab0cbdf))
* Password authentication in ssh_to_host ([`dd151b5`](https://github.com/neoave/mrack/commit/dd151b524eac0eaecf9faf35d81073a0724f9d1e))
* Virt a local virtual machine provider ([`b2f917e`](https://github.com/neoave/mrack/commit/b2f917e3a17802ac238508e2326d0b262f02f6fd))
* **OpenStack:** Move network translation to provider ([`5d5146b`](https://github.com/neoave/mrack/commit/5d5146b098c268bed8fe277c1cba30dd0a514317))
* Add capability to disable ssh check ([`efc5061`](https://github.com/neoave/mrack/commit/efc5061c93f28510d56ca53d5be53b5f709e3ff8))
* **OpenStack:** Distribute choosing of networks ([`b28acca`](https://github.com/neoave/mrack/commit/b28acca76cd095a5c70e8417ffe9321b8aa671c0))

### Fix
* Remove redundant host validation ([`baa2a06`](https://github.com/neoave/mrack/commit/baa2a06c27ece44302848a9f36fcd24681034e8f))
* Change priority of hardcoding Administrator to Win hosts ([`3a5f19f`](https://github.com/neoave/mrack/commit/3a5f19ffc0b995814182bec335e002147fe670c2))
* Do not add the config_drive_req to req ([`db1f82a`](https://github.com/neoave/mrack/commit/db1f82ae6a108fc8da38961cb0efe6dafede8726))

### Documentation
* Update method docsting as it does not Validate hosts anymore ([`46e725c`](https://github.com/neoave/mrack/commit/46e725ca64223da5560948a144a5798f0e8499ed))

## v0.11.0 (2021-05-07)
### Feature
* Log mrack version into mrack.log ([`8ffa3c6`](https://github.com/neoave/mrack/commit/8ffa3c6610535c7fae8f4fa7d8d7a833bb200cab))
* Add --version option to mrack cli ([`1863b79`](https://github.com/neoave/mrack/commit/1863b79c97ea00bc9277bba0fec1c78d7b42fbf8))

### Fix
* Decrease and insanely long timeout ([`2d8ed4e`](https://github.com/neoave/mrack/commit/2d8ed4ec115a9c2ac5ea2f904035b5042dbe570b))

## v0.10.0 (2021-04-30)
### Feature
* Create podman networks in preparation ([`c6791ce`](https://github.com/neoave/mrack/commit/c6791cedc49148200761f3540778fe6a999110f5))
* Pull podman images in preparation ([`c19b230`](https://github.com/neoave/mrack/commit/c19b230da6c7fa01ef3200853aecd115ed2badc2))
* Check ssh connectivity outside of pares_error_hosts more than once ([`ecd5470`](https://github.com/neoave/mrack/commit/ecd5470babfec8868263127d4b1cdf42b7bc52b6))
* Use always root user for provisioned containers ([`311a8a5`](https://github.com/neoave/mrack/commit/311a8a576af821ccd2c49ef615a38521b1a7d67b))
* Use more flexible way of defining podman names ([`a94d922`](https://github.com/neoave/mrack/commit/a94d922fc6aa83e65c538cb09edfd139487caf35))
* Use ssh public key to access container instead of podman id ([`87c1ff0`](https://github.com/neoave/mrack/commit/87c1ff04215d120f90d6e8785d7c2478da92ec13))
* Add capability to use custom podman options ([`d05a41f`](https://github.com/neoave/mrack/commit/d05a41f542861ff404113af68de52041779f0d72))

### Fix
* The type of duration is not correct ([`dbdc25c`](https://github.com/neoave/mrack/commit/dbdc25ceae5a5e7985d1ece7eb253f0729b560fa))
* Ssh action crashes as it misses global_context ([`a210f6e`](https://github.com/neoave/mrack/commit/a210f6eef895441198706b44697f7c3638630e94))
* Log error when ssh fails after provisioning ([`76af86e`](https://github.com/neoave/mrack/commit/76af86ebe85a1ba500c89fed48fb3bf55cc692bd))
* Do not use compression when trying ssh to machine ([`26d89be`](https://github.com/neoave/mrack/commit/26d89be9e643d7a9b8ea0ca929331b77af165bf9))
* Mrack ssh action needs host.host_id for podman ([`c4daabd`](https://github.com/neoave/mrack/commit/c4daabda53bcace5a5d69dbe6e24f9fd62991bf2))
* Use pubkey instead of keypair for beaker ([`abc2a84`](https://github.com/neoave/mrack/commit/abc2a843c872a04a32908c931e5302def9879ca0))
* Podman provider logger does not use Podman prefix ([`ef7dd59`](https://github.com/neoave/mrack/commit/ef7dd598d4ba9b86b5ba2037acaf06190e88289e))

### Documentation
* Add example provisioning config for podman ([`f54b2e9`](https://github.com/neoave/mrack/commit/f54b2e96d24e91c57c161f1cf8c1f62cde1b7899))
* Fix typo in docstring ([`255032b`](https://github.com/neoave/mrack/commit/255032b9ed38c083250cffae710f6330a543414e))

## v0.9.0 (2021-04-19)
### Feature
* Enable config drive in OpenStack ([`3cdb54b`](https://github.com/neoave/mrack/commit/3cdb54b0ce64c97fb884c9d83ba46576fa8bbae7))

## v0.8.0 (2021-04-15)
### Feature
* Use ssh to check VM availability after provisioning ([`7af47ec`](https://github.com/neoave/mrack/commit/7af47ec4a161c6b6e7f521d06ea3a23ca859ed51))

### Documentation
* Add info on how to install on Fedora ([`90a52bc`](https://github.com/neoave/mrack/commit/90a52bc2661598da698f40c0a1cd5e730ec65bed))

## v0.7.1 (2021-03-23)
### Fix
* Update project homepage ([`1a1a0c2`](https://github.com/neoave/mrack/commit/1a1a0c2082ede76c74a14ccee0a7e364a2cc0a5d))

### Documentation
* Add copr build badge and fix some typos ([`f85e236`](https://github.com/neoave/mrack/commit/f85e2366ee3fb5f952a03291bd4768099f298d23))

## v0.7.0 (2021-03-22)
### Feature
* Add RPM spec file ([`17aebbb`](https://github.com/neoave/mrack/commit/17aebbbb41453cace25258695eef795320477869))
* OpenStack: increase polling time based on number of hosts ([`7558969`](https://github.com/neoave/mrack/commit/755896999e17b4b94336349ec98438a9bd532f3c))

### Fix
* Handle ServerError in all Openstack calls ([`585543a`](https://github.com/neoave/mrack/commit/585543a476debfbc9a2106e9fee2ed25014b7c82))
* Handle timeout state and treat it as an error ([`a6b9738`](https://github.com/neoave/mrack/commit/a6b9738749d3392fae99d4d1b3df9e19fc118c89))
* Podman ansible inventory and status_map ([`503a680`](https://github.com/neoave/mrack/commit/503a6802418bf8ac33cf08c0fd3468b13e7d5b74))
* Fix pylint isssues and reuse existing methods ([`788b2ff`](https://github.com/neoave/mrack/commit/788b2ff520f26a7e50601d8c450ad74c2c7a9feb))
* If mrack is run first time db may not exist ([`bd51176`](https://github.com/neoave/mrack/commit/bd51176b025390e32d3012aec26c56e055771be0))
* Require beaker version with support for python 3.9 ([`6f22bea`](https://github.com/neoave/mrack/commit/6f22bea70c963ad717b8c8ce53bb85f848b0be88))
* OpenStack provider does not crash if no credentials are provided ([`6115c1a`](https://github.com/neoave/mrack/commit/6115c1af4e8a8cb73624c7182259161e797910aa))
* Provider: await abort_and_delete ([`8f361f5`](https://github.com/neoave/mrack/commit/8f361f5525bbfc9b3fba574825518dbc1ad3c2cd))

## v0.6.0 (2021-01-27)
### Feature
* Podman support in SSH action ([`10a43f1`](https://github.com/neoave/mrack/commit/10a43f1bdaa328fad0a4fb2ad4ae57cd7ef41878))
* Podman support in Ansible inventory ([`f5dbed9`](https://github.com/neoave/mrack/commit/f5dbed9fc61ab474220fbc655246e1aafe03f73b))
* Add Podman provider ([`ef35545`](https://github.com/neoave/mrack/commit/ef3554547eada23a65f0d40b7ecd9f51cb17eeeb))

### Fix
* Handle ServerError in OpenStack provisioning ([`46048c0`](https://github.com/neoave/mrack/commit/46048c01f6ae3224e9d49e711e610b28497f63df))
* More verbose print about available networks ([`824b359`](https://github.com/neoave/mrack/commit/824b3594d152b061c36ade3f382b8908272030f9))

## v0.5.2 (2020-12-21)
### Fix
* Mrack eh add no longer complains about coroutine 'eh' not awaited ([`7dbdd6a`](https://github.com/neoave/mrack/commit/7dbdd6a6f54331078907081527c944dd5899ab19))
* Error for non authorized user reading image ([`a5c355d`](https://github.com/neoave/mrack/commit/a5c355da2a0b7d37e5865fb3a78558c26b163b3f))
* Mrack.conf '~' causes no such file or directory ([`4b8dee8`](https://github.com/neoave/mrack/commit/4b8dee8d710a9a0d978561733dfcd898d96c2c67))
* Load possible missing image specified in metadata ([`19103c0`](https://github.com/neoave/mrack/commit/19103c0a44311ba95409560877a48e0585795c01))

## v0.5.1 (2020-12-14)
### Fix
* Set user for Windows host in pytest-multihost config ([`e36138c`](https://github.com/neoave/mrack/commit/e36138c8f80e18eb235981ffd7eeb4840cac0855))

## v0.5.0 (2020-12-11)
### Feature
* Retry provisioning strategy ([`3683d3c`](https://github.com/neoave/mrack/commit/3683d3c20f917f57de7f88d0b3e9e4fea5ff0398))

### Fix
* Openstack: log which server is being provisioned ([`d89aa5d`](https://github.com/neoave/mrack/commit/d89aa5d20192c75560f7bb0beffb3027b0431a47))
* Pytest-multihost: handle unresolvable IP into DNS ([`56c716e`](https://github.com/neoave/mrack/commit/56c716ec910028604e2ecaf42124e7e1f6061324))
* Fix making ssh_key_filename absolute for default behavior. ([`6b5ea95`](https://github.com/neoave/mrack/commit/6b5ea951f132336fcde50b53a97c7b4338eb0099))
* Remove double status translation in parse_errors ([`e5da9cd`](https://github.com/neoave/mrack/commit/e5da9cd6403d67f75d429b3207e11555dd90e437))

## v0.4.0 (2020-12-07)
### Feature
* Output file paths configurable in mrack config ([`1761baf`](https://github.com/neoave/mrack/commit/1761baf1da0c75e8bb86ec423e3b563bdfb18871))
* Simple way to add hosts into /etc/hosts file ([`da24ac5`](https://github.com/neoave/mrack/commit/da24ac55a3189512c98884eb30f1b5a6ad4dd46a))

### Fix
* Use meta_ prefix for parent domain ([`aaeeb58`](https://github.com/neoave/mrack/commit/aaeeb58c0682dbd7be9db94dcb7469c07e6243eb))
* Add missing annotations for mypy ([`2427b15`](https://github.com/neoave/mrack/commit/2427b15ddd12b4d7813a51b3b276b8affd42259b))
* Remove deprecated flag --recursive from Makefile ([`48937f3`](https://github.com/neoave/mrack/commit/48937f38a3b8e2780d39539c513187591b9a953d))
* Move common methods to transfromer.py ([`4ea839e`](https://github.com/neoave/mrack/commit/4ea839e560a3d11662d2b65309993652b4cd44bd))
