# Changelog

<!--next-version-placeholder-->

## v1.12.1 (2022-11-24)
### Fix
* Make db file and provisioning file optional ([`9449082`](https://github.com/neoave/mrack/commit/94490824e8e6d3713328e08b99acb2a8a83623f8))
* Use MrackError in action Up to catch all possible mrack errors at once ([`990224b`](https://github.com/neoave/mrack/commit/990224bd326ee2a70021a558a46596005121159b))
* Validate ownership and lifetime only for AWS and OpenStack ([`111d481`](https://github.com/neoave/mrack/commit/111d481e9bac692854a1b2764a760608b7fc2046))

## v1.12.0 (2022-11-14)
### Feature
* **aws:** Add owner/lifetime info in VM's metadata ([`ed9e977`](https://github.com/neoave/mrack/commit/ed9e977f4f56c5cc5cda6f0b4ad0f09cdaab89b9))
* **openstack:** Add owner/lifetime info in VM's metadata ([`e33038e`](https://github.com/neoave/mrack/commit/e33038e4de2fcca8d58564508b1d6786fbe8d01b))

### Fix
* Integration test_actions test fixes ([`07682c1`](https://github.com/neoave/mrack/commit/07682c148a7fe7d40b8e5761e9845cdd85972013))
* Do not use deprecated asyncio.coroutine wrapper ([`c66fef7`](https://github.com/neoave/mrack/commit/c66fef729754d3f28f8014e901524184bba5e18d))

## v1.11.0 (2022-11-03)
### Feature
* **AWS:** Add multiple subnet support & IPs availability check ([`742ed9c`](https://github.com/neoave/mrack/commit/742ed9cf2e6ffe32575584ab405aa034f8049128))

### Fix
* **mrack.spec:** Fix the location for mrack.egg-info ([`9a998bc`](https://github.com/neoave/mrack/commit/9a998bce750c09aa1bd2d2f0007cc67b729ab8f3))
* **mrack.spec:** Cli package files and deps ([`f76c31a`](https://github.com/neoave/mrack/commit/f76c31a7fdd297ae121f2001980742783cf62687))
* **Podman:** Fix action ssh import failing if podman provider not found ([`87c397e`](https://github.com/neoave/mrack/commit/87c397eb0fd1c84384bda7dfe28e446d35158764))
* **mrack.spec:** Remove unecessary statement ([`dbb43f3`](https://github.com/neoave/mrack/commit/dbb43f30a0a978ce8570f1d3d23efb28cfd440a5))

## v1.10.0 (2022-10-26)
### Feature
* **OpenStack:** Pick from all networks based on load ([`317c2ac`](https://github.com/neoave/mrack/commit/317c2ac8c11580b078f306192309a0637522aed5))

### Fix
* Update paths in specfile and python_provide ([`5262bca`](https://github.com/neoave/mrack/commit/5262bca0782e343927aa0c5ee2be63c10f9c9e0d))
* **utils:** Add encoding to open functions ([`e28e044`](https://github.com/neoave/mrack/commit/e28e044e9398c380d64ef0980eab4239881f98d1))
* **Podman:** Add encoding to open function ([`84cd4dc`](https://github.com/neoave/mrack/commit/84cd4dcf53d5888c6537fdb5f3bd4ec99c83583c))
* **Beaker:** Add encoding to open when opening ssh key ([`71ef2f1`](https://github.com/neoave/mrack/commit/71ef2f102f8110f84c12914a1bbd2308a5f592b2))

## v1.9.1 (2022-10-20)
### Fix
* Add CHANGELOG.md to MANIFEST.in ([`64fa546`](https://github.com/neoave/mrack/commit/64fa546e9fc24e30ea655c2ee211f5b348272929))
* Update spec to match fedora community standard ([`91726d7`](https://github.com/neoave/mrack/commit/91726d786414620b5556165e7a90adc672bfc3d2))
* **Beaker:** Traceback when hub is not accessible at session creation ([`18f6b78`](https://github.com/neoave/mrack/commit/18f6b7898130cf8c5c7e4c392b1d4ad72b15f1ba))
* **Beaker:** Connection to hub timing out ([`9c258d8`](https://github.com/neoave/mrack/commit/9c258d8bf4eea248e8220d0b697ea0126e24b23b))

## v1.9.0 (2022-10-12)
### Feature
* Split mrack spec to multiple packages ([`1709af0`](https://github.com/neoave/mrack/commit/1709af06150c567f91e44584375bddf79b993807))

### Documentation
* Update installation steps based on mrack package division ([`48b16f4`](https://github.com/neoave/mrack/commit/48b16f45acf96e9129507037e2fcac1a0abf0045))

## v1.8.1 (2022-10-10)
### Fix
* Add missing split support for transformer ([`d22d360`](https://github.com/neoave/mrack/commit/d22d36071dc922e088ede8df63576988e2c8bd52))

## v1.8.0 (2022-10-10)
### Feature
* Add support to dynamically load providers ([`607c99c`](https://github.com/neoave/mrack/commit/607c99c7cd6aef5fdf10dd4f634fe3c99543ff96))

### Fix
* Use encoding when opening files in setup.py ([`3ef4b92`](https://github.com/neoave/mrack/commit/3ef4b92ac2751cbc2144e86bb12ae56da8833bae))

## v1.7.0 (2022-09-20)
### Feature
* **Beaker:** Specify ks_append per host or config ([`59ba489`](https://github.com/neoave/mrack/commit/59ba489e70e7c83fc56d006ca0073d010dd4564f))
* **Beaker:** Support configurable jobxml specs ([`e9b6fa7`](https://github.com/neoave/mrack/commit/e9b6fa7a1c7bd550953d5905f5fe262787559070))
* **Beaker:** Support custom configurable ks_meta values ([`e167443`](https://github.com/neoave/mrack/commit/e16744346169ca375cea005c9e5989ff30bfc43b))

### Fix
* **Beaker:** Do not throw an Exception when not authenticated ([`d1b794b`](https://github.com/neoave/mrack/commit/d1b794b9622b27a6c776e9699bb21bb7032db173))
* Issue when searching for value when dict_name == attr ([`98255c7`](https://github.com/neoave/mrack/commit/98255c78ec52053c508170238951daff90f4f5c6))
* Beaker log polling to logfile instead of console ([`be560d9`](https://github.com/neoave/mrack/commit/be560d9b59fae0f8d142e737db99d7077ee8cf92))

## v1.6.0 (2022-07-27)
### Feature
* **pytest-multihost:** Arbitrary attributes for hosts ([`d0c28f6`](https://github.com/neoave/mrack/commit/d0c28f62dad1cb8cf99704973209102cc0deab2f))
* **ansible-inventory:** Host arbitrary attributes ([`65057e7`](https://github.com/neoave/mrack/commit/65057e734db89531d10ee02ec8b763f25578b840))
* Copyign meta_ attributes from host to ansible inventory ([`3da517c`](https://github.com/neoave/mrack/commit/3da517c18701999c43638a67835f09938272badc))

### Fix
* **pytest-multihost:** Crash when group is not defined ([`d337a7b`](https://github.com/neoave/mrack/commit/d337a7bbec98f9385fa7f86fb944e032b8b60878))
* **pytest-multihost:** Crash when mhcfg is missing in prov. config ([`d6e3483`](https://github.com/neoave/mrack/commit/d6e3483f509fb6fe5b5c0759f0d51e0db9bd28b5))

## v1.5.0 (2022-07-08)
### Feature
* **AWS:** Create unique instance name with the tag ([`b3e31e0`](https://github.com/neoave/mrack/commit/b3e31e0ab614c795ea34ef250e118ffa4905b536))

## v1.4.1 (2022-06-17)
### Fix
* Creating inventory with None host ([`7489240`](https://github.com/neoave/mrack/commit/748924088ab0416d8ff1d9381cb5da5f262a2af9))

## v1.4.0 (2022-05-05)
### Feature
* **AWS:** Move tagging into creation request itself ([`b4fae6b`](https://github.com/neoave/mrack/commit/b4fae6bceabfeffa2fe47efae5a3ee87aba6da74))

### Fix
* **AWS:** Return False when ValidationError is raised ([`bb5594b`](https://github.com/neoave/mrack/commit/bb5594b4028bc06e71f5167615acbb9ac3cd7e32))

## v1.3.1 (2022-04-05)
### Fix
* Image transformer none value in requirements ([`cb5290d`](https://github.com/neoave/mrack/commit/cb5290d7c4864dccf94c9c126487e9436fea8682))

### Documentation
* Update the _get_image() method doc string ([`6b88058`](https://github.com/neoave/mrack/commit/6b8805880e2e9bfcb26dca4d9628254e4ad896cf))

## v1.3.0 (2022-04-01)
### Feature
* **Beaker:** Support distro variant configuration ([`e568507`](https://github.com/neoave/mrack/commit/e568507ec233fe232109717c68abb4a86b14948d))
* **Openstack:** Printout compose_id when using -latest image pointer ([`bb91893`](https://github.com/neoave/mrack/commit/bb918931d76b2cb031094398eb5e6970f2ef42ad))
* **aws:** Delete volumes on termination ([`d90375e`](https://github.com/neoave/mrack/commit/d90375ebf571efb4f3b3d6cbf34dc741910fa95a))
* Possibility to disable host DNS resolution in outputs ([`3fbd133`](https://github.com/neoave/mrack/commit/3fbd133e14f7397ccf261edaf05470664681fc0a))
* **aws:** Request spot instances ([`25576cb`](https://github.com/neoave/mrack/commit/25576cbb9be0e8e258e8e5fc7209acd17a7e641d))
* **aws:** Defining AMIs by tags ([`a04497c`](https://github.com/neoave/mrack/commit/a04497c6003445241d96b19218a775a106db7da5))

### Fix
* Use host['os'] as default value when distro is not found ([`253a380`](https://github.com/neoave/mrack/commit/253a3809887b1024b0ee09c1bc47a40869f35e8c))
* **Virt:** Remove password when provisioning windows ([`e3a976a`](https://github.com/neoave/mrack/commit/e3a976a75a6e13659277936c690a5abec1ae6faa))

### Documentation
* **aws:** Add missing examples to provisioning config ([`e00e149`](https://github.com/neoave/mrack/commit/e00e1499364fef1b60a81417d485250817108991))

## v1.2.0 (2021-12-15)
### Feature
* **aws:** Support for PrivateIpAddress ([`8b7ed70`](https://github.com/neoave/mrack/commit/8b7ed705a58d533b7c5a2115b595d4e4e3e8c2e4))
* **aws:** Subnet support ([`01c6bf5`](https://github.com/neoave/mrack/commit/01c6bf5a315ce4df73952086645911781516117d))
* **aws:** Multiple security groups ([`1340813`](https://github.com/neoave/mrack/commit/13408133310b80a4163aef21825ebaa861d9d0dc))
* **Openstack:** Poll openstack load when running can_provision() ([`8ef8312`](https://github.com/neoave/mrack/commit/8ef831297a99c47eb270a6ea4f5e33ed20c8caee))
* Search also provider config for username ([`8419698`](https://github.com/neoave/mrack/commit/84196984b85f7743cab3d148827d8417cefef11f))
* Find_value_in_config_hierarchy utility method ([`c05ab58`](https://github.com/neoave/mrack/commit/c05ab586ea61cb55b5ff211a7486be0c3ae74761))

### Fix
* SSH action - do not redirect to PIPEs ([`8992629`](https://github.com/neoave/mrack/commit/89926294b663c43edddea4a7c92503e407c92447))
* Prepare_provisioning now shall return bool value ([`7e47c6f`](https://github.com/neoave/mrack/commit/7e47c6fd18015826575b8a844d95086502022e98))
* **Virt:** Handle traceback when image is not accessible ([`a0de847`](https://github.com/neoave/mrack/commit/a0de8475659153fd3fb39133a34f56729d0e561c))

## v1.1.1 (2021-11-25)
### Fix
* Add domain name for fqdn if host has short name ([`a870f7f`](https://github.com/neoave/mrack/commit/a870f7f0fbe5117d08ffda6f789b09ab53018ece))

## v1.1.0 (2021-11-23)
### Feature
* Add shortname in Ansible inventory output ([`ea76cbc`](https://github.com/neoave/mrack/commit/ea76cbc07750ffb3e324919a4089bbba88470121))
* Add group specific ssh config possibility ([`f0e32d8`](https://github.com/neoave/mrack/commit/f0e32d8aab1e22126b3d5e1b3b82afb0082a5ad6))
* Make post provisioning ssh check configurable ([`c419dc2`](https://github.com/neoave/mrack/commit/c419dc29fdc98ce8aef1dcc13f5ca40f511375a9))
* **Beaker:** Add parsing of HostRequires to the job ([`e696872`](https://github.com/neoave/mrack/commit/e69687234c26c518de159a082f4bfcb1df328860))
* **Podman:** Add possibility to run post provisioning commands ([`ea488fc`](https://github.com/neoave/mrack/commit/ea488fc5e367b5d33e074585e48197e050c7d0fb))

### Fix
* **OpenStack:** Do not raise exception when using unavailable network ([`6c31bb6`](https://github.com/neoave/mrack/commit/6c31bb6f24132051ba7be777a59ec7652cf28f67))
* **openstack:** Use shortnames for Windows vm names ([`d4a1bec`](https://github.com/neoave/mrack/commit/d4a1bec262041d101d555264382f852faf7190c1))
* **AWS:** Fix provision of non-existing ami ([`0971479`](https://github.com/neoave/mrack/commit/09714792de24877fe1fa59e8d51fbfd01a7c75ec))
* **Beaker:** Change host status to error when task did not pass ([`90cd628`](https://github.com/neoave/mrack/commit/90cd6281aba071fe80705dc89adb0dcc721b40d9))
* **Podman:** Fix the exception handling when container creation is failing ([`6df9605`](https://github.com/neoave/mrack/commit/6df9605c05a1a59bc09715e53edf97126bdb78e0))
* **Podman:** Raise an exception when image failed to pull ([`ed79732`](https://github.com/neoave/mrack/commit/ed79732a12b47e28d3228e14cf0ea725e80360df))

### Documentation
* Add post-provisioning ssh check docs ([`ef0e339`](https://github.com/neoave/mrack/commit/ef0e339d25eb735d3825493e815376cd5c6f106b))
* Fix toctree for guides ([`d9075f9`](https://github.com/neoave/mrack/commit/d9075f91304d1d31491bb37e8cde0a671597b230))

## v1.0.0 (2021-09-03)
### Feature
* Use global context instead of dictionary as ctx for click ([`9f38a3c`](https://github.com/neoave/mrack/commit/9f38a3c77cf3874326866247d40ff696a5c24a4b))
* Use GlobalContext class in runtime ([`2c23c97`](https://github.com/neoave/mrack/commit/2c23c9714900e727f845c99ef675b7a8a9ac0147))
* Log message when job is not changing state ([`9e50f46`](https://github.com/neoave/mrack/commit/9e50f468fd58912a76ec6b19312f87f5c9f46252))
* Improve logging for openstack and ssh subprocess ([`7594732`](https://github.com/neoave/mrack/commit/7594732cbbf46c5cc2e4ef07c3fee35c02ee5081))
* Do not destroy if there are not success hosts ([`84dce71`](https://github.com/neoave/mrack/commit/84dce715bb181adfb5bdc2d285e73c837b18172e))
* **Virt:** Support testcloud v0.6.0 and later ([`6403bd6`](https://github.com/neoave/mrack/commit/6403bd64b63a52e187d447ec702e9e6253ef02c8))
* **Virt:** Log the tracebacks for Virt provider ([`d508aff`](https://github.com/neoave/mrack/commit/d508aff342fbbfceb4334e2068ab092d6fe6662d))
* Use max_retry across providers to define retry count ([`d8caab5`](https://github.com/neoave/mrack/commit/d8caab5fa96cb74410193c8c1cc7e927d776c9a9))
* **Beaker:** Use timeout instead of number of retries ([`00330ef`](https://github.com/neoave/mrack/commit/00330efa500d1c2d2de796004bde04709ac2ac92))
* Add possibility to change strategy per provider in provisioning config ([`ee8cb36`](https://github.com/neoave/mrack/commit/ee8cb36e5e6c0ecd9e3885676d3b16a91f2be140))

### Fix
* **AWS:** Catch traceback when credentials are missing ([`1dc975e`](https://github.com/neoave/mrack/commit/1dc975e027039d46c8a36e6b7d6f2cd70f9d0340))
* **Podman:** Handle premature deletion ([`0353d89`](https://github.com/neoave/mrack/commit/0353d895c83699e6f07af12416b29195d2059a5d))
* **Beaker:** Delete_host handle premature deletion ([`c57ff28`](https://github.com/neoave/mrack/commit/c57ff287ed506d9c4b353f7439230cc4dbdc0b54))
* **Virt:** Create more readable output and move to debug ([`04d4d4a`](https://github.com/neoave/mrack/commit/04d4d4a3e9ceb9583af980a69df94071e3f2c1eb))
* Do not end provisioning if there are no resources ([`4cbdc50`](https://github.com/neoave/mrack/commit/4cbdc501085d5f5ae8f819f828a30bcea59d940e))
* **OpenStack:** Add exception handling to init of provider ([`5ac9eaf`](https://github.com/neoave/mrack/commit/5ac9eafba2e368015a6bffd3d1d5f9e81a3e40aa))
* **Beaker:** Handle Fault exception when contacting hub ([`02cfd66`](https://github.com/neoave/mrack/commit/02cfd6652ba938df1b9239dd5b84d710867e5ec7))
* Attempts should be greater than max_retry ([`e29e92d`](https://github.com/neoave/mrack/commit/e29e92d78b6f9bdf7b0dd4fb79e0c98eb921954c))
* Add missing '/' to log message while deleting ([`65e4ad0`](https://github.com/neoave/mrack/commit/65e4ad094bcced6434c2e0510354238fc71d8b9c))
* Make static provider more verbose ([`9c6b217`](https://github.com/neoave/mrack/commit/9c6b21795b72bb4cf554ccd3929d41cae7dc2d54))
* Destroy active VMs after other providers fail ([`7e58e5d`](https://github.com/neoave/mrack/commit/7e58e5d9622e5c714c1e5e6659ffee89680a9b05))
* Add verbosity to virt and podman resource deletion ([`c7653fb`](https://github.com/neoave/mrack/commit/c7653fb22ed37142fb80573b77b24de8ec4f8501))
* **Beaker:** Beaker job link add missing '/' in url ([`4a33072`](https://github.com/neoave/mrack/commit/4a330725d1b6ab410a0610fd8662c0fa86af2f43))
* **Virt:** Add de-sync state and fix error parsing. ([`5875883`](https://github.com/neoave/mrack/commit/5875883e89f85484cb3b48dc8bdfae8cc6f6b37c))
* Do not remove error hosts when doing last retry ([`6201042`](https://github.com/neoave/mrack/commit/6201042d34e352ead8ce6369f43a5f8e8622f2b8))
* Fail without traceback when job times out ([`5aa156e`](https://github.com/neoave/mrack/commit/5aa156e44fe2a1589879d78ec8cac9a8d7cc5f2e))
* Use SPECS and ERROR_OBJ keys to create fault object ([`2de1f6f`](https://github.com/neoave/mrack/commit/2de1f6f350decff116f80b519ed4e53cd2b75aaa))
* Unite providers's create server to return tuple ([`5f9ba63`](https://github.com/neoave/mrack/commit/5f9ba633ef1ddafa07105e6f8a0667f057a09786))
* Do not proceed to ssh check if port is not open ([`ea94a8e`](https://github.com/neoave/mrack/commit/ea94a8e53dd56e306e0131404508476a0929fe67))

### Breaking
* Release 1.0.0 candidate ([`2df06d7`](https://github.com/neoave/mrack/commit/2df06d7cdc0b9ce008bc40ad25708adb24564a68))
* Using GlobalContext class in runtime allows us to use mrack actions without parameters Up/Destroy/... which simplify the workflow in scripts so mrack can be used as library in python automation. ([`2c23c97`](https://github.com/neoave/mrack/commit/2c23c9714900e727f845c99ef675b7a8a9ac0147))

### Documentation
* Add docs about usage mrack as lib ([`2df06d7`](https://github.com/neoave/mrack/commit/2df06d7cdc0b9ce008bc40ad25708adb24564a68))
* Fix title underline too short ([`225cff4`](https://github.com/neoave/mrack/commit/225cff4d0c4c4d745844ef8b591f99628f6d82bc))
* Add documentation to strategy switch ([`5cd1a8a`](https://github.com/neoave/mrack/commit/5cd1a8a6e83a5eb8cef04ac8d88108c533a66f28))

## v0.14.0 (2021-07-01)
### Feature
* **Beaker:** Add distro tag from provisioning conf ([`762e88a`](https://github.com/neoave/mrack/commit/762e88a00c79be2c1194a459a7404f2eb3513e19))

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
