# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.9.3](https://github.com/IllumiDesk/illumidesk/compare/v0.9.2...v0.9.3) (2020-09-17)

### 0.9.2 (2020-09-17)


### Features

* Add a postgres service for labs ([#75](https://github.com/IllumiDesk/illumidesk/issues/75)) ([b733c0b](https://github.com/IllumiDesk/illumidesk/commit/b733c0b4015754d85788629e51a7594154db6f0e))
* Add announcement for pilot environments ([#317](https://github.com/IllumiDesk/illumidesk/issues/317)) ([3c1a9d2](https://github.com/IllumiDesk/illumidesk/commit/3c1a9d264499d9a6340f4438ba98227a03b26b1e))
* Add course template and use setup-course for course config ([#236](https://github.com/IllumiDesk/illumidesk/issues/236)) ([2f229e3](https://github.com/IllumiDesk/illumidesk/commit/2f229e316f317d94dfaa13e2a874a983792bb2cf))
* Add grader header and footer templates ([#305](https://github.com/IllumiDesk/illumidesk/issues/305)) ([f2be08a](https://github.com/IllumiDesk/illumidesk/commit/f2be08abbbd29871c63c5273e0eb1dd5fb34564c))
* Add java dependencies and jupyter kernel ([#187](https://github.com/IllumiDesk/illumidesk/issues/187)) ([5800408](https://github.com/IllumiDesk/illumidesk/commit/5800408c1285a669f3ed95d53e4c12fc799d0800))
* Add option to shutdown server upon logout ([#322](https://github.com/IllumiDesk/illumidesk/issues/322)) ([f751c67](https://github.com/IllumiDesk/illumidesk/commit/f751c6757d6589711327e2f01516cece33e8b1a4))
* Add plotly dependencies ([#59](https://github.com/IllumiDesk/illumidesk/issues/59)) ([59b8f1f](https://github.com/IllumiDesk/illumidesk/commit/59b8f1f992251bdad4bd30cc7c79be5b01b6edb4))
* Add support to setup stack with AWS EFS-based mounts ([#159](https://github.com/IllumiDesk/illumidesk/issues/159)) ([d50d311](https://github.com/IllumiDesk/illumidesk/commit/d50d311faa7274c71b4bb5b7e88073eb4215debc))
* Adds lms_user_id in custom_fields ([#121](https://github.com/IllumiDesk/illumidesk/issues/121)) ([aaa98bd](https://github.com/IllumiDesk/illumidesk/commit/aaa98bdc2725838a6c48e45cf1b3bad75e745ebf))
* Automated assignment creation with LTI 1.3 ([#260](https://github.com/IllumiDesk/illumidesk/issues/260)) ([170dc92](https://github.com/IllumiDesk/illumidesk/commit/170dc923a864bebf4fb3a6bf0d2a56284fb7390e))
* Automated assignment creation with LTI11 ([#265](https://github.com/IllumiDesk/illumidesk/issues/265)) ([beadb21](https://github.com/IllumiDesk/illumidesk/commit/beadb216f375c6a007d16471d14c7c53d91b12e4))
* Clone and merge code located in remote git-based repositories with workspace launches ([#153](https://github.com/IllumiDesk/illumidesk/issues/153)) ([19eb3d7](https://github.com/IllumiDesk/illumidesk/commit/19eb3d7f82424bfdaf604c2ff8b681b148237d99))
* Complete Julia dynamic config setup ([#222](https://github.com/IllumiDesk/illumidesk/issues/222)) ([e5ebea5](https://github.com/IllumiDesk/illumidesk/commit/e5ebea52f0b4d16ded03a6c9604d490311c8e8f1))
* Create a shared folder for graders and students ([#281](https://github.com/IllumiDesk/illumidesk/issues/281)) ([c0d86a1](https://github.com/IllumiDesk/illumidesk/commit/c0d86a18ab2cbf086436cb7aefb6995fb3b3e354))
* Custom base url configuration ([#231](https://github.com/IllumiDesk/illumidesk/issues/231)) ([5c50458](https://github.com/IllumiDesk/illumidesk/commit/5c50458843d46bc30fac819cccbb00cb03258118))
* DeepLinking request support to allow file selection ([#308](https://github.com/IllumiDesk/illumidesk/issues/308)) ([828b008](https://github.com/IllumiDesk/illumidesk/commit/828b0086bb3420f6d2ecde0c21d3d27dec0f25c7))
* Do not use initial course service when LTI is enabled ([#53](https://github.com/IllumiDesk/illumidesk/issues/53)) ([2ab217e](https://github.com/IllumiDesk/illumidesk/commit/2ab217efa064c889f63773549d34fbf3db0cd7d8))
* Fixes the use of next url with LTI 1.3 ([#244](https://github.com/IllumiDesk/illumidesk/issues/244)) ([2f90f8e](https://github.com/IllumiDesk/illumidesk/commit/2f90f8e4ac41eb6a2c41be0abf4e6bda04a57560))
* Handle unique usernames with the Canvas LMS ([#268](https://github.com/IllumiDesk/illumidesk/issues/268)) ([7d26c74](https://github.com/IllumiDesk/illumidesk/commit/7d26c74fbf2502fe9fc8bac9073dbf0c5a02ca70))
* Include users with TeachingAssistant role in the formgrade group ([#271](https://github.com/IllumiDesk/illumidesk/issues/271)) ([6b769be](https://github.com/IllumiDesk/illumidesk/commit/6b769be00f24e02c92ab327349223b0caf96ed76))
* Initialize shared directory with git by default ([#312](https://github.com/IllumiDesk/illumidesk/issues/312)) ([ae0378a](https://github.com/IllumiDesk/illumidesk/commit/ae0378a770a2f51f0ccb022a6958095f1ef65fef))
* Pull workspace images with ansible-playbook from registry ([#229](https://github.com/IllumiDesk/illumidesk/issues/229)) ([757006b](https://github.com/IllumiDesk/illumidesk/commit/757006b881fcc59abf963644979a55d5836d1750))
* Run JupyterHub with  python 3.8 ([#12](https://github.com/IllumiDesk/illumidesk/issues/12)) ([cc07bd9](https://github.com/IllumiDesk/illumidesk/commit/cc07bd919d57d698f0a225ba86f791f4a16ff7af))
* Segregate public key endpoint from config endpoint for LTI 1.3 (public key) ([#171](https://github.com/IllumiDesk/illumidesk/issues/171)) ([e2dbca7](https://github.com/IllumiDesk/illumidesk/commit/e2dbca7f600e2ed0718a71d6f917cf8f2f38423f))
* Set admin user with ansible configuration ([#213](https://github.com/IllumiDesk/illumidesk/issues/213)) ([eb7981f](https://github.com/IllumiDesk/illumidesk/commit/eb7981f3cc764d10c0d81f1387260cfdf9784262))
* Share Plotly dashboards from end-user notebooks ([#96](https://github.com/IllumiDesk/illumidesk/issues/96)) ([e3489e4](https://github.com/IllumiDesk/illumidesk/commit/e3489e4e3b9c94cdd75a56ba3a4ec00796b9df63))
* Shares folders and files only for courses the user is enrolled in ([#320](https://github.com/IllumiDesk/illumidesk/issues/320)) ([37173b6](https://github.com/IllumiDesk/illumidesk/commit/37173b6824c4d9ef8bcae50ae16982dfd4223b7f))
* Simplify setup with make and new inventory file ([#8](https://github.com/IllumiDesk/illumidesk/issues/8)) ([019687e](https://github.com/IllumiDesk/illumidesk/commit/019687ed9325b822ec948c3ab7be9ef51bf67a4a))
* Support additional workspace types ([#164](https://github.com/IllumiDesk/illumidesk/issues/164)) ([6c13bc9](https://github.com/IllumiDesk/illumidesk/commit/6c13bc95feb632727e6df10ed9f6c398d3b66136))
* Upate settings and readme ([#324](https://github.com/IllumiDesk/illumidesk/issues/324)) ([7b5179a](https://github.com/IllumiDesk/illumidesk/commit/7b5179a984164124152c16643123b1368c2c3837))
* Update default JupyterHub configuration ([#299](https://github.com/IllumiDesk/illumidesk/issues/299)) ([552a8c5](https://github.com/IllumiDesk/illumidesk/commit/552a8c573dfab652fdf352c51586f59516cc5b41))
* Update dockerspawner configuration settings ([#288](https://github.com/IllumiDesk/illumidesk/issues/288)) ([a8f4dac](https://github.com/IllumiDesk/illumidesk/commit/a8f4dacd6f6891373de1cf0fb213ce5385cb71de))
* Update nbgrader config file to include the code stub for julia language ([#181](https://github.com/IllumiDesk/illumidesk/issues/181)) ([add1b3c](https://github.com/IllumiDesk/illumidesk/commit/add1b3c90a394dd91cccc5b4f2dac40c3e830208))
* Update Services dropdown in JupyterHub's control panel ([#46](https://github.com/IllumiDesk/illumidesk/issues/46)) ([f1101c5](https://github.com/IllumiDesk/illumidesk/commit/f1101c59aa5f236c02909b7147ac7366a5a558ac))
* **core:** Add grades submission feature using LTI 1.1 ([#38](https://github.com/IllumiDesk/illumidesk/issues/38)) ([10d1a63](https://github.com/IllumiDesk/illumidesk/commit/10d1a631a4dd16637cfa917beb940267a63bcfd4))
* **core:** Dynamic course and user setup with LTI 1.1 ([#18](https://github.com/IllumiDesk/illumidesk/issues/18)) ([dfa21c0](https://github.com/IllumiDesk/illumidesk/commit/dfa21c0498fd082a7bd9bcd86d30a036a872c61c))


### Bug Fixes

* Add defaults to demo_* env vars for FirstUse  authenticator ([#143](https://github.com/IllumiDesk/illumidesk/issues/143)) ([e34395a](https://github.com/IllumiDesk/illumidesk/commit/e34395a143e2f16281b2fc5fd28d0e331a7c35ad))
* Add jupyterhub config for LTI 1.1 to task ([#27](https://github.com/IllumiDesk/illumidesk/issues/27)) ([0a21d55](https://github.com/IllumiDesk/illumidesk/commit/0a21d557cde343e3559244c8563bd2b0d3efc531))
* Add missing setup-course image dependencies to install illumidesk packages ([#58](https://github.com/IllumiDesk/illumidesk/issues/58)) ([4ba9fd2](https://github.com/IllumiDesk/illumidesk/commit/4ba9fd25ab6c1bf5a94168881c1784d01eb0923a))
* Add text to clarify assignment name in modal ([#48](https://github.com/IllumiDesk/illumidesk/issues/48)) ([fcfdd22](https://github.com/IllumiDesk/illumidesk/commit/fcfdd225e6816b9bdf0d9e00a76423958e879fcb))
* Copy notebook config to global jupyter --paths location ([#209](https://github.com/IllumiDesk/illumidesk/issues/209)) ([e16cccf](https://github.com/IllumiDesk/illumidesk/commit/e16cccf1ff7b80684a395b64d7a82a2ae2396ebe))
* Determine what authenticator is used to submit grades ([#251](https://github.com/IllumiDesk/illumidesk/issues/251)) ([ff952fc](https://github.com/IllumiDesk/illumidesk/commit/ff952fc0d05dc250ebbf6ea8b28fd8fb81090a35))
* Ensure the course directory exists before adding LTI 1.1 control file ([#300](https://github.com/IllumiDesk/illumidesk/issues/300)) ([d90e89d](https://github.com/IllumiDesk/illumidesk/commit/d90e89d4c763bacdafd76c709f2f4f4ed3a1e7cf))
* Fetch all lineitems using pagination ([#328](https://github.com/IllumiDesk/illumidesk/issues/328)) ([6626af4](https://github.com/IllumiDesk/illumidesk/commit/6626af458997d239e4ea788dc960ab45d8cb34d2))
* Fix invalid image tag error when running ansible-playbook ([#122](https://github.com/IllumiDesk/illumidesk/issues/122)) ([4630417](https://github.com/IllumiDesk/illumidesk/commit/4630417d6cdf1965f23723737fe6356283a95620))
* Fix race condition so traefik can load rules.toml correctly ([#29](https://github.com/IllumiDesk/illumidesk/issues/29)) ([e56e423](https://github.com/IllumiDesk/illumidesk/commit/e56e423b1a8b87cca9c3331439e797a3d1251af3))
* Fixes grades submission for moodle ([#41](https://github.com/IllumiDesk/illumidesk/issues/41)) ([d505e99](https://github.com/IllumiDesk/illumidesk/commit/d505e997d4a91c67e882c183ff55760aabfad9b1))
* Handle missing lis arguments with launch requests initiated by learners ([#65](https://github.com/IllumiDesk/illumidesk/issues/65)) ([b83318a](https://github.com/IllumiDesk/illumidesk/commit/b83318a0217a0348861478df916823710f745ac7))
* Java kernel installation with base image ([#190](https://github.com/IllumiDesk/illumidesk/issues/190)) ([61b064c](https://github.com/IllumiDesk/illumidesk/commit/61b064cf9655725108deb1331375adb86e2aaa3c))
* Normalize course label for lti 13 ([#198](https://github.com/IllumiDesk/illumidesk/issues/198)) ([4d5cffe](https://github.com/IllumiDesk/illumidesk/commit/4d5cffe4641b4b114ca8a944438d1ed52d248679))
* Normalize line item strings before submitting grades with LTI 1.3 ([#287](https://github.com/IllumiDesk/illumidesk/issues/287)) ([7df5bc3](https://github.com/IllumiDesk/illumidesk/commit/7df5bc3c86711c9d7d8bd4dcb8d6e41969abbad1))
* Normalize the assignment name and course-id ([#264](https://github.com/IllumiDesk/illumidesk/issues/264)) ([aaf89f2](https://github.com/IllumiDesk/illumidesk/commit/aaf89f27c8154cc3beefd5760063997e30f6e618))
* Register jupyterhub api token ([#86](https://github.com/IllumiDesk/illumidesk/issues/86)) ([9342037](https://github.com/IllumiDesk/illumidesk/commit/9342037f0a584938a7cced02a4a203865fc52819))
* requirements.txt to reduce vulnerabilities ([#273](https://github.com/IllumiDesk/illumidesk/issues/273)) ([ad59405](https://github.com/IllumiDesk/illumidesk/commit/ad594058b314df57c52f254cd99a276ca59df7c9))
* requirements.txt to reduce vulnerabilities ([#63](https://github.com/IllumiDesk/illumidesk/issues/63)) ([72e07b3](https://github.com/IllumiDesk/illumidesk/commit/72e07b39e6ef4d1ffe0737528cc9030ab993e2c8))
* Revert "fix: requirements.txt to reduce vulnerabilities ([#273](https://github.com/IllumiDesk/illumidesk/issues/273))" ([#275](https://github.com/IllumiDesk/illumidesk/issues/275)) ([2997652](https://github.com/IllumiDesk/illumidesk/commit/2997652afddc6c5a40654932e774187a3bdf6969))
* Revert ansible to 2.9.9 ([#70](https://github.com/IllumiDesk/illumidesk/issues/70)) ([833a276](https://github.com/IllumiDesk/illumidesk/commit/833a276a7de59e56ac56e84636894305abaf3c91))
* Set python interpreter in hosts file ([#173](https://github.com/IllumiDesk/illumidesk/issues/173)) ([930b303](https://github.com/IllumiDesk/illumidesk/commit/930b3036c2d3f78a0e6c0d35b4bdbb97f41ebdda))
* Set the course id in auth_state with the normalized value ([#326](https://github.com/IllumiDesk/illumidesk/issues/326)) ([858e0f3](https://github.com/IllumiDesk/illumidesk/commit/858e0f3be1130d03ecdfd2f7a9a89922138a04f0))
* Source directory permissions when adding gradebook ([#270](https://github.com/IllumiDesk/illumidesk/issues/270)) ([579a02c](https://github.com/IllumiDesk/illumidesk/commit/579a02cd15883b76e74552cc0847bf7a64348497))
* Update authentication validation steps ([#168](https://github.com/IllumiDesk/illumidesk/issues/168)) ([c507ca7](https://github.com/IllumiDesk/illumidesk/commit/c507ca71e693af81f17473d4850f5cf9b77929bb))
* Update conditional in lti11 authenticator with Learner string ([#132](https://github.com/IllumiDesk/illumidesk/issues/132)) ([b276f08](https://github.com/IllumiDesk/illumidesk/commit/b276f08112d053928ecae72d5dc6dbf2d930f646))
* Update escaped character configuration to remove duplicate home folders ([#85](https://github.com/IllumiDesk/illumidesk/issues/85)) ([c518bd5](https://github.com/IllumiDesk/illumidesk/commit/c518bd53f0a42a263b6d94913c6867e939b29e31))
* Update LTI configs with admin user env var ([#219](https://github.com/IllumiDesk/illumidesk/issues/219)) ([3c99d58](https://github.com/IllumiDesk/illumidesk/commit/3c99d5831b1dd194fdf49ac1c0398703a475e6d8))
* Update nbgrader config template by adding a escape characters ([#230](https://github.com/IllumiDesk/illumidesk/issues/230)) ([57f5361](https://github.com/IllumiDesk/illumidesk/commit/57f53619ea8b6ea8dac09d19d9f0dbcf0f173e69))
* Update regex for to accept course names with hyphens and underscores ([#134](https://github.com/IllumiDesk/illumidesk/issues/134)) ([1201130](https://github.com/IllumiDesk/illumidesk/commit/12011309a3e4caa92d569a153f55567b36573a9b))
* Update required claims and username value when private ([#241](https://github.com/IllumiDesk/illumidesk/issues/241)) ([1c49ed6](https://github.com/IllumiDesk/illumidesk/commit/1c49ed66f71c6096b299473d06ede64bac145f79))
* Update setup course service default CMD ([#197](https://github.com/IllumiDesk/illumidesk/issues/197)) ([02c5b4d](https://github.com/IllumiDesk/illumidesk/commit/02c5b4d7de7fd03210ff3e5b9f359f14b2934b5e))
* Update standard launch url for LTI 11 ([#6](https://github.com/IllumiDesk/illumidesk/issues/6)) ([736132a](https://github.com/IllumiDesk/illumidesk/commit/736132a971fcb7a7df2b77ee2392a07e0d39ea4a))
* Update to resolve CVE-2020-8116 ([#258](https://github.com/IllumiDesk/illumidesk/issues/258)) ([539f4f5](https://github.com/IllumiDesk/illumidesk/commit/539f4f5e599e3beaf97d7c66a2f4b2f97249b2c1))
* Updates response of the `/jwks` endpoint ([#220](https://github.com/IllumiDesk/illumidesk/issues/220)) ([0dc1264](https://github.com/IllumiDesk/illumidesk/commit/0dc1264d8bff472fdeb4b0cf8a2c96dd92c350b7))
* Validates if 'lis_outcome_service_url' and 'lis_result_sourcedid' fields exist ([#95](https://github.com/IllumiDesk/illumidesk/issues/95)) ([105e854](https://github.com/IllumiDesk/illumidesk/commit/105e854dc2b3758bce1f64f3e695d9397ba4c287))
* **deps:** Remove ansible-lint ([#34](https://github.com/IllumiDesk/illumidesk/issues/34)) ([278ca0c](https://github.com/IllumiDesk/illumidesk/commit/278ca0c3af12b13f94416b1cda44f630a67ef457))

### 0.9.1 (2020-08-25)


### Bug Fixes

* Ensure the course directory exists before adding LTI 1.1 control file ([#300](https://github.com/IllumiDesk/illumidesk/issues/300)) ([d90e89d](https://github.com/IllumiDesk/illumidesk/commit/d90e89d4c763bacdafd76c709f2f4f4ed3a1e7cf))


## 0.9.0 (2020-08-24)


### Features

* Automated assignment creation with LTI 1.3 ([#260](https://github.com/IllumiDesk/illumidesk/issues/260)) ([170dc92](https://github.com/IllumiDesk/illumidesk/commit/170dc923a864bebf4fb3a6bf0d2a56284fb7390e))
* Automated assignment creation with LTI11 ([#265](https://github.com/IllumiDesk/illumidesk/issues/265)) ([beadb21](https://github.com/IllumiDesk/illumidesk/commit/beadb216f375c6a007d16471d14c7c53d91b12e4))
* Create a shared folder for graders and students ([#281](https://github.com/IllumiDesk/illumidesk/issues/281)) ([c0d86a1](https://github.com/IllumiDesk/illumidesk/commit/c0d86a18ab2cbf086436cb7aefb6995fb3b3e354))
* Fixes the use of next url with LTI 1.3 ([#244](https://github.com/IllumiDesk/illumidesk/issues/244)) ([2f90f8e](https://github.com/IllumiDesk/illumidesk/commit/2f90f8e4ac41eb6a2c41be0abf4e6bda04a57560))
* Handle unique usernames with the Canvas LMS ([#268](https://github.com/IllumiDesk/illumidesk/issues/268)) ([7d26c74](https://github.com/IllumiDesk/illumidesk/commit/7d26c74fbf2502fe9fc8bac9073dbf0c5a02ca70))
* Include users with TeachingAssistant role in the formgrade group ([#271](https://github.com/IllumiDesk/illumidesk/issues/271)) ([6b769be](https://github.com/IllumiDesk/illumidesk/commit/6b769be00f24e02c92ab327349223b0caf96ed76))
* Update dockerspawner configuration settings ([#288](https://github.com/IllumiDesk/illumidesk/issues/288)) ([a8f4dac](https://github.com/IllumiDesk/illumidesk/commit/a8f4dacd6f6891373de1cf0fb213ce5385cb71de))

### Bug Fixes

* Add defaults to demo_* env vars for FirstUse  authenticator ([#143](https://github.com/IllumiDesk/illumidesk/issues/143)) ([e34395a](https://github.com/IllumiDesk/illumidesk/commit/e34395a143e2f16281b2fc5fd28d0e331a7c35ad))
* Determine what authenticator is used to submit grades ([#251](https://github.com/IllumiDesk/illumidesk/issues/251)) ([ff952fc](https://github.com/IllumiDesk/illumidesk/commit/ff952fc0d05dc250ebbf6ea8b28fd8fb81090a35))
* Java kernel installation with base image ([#190](https://github.com/IllumiDesk/illumidesk/issues/190)) ([61b064c](https://github.com/IllumiDesk/illumidesk/commit/61b064cf9655725108deb1331375adb86e2aaa3c))
* Normalize line item strings before submitting grades with LTI 1.3 ([#287](https://github.com/IllumiDesk/illumidesk/issues/287)) ([7df5bc3](https://github.com/IllumiDesk/illumidesk/commit/7df5bc3c86711c9d7d8bd4dcb8d6e41969abbad1))
* Source directory permissions when adding gradebook ([#270](https://github.com/IllumiDesk/illumidesk/issues/270)) ([579a02c](https://github.com/IllumiDesk/illumidesk/commit/579a02cd15883b76e74552cc0847bf7a64348497))
* Update to resolve CVE-2020-8116 ([#258](https://github.com/IllumiDesk/illumidesk/issues/258)) ([539f4f5](https://github.com/IllumiDesk/illumidesk/commit/539f4f5e599e3beaf97d7c66a2f4b2f97249b2c1))

### 0.8.3 (2020-07-23)


### Features

* Custom base url configuration ([#231](https://github.com/IllumiDesk/illumidesk/issues/231)) ([5c50458](https://github.com/IllumiDesk/illumidesk/commit/5c50458843d46bc30fac819cccbb00cb03258118))
* Pull workspace images with ansible-playbook from registry ([#229](https://github.com/IllumiDesk/illumidesk/issues/229)) ([757006b](https://github.com/IllumiDesk/illumidesk/commit/757006b881fcc59abf963644979a55d5836d1750))
* Set admin user with ansible configuration ([#213](https://github.com/IllumiDesk/illumidesk/issues/213)) ([eb7981f](https://github.com/IllumiDesk/illumidesk/commit/eb7981f3cc764d10c0d81f1387260cfdf9784262))
* Add course template and use setup-course for course config ([#236](https://github.com/IllumiDesk/illumidesk/issues/236)) ([2f229e3](https://github.com/IllumiDesk/illumidesk/commit/2f229e316f317d94dfaa13e2a874a983792bb2cf))

### Bug Fixes

* Update required claims and username value when private ([#241](https://github.com/IllumiDesk/illumidesk/issues/241)) ([1c49ed6](https://github.com/IllumiDesk/illumidesk/commit/1c49ed66f71c6096b299473d06ede64bac145f79))
* Update nbgrader config template by adding a escape characters ([#230](https://github.com/IllumiDesk/illumidesk/issues/230)) ([57f5361](https://github.com/IllumiDesk/illumidesk/commit/57f53619ea8b6ea8dac09d19d9f0dbcf0f173e69))

### 0.8.2 (2020-07-16)


### Features

* Complete Julia dynamic config setup ([#222](https://github.com/IllumiDesk/illumidesk/issues/222)) ([e5ebea5](https://github.com/IllumiDesk/illumidesk/commit/e5ebea52f0b4d16ded03a6c9604d490311c8e8f1))


### Bug Fixes

* Copy notebook config to global /etc/jupyter location ([#209](https://github.com/IllumiDesk/illumidesk/issues/209)) ([e16cccf](https://github.com/IllumiDesk/illumidesk/commit/e16cccf1ff7b80684a395b64d7a82a2ae2396ebe))
* Update LTI configs with admin_user environment variable ([#219](https://github.com/IllumiDesk/illumidesk/issues/219)) ([3c99d58](https://github.com/IllumiDesk/illumidesk/commit/3c99d5831b1dd194fdf49ac1c0398703a475e6d8))
* Update setup-course service default docker CMD ([#197](https://github.com/IllumiDesk/illumidesk/issues/197)) ([02c5b4d](https://github.com/IllumiDesk/illumidesk/commit/02c5b4d7de7fd03210ff3e5b9f359f14b2934b5e))
* Updates response of the `/jwks` endpoint ([#220](https://github.com/IllumiDesk/illumidesk/issues/220)) ([0dc1264](https://github.com/IllumiDesk/illumidesk/commit/0dc1264d8bff472fdeb4b0cf8a2c96dd92c350b7))

### 0.8.1 (2020-07-11)


### Features

* Add Java kernel ([#187](https://github.com/IllumiDesk/illumidesk/issues/187)) ([5800408](https://github.com/IllumiDesk/illumidesk/commit/5800408c1285a669f3ed95d53e4c12fc799d0800))
* Improve deployment times with ansible-playbook by updating setup-course base image ([#199](https://github.com/IllumiDesk/illumidesk/pull/199)) ([a958f57](https://github.com/IllumiDesk/illumidesk/commit/a958f578c9cfddda531590c0548e2927a2e52842))

### Bug Fixes

* Normalize course label for LTI 1.3 ([#198](https://github.com/IllumiDesk/illumidesk/issues/198)) ([4d5cffe](https://github.com/IllumiDesk/illumidesk/commit/4d5cffe4641b4b114ca8a944438d1ed52d248679))

## 0.8.0 (2020-07-08)


### Features

* Add support to setup stack with AWS EFS-based mounts ([#159](https://github.com/IllumiDesk/illumidesk/issues/159)) ([d50d311](https://github.com/IllumiDesk/illumidesk/commit/d50d311faa7274c71b4bb5b7e88073eb4215debc))
* Segregate public key endpoint from config endpoint for LTI 1.3 (public key) ([#171](https://github.com/IllumiDesk/illumidesk/issues/171)) ([e2dbca7](https://github.com/IllumiDesk/illumidesk/commit/e2dbca7f600e2ed0718a71d6f917cf8f2f38423f))
* Support additional workspace types ([#164](https://github.com/IllumiDesk/illumidesk/issues/164)) ([6c13bc9](https://github.com/IllumiDesk/illumidesk/commit/6c13bc95feb632727e6df10ed9f6c398d3b66136))
* Update nbgrader config file to include the code stub for julia language ([#181](https://github.com/IllumiDesk/illumidesk/issues/181)) ([add1b3c](https://github.com/IllumiDesk/illumidesk/commit/add1b3c90a394dd91cccc5b4f2dac40c3e830208))


### Bug Fixes

* Set python interpreter in hosts file ([#173](https://github.com/IllumiDesk/illumidesk/issues/173)) ([930b303](https://github.com/IllumiDesk/illumidesk/commit/930b3036c2d3f78a0e6c0d35b4bdbb97f41ebdda))
* Update authentication validation steps ([#168](https://github.com/IllumiDesk/illumidesk/issues/168)) ([c507ca7](https://github.com/IllumiDesk/illumidesk/commit/c507ca71e693af81f17473d4850f5cf9b77929bb))

### 0.7.3 (2020-06-23)


### Features

* Clone and merge code located in remote git-based repositories with workspace launches ([#153](https://github.com/IllumiDesk/illumidesk/issues/153)) ([19eb3d7](https://github.com/IllumiDesk/illumidesk/commit/19eb3d7f82424bfdaf604c2ff8b681b148237d99))


### Bug Fixes

* Add defaults to demo_* env vars for FirstUse  authenticator ([#143](https://github.com/IllumiDesk/illumidesk/issues/143)) ([e34395a](https://github.com/IllumiDesk/illumidesk/commit/e34395a143e2f16281b2fc5fd28d0e331a7c35ad))


### 0.7.2 (2020-06-15)


### Bug Fixes

* Update conditional in lti11 authenticator with Learner string ([#132](https://github.com/IllumiDesk/illumidesk/issues/132)) ([b276f08](https://github.com/IllumiDesk/illumidesk/commit/b276f08112d053928ecae72d5dc6dbf2d930f646))
* Update regex for to accept course names with hyphens and underscores ([#134](https://github.com/IllumiDesk/illumidesk/issues/134)) ([1201130](https://github.com/IllumiDesk/illumidesk/commit/12011309a3e4caa92d569a153f55567b36573a9b))


### 0.7.1 (2020-06-10)


### Features

* Adds lms_user_id in custom_fields ([#121](https://github.com/IllumiDesk/illumidesk/issues/121)) ([aaa98bd](https://github.com/IllumiDesk/illumidesk/commit/aaa98bdc2725838a6c48e45cf1b3bad75e745ebf))

### Bug Fixes

* Fix invalid image tag error when running ansible-playbook ([#122](https://github.com/IllumiDesk/illumidesk/issues/122)) ([4630417](https://github.com/IllumiDesk/illumidesk/commit/4630417d6cdf1965f23723737fe6356283a95620))


### 0.7.0 (2020-06-06)


### Features

* Share Plotly dashboards from end-user notebooks ([#96](https://github.com/IllumiDesk/illumidesk/issues/96)) ([e3489e4](https://github.com/IllumiDesk/illumidesk/commit/e3489e4e3b9c94cdd75a56ba3a4ec00796b9df63))

### Bug Fixes

* Validates if 'lis_outcome_service_url' and 'lis_result_sourcedid' fields exist ([#95](https://github.com/IllumiDesk/illumidesk/issues/95)) ([105e854](https://github.com/IllumiDesk/illumidesk/commit/105e854dc2b3758bce1f64f3e695d9397ba4c287))

### 0.6.1 (2020-05-27)


### Bug Fixes

* Register jupyterhub api token ([#86](https://github.com/IllumiDesk/illumidesk/issues/86)) ([9342037](https://github.com/IllumiDesk/illumidesk/commit/9342037f0a584938a7cced02a4a203865fc52819))
* Update escaped character configuration to remove duplicate home folders ([#85](https://github.com/IllumiDesk/illumidesk/issues/85)) ([c518bd5](https://github.com/IllumiDesk/illumidesk/commit/c518bd53f0a42a263b6d94913c6867e939b29e31))

## 0.6.0 (2020-05-23)


### Features

* Add LTI 1.3 authentication to IllumiDesk package with JupyterHub ([#33](https://github.com/IllumiDesk/illumidesk/issues/33)) ([364f9b6](https://github.com/IllumiDesk/illumidesk/commit/364f9b6b4315fd4b1912abf9c069dbb1a1aa66b8))

## 0.5.0 (2020-05-23)


### Features

* Add a postgres service for labs ([#75](https://github.com/IllumiDesk/illumidesk/issues/75)) ([b733c0b](https://github.com/IllumiDesk/illumidesk/commit/b733c0b4015754d85788629e51a7594154db6f0e))


### 0.4.1 (2020-05-23)


### Bug Fixes

* Handle missing lis arguments with learner launch requests ([#65](https://github.com/IllumiDesk/illumidesk/issues/65)) ([b83318a](https://github.com/IllumiDesk/illumidesk/commit/b83318a0217a0348861478df916823710f745ac7))

## 0.4.0 (2020-05-14)


### Features

* Add plotly dependencies ([#59](https://github.com/IllumiDesk/illumidesk/issues/59)) ([59b8f1f](https://github.com/IllumiDesk/illumidesk/commit/59b8f1f992251bdad4bd30cc7c79be5b01b6edb4))

### 0.3.5 (2020-05-14)


### Bug Fixes

* Add missing setup-course image dependencies to install illumidesk packages ([#58](https://github.com/IllumiDesk/illumidesk/issues/58)) ([4ba9fd2](https://github.com/IllumiDesk/illumidesk/commit/4ba9fd25ab6c1bf5a94168881c1784d01eb0923a))

### 0.3.4 (2020-05-12)


### Bug Fixes

* Fixes grades submission for moodle ([#41](https://github.com/IllumiDesk/illumidesk/issues/41)) ([d505e99](https://github.com/IllumiDesk/illumidesk/commit/d505e997d4a91c67e882c183ff55760aabfad9b1))

### 0.3.3 (2020-05-12)


### Features

* Circumvent initial course setup during deployment when LTI v1.1 or vLTI 1.3 is enabled ([#53](https://github.com/IllumiDesk/illumidesk/issues/53)) ([2ab217e](https://github.com/IllumiDesk/illumidesk/commit/2ab217efa064c889f63773549d34fbf3db0cd7d8))


### 0.3.2 (2020-05-12)


### Bug Fixes

* **User Interface** Add text to clarify assignment name in modal ([#48](https://github.com/IllumiDesk/illumidesk/issues/48)) ([fcfdd22](https://github.com/IllumiDesk/illumidesk/commit/fcfdd225e6816b9bdf0d9e00a76423958e879fcb))

### 0.3.1 (2020-05-11)


### Features

* Update services menu in JupyterHub's control panel ([#46](https://github.com/IllumiDesk/illumidesk/issues/46)) ([f1101c5](https://github.com/IllumiDesk/illumidesk/commit/f1101c59aa5f236c02909b7147ac7366a5a558ac))

## 0.3.0 (2020-05-07)


### Features

* Add grades submission feature using LTI 1.1 ([#38](https://github.com/IllumiDesk/illumidesk/issues/38)) ([10d1a63](https://github.com/IllumiDesk/illumidesk/commit/10d1a631a4dd16637cfa917beb940267a63bcfd4))

### 0.2.3 (2020-05-01)


### Bug Fixes

* Remove ansible-lint due to security issues ([#24](https://github.com/IllumiDesk/illumidesk/issues/34)) ([278ca0c](https://github.com/IllumiDesk/illumidesk/commit/278ca0c3af12b13f94416b1cda44f630a67ef457))


### 0.2.2 (2020-04-25)


### Bug Fixes

* Fix race condition so traefik can load rules.toml correctly ([#29](https://github.com/IllumiDesk/illumidesk/issues/29)) ([e56e423](https://github.com/IllumiDesk/illumidesk/commit/e56e423b1a8b87cca9c3331439e797a3d1251af3))

### 0.2.1 (2020-04-24)


### Bug Fixes

* Add jupyterhub config for LTI 1.1 to task ([#27](https://github.com/IllumiDesk/illumidesk/issues/27)) ([0a21d55](https://github.com/IllumiDesk/illumidesk/commit/0a21d557cde343e3559244c8563bd2b0d3efc531))

## 0.2.0 (2020-04-24)


### Features

* Dynamic course and user setup with LTI 1.1 ([#18](https://github.com/IllumiDesk/illumidesk/issues/18)) ([dfa21c0](https://github.com/IllumiDesk/illumidesk/commit/dfa21c0498fd082a7bd9bcd86d30a036a872c61c))
* Run JupyterHub with  python 3.8 ([#12](https://github.com/IllumiDesk/illumidesk/issues/12)) ([cc07bd9](https://github.com/IllumiDesk/illumidesk/commit/cc07bd919d57d698f0a225ba86f791f4a16ff7af))
* Simplify setup with make and new inventory file ([#8](https://github.com/IllumiDesk/illumidesk/issues/8)) ([019687e](https://github.com/IllumiDesk/illumidesk/commit/019687ed9325b822ec948c3ab7be9ef51bf67a4a))


### Bug Fixes

* Update standard launch url for LTI 11 ([#6](https://github.com/IllumiDesk/illumidesk/issues/6)) ([736132a](https://github.com/IllumiDesk/illumidesk/commit/736132a971fcb7a7df2b77ee2392a07e0d39ea4a))

### 0.1.1 (2020-04-15)


### Features

* Run JupyterHub with  python 3.8 ([#12](https://github.com/IllumiDesk/illumidesk/issues/12)) ([cc07bd9](https://github.com/IllumiDesk/illumidesk/commit/cc07bd919d57d698f0a225ba86f791f4a16ff7af))
* Simplify setup with make and new inventory file ([#8](https://github.com/IllumiDesk/illumidesk/issues/8)) ([019687e](https://github.com/IllumiDesk/illumidesk/commit/019687ed9325b822ec948c3ab7be9ef51bf67a4a))


### Bug Fixes

* Update standard launch url for LTI 11 ([#6](https://github.com/IllumiDesk/illumidesk/issues/6)) ([736132a](https://github.com/IllumiDesk/illumidesk/commit/736132a971fcb7a7df2b77ee2392a07e0d39ea4a))