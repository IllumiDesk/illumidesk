# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## 0.8.0 (2020-07-08)


### Features

* Add a postgres service for labs ([#75](https://github.com/IllumiDesk/illumidesk/issues/75)) ([b733c0b](https://github.com/IllumiDesk/illumidesk/commit/b733c0b4015754d85788629e51a7594154db6f0e))
* Add plotly dependencies ([#59](https://github.com/IllumiDesk/illumidesk/issues/59)) ([59b8f1f](https://github.com/IllumiDesk/illumidesk/commit/59b8f1f992251bdad4bd30cc7c79be5b01b6edb4))
* Add support to setup stack with AWS EFS-based mounts ([#159](https://github.com/IllumiDesk/illumidesk/issues/159)) ([d50d311](https://github.com/IllumiDesk/illumidesk/commit/d50d311faa7274c71b4bb5b7e88073eb4215debc))
* Adds lms_user_id in custom_fields ([#121](https://github.com/IllumiDesk/illumidesk/issues/121)) ([aaa98bd](https://github.com/IllumiDesk/illumidesk/commit/aaa98bdc2725838a6c48e45cf1b3bad75e745ebf))
* Clone and merge code located in remote git-based repositories with workspace launches ([#153](https://github.com/IllumiDesk/illumidesk/issues/153)) ([19eb3d7](https://github.com/IllumiDesk/illumidesk/commit/19eb3d7f82424bfdaf604c2ff8b681b148237d99))
* Do not use initial course service when LTI is enabled ([#53](https://github.com/IllumiDesk/illumidesk/issues/53)) ([2ab217e](https://github.com/IllumiDesk/illumidesk/commit/2ab217efa064c889f63773549d34fbf3db0cd7d8))
* Run JupyterHub with  python 3.8 ([#12](https://github.com/IllumiDesk/illumidesk/issues/12)) ([cc07bd9](https://github.com/IllumiDesk/illumidesk/commit/cc07bd919d57d698f0a225ba86f791f4a16ff7af))
* Segregate public key endpoint from config endpoint for LTI 1.3 (public key) ([#171](https://github.com/IllumiDesk/illumidesk/issues/171)) ([e2dbca7](https://github.com/IllumiDesk/illumidesk/commit/e2dbca7f600e2ed0718a71d6f917cf8f2f38423f))
* Share Plotly dashboards from end-user notebooks ([#96](https://github.com/IllumiDesk/illumidesk/issues/96)) ([e3489e4](https://github.com/IllumiDesk/illumidesk/commit/e3489e4e3b9c94cdd75a56ba3a4ec00796b9df63))
* Simplify setup with make and new inventory file ([#8](https://github.com/IllumiDesk/illumidesk/issues/8)) ([019687e](https://github.com/IllumiDesk/illumidesk/commit/019687ed9325b822ec948c3ab7be9ef51bf67a4a))
* Support additional workspace types ([#164](https://github.com/IllumiDesk/illumidesk/issues/164)) ([6c13bc9](https://github.com/IllumiDesk/illumidesk/commit/6c13bc95feb632727e6df10ed9f6c398d3b66136))
* Update nbgrader config file to include the code stub for julia language ([#181](https://github.com/IllumiDesk/illumidesk/issues/181)) ([add1b3c](https://github.com/IllumiDesk/illumidesk/commit/add1b3c90a394dd91cccc5b4f2dac40c3e830208))
* Update Services dropdown in JupyterHub's control panel ([#46](https://github.com/IllumiDesk/illumidesk/issues/46)) ([f1101c5](https://github.com/IllumiDesk/illumidesk/commit/f1101c59aa5f236c02909b7147ac7366a5a558ac))
* **core:** Add grades submission feature using LTI 1.1 ([#38](https://github.com/IllumiDesk/illumidesk/issues/38)) ([10d1a63](https://github.com/IllumiDesk/illumidesk/commit/10d1a631a4dd16637cfa917beb940267a63bcfd4))
* **core:** Dynamic course and user setup with LTI 1.1 ([#18](https://github.com/IllumiDesk/illumidesk/issues/18)) ([dfa21c0](https://github.com/IllumiDesk/illumidesk/commit/dfa21c0498fd082a7bd9bcd86d30a036a872c61c))


### Bug Fixes

* Add defaults to demo_* env vars for FirstUse  authenticator ([#143](https://github.com/IllumiDesk/illumidesk/issues/143)) ([e34395a](https://github.com/IllumiDesk/illumidesk/commit/e34395a143e2f16281b2fc5fd28d0e331a7c35ad))
* Add jupyterhub config for LTI 1.1 to task ([#27](https://github.com/IllumiDesk/illumidesk/issues/27)) ([0a21d55](https://github.com/IllumiDesk/illumidesk/commit/0a21d557cde343e3559244c8563bd2b0d3efc531))
* Add missing setup-course image dependencies to install illumidesk packages ([#58](https://github.com/IllumiDesk/illumidesk/issues/58)) ([4ba9fd2](https://github.com/IllumiDesk/illumidesk/commit/4ba9fd25ab6c1bf5a94168881c1784d01eb0923a))
* Add text to clarify assignment name in modal ([#48](https://github.com/IllumiDesk/illumidesk/issues/48)) ([fcfdd22](https://github.com/IllumiDesk/illumidesk/commit/fcfdd225e6816b9bdf0d9e00a76423958e879fcb))
* Fix invalid image tag error when running ansible-playbook ([#122](https://github.com/IllumiDesk/illumidesk/issues/122)) ([4630417](https://github.com/IllumiDesk/illumidesk/commit/4630417d6cdf1965f23723737fe6356283a95620))
* Fix race condition so traefik can load rules.toml correctly ([#29](https://github.com/IllumiDesk/illumidesk/issues/29)) ([e56e423](https://github.com/IllumiDesk/illumidesk/commit/e56e423b1a8b87cca9c3331439e797a3d1251af3))
* Fixes grades submission for moodle ([#41](https://github.com/IllumiDesk/illumidesk/issues/41)) ([d505e99](https://github.com/IllumiDesk/illumidesk/commit/d505e997d4a91c67e882c183ff55760aabfad9b1))
* Handle missing lis arguments with launch requests initiated by learners ([#65](https://github.com/IllumiDesk/illumidesk/issues/65)) ([b83318a](https://github.com/IllumiDesk/illumidesk/commit/b83318a0217a0348861478df916823710f745ac7))
* Register jupyterhub api token ([#86](https://github.com/IllumiDesk/illumidesk/issues/86)) ([9342037](https://github.com/IllumiDesk/illumidesk/commit/9342037f0a584938a7cced02a4a203865fc52819))
* requirements.txt to reduce vulnerabilities ([#63](https://github.com/IllumiDesk/illumidesk/issues/63)) ([72e07b3](https://github.com/IllumiDesk/illumidesk/commit/72e07b39e6ef4d1ffe0737528cc9030ab993e2c8))
* Revert ansible to 2.9.9 ([#70](https://github.com/IllumiDesk/illumidesk/issues/70)) ([833a276](https://github.com/IllumiDesk/illumidesk/commit/833a276a7de59e56ac56e84636894305abaf3c91))
* Set python interpreter in hosts file ([#173](https://github.com/IllumiDesk/illumidesk/issues/173)) ([930b303](https://github.com/IllumiDesk/illumidesk/commit/930b3036c2d3f78a0e6c0d35b4bdbb97f41ebdda))
* Update authentication validation steps ([#168](https://github.com/IllumiDesk/illumidesk/issues/168)) ([c507ca7](https://github.com/IllumiDesk/illumidesk/commit/c507ca71e693af81f17473d4850f5cf9b77929bb))
* Update conditional in lti11 authenticator with Learner string ([#132](https://github.com/IllumiDesk/illumidesk/issues/132)) ([b276f08](https://github.com/IllumiDesk/illumidesk/commit/b276f08112d053928ecae72d5dc6dbf2d930f646))
* Update escaped character configuration to remove duplicate home folders ([#85](https://github.com/IllumiDesk/illumidesk/issues/85)) ([c518bd5](https://github.com/IllumiDesk/illumidesk/commit/c518bd53f0a42a263b6d94913c6867e939b29e31))
* Update regex for to accept course names with hyphens and underscores ([#134](https://github.com/IllumiDesk/illumidesk/issues/134)) ([1201130](https://github.com/IllumiDesk/illumidesk/commit/12011309a3e4caa92d569a153f55567b36573a9b))
* Update standard launch url for LTI 11 ([#6](https://github.com/IllumiDesk/illumidesk/issues/6)) ([736132a](https://github.com/IllumiDesk/illumidesk/commit/736132a971fcb7a7df2b77ee2392a07e0d39ea4a))
* Validates if 'lis_outcome_service_url' and 'lis_result_sourcedid' fields exist ([#95](https://github.com/IllumiDesk/illumidesk/issues/95)) ([105e854](https://github.com/IllumiDesk/illumidesk/commit/105e854dc2b3758bce1f64f3e695d9397ba4c287))
* **deps:** Remove ansible-lint ([#34](https://github.com/IllumiDesk/illumidesk/issues/34)) ([278ca0c](https://github.com/IllumiDesk/illumidesk/commit/278ca0c3af12b13f94416b1cda44f630a67ef457))

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
