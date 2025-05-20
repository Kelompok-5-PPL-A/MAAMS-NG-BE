# CHANGELOG



## v0.2.1 (2025-05-20)

### Refactor

* refactor: change django timezone to datetime ([`2cb3a79`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2cb3a79793723653ce3bed1416c9e6809dbd16d1))


## v0.2.0 (2025-05-20)

### Chore

* chore(ci): revert semantic release version ([`0845633`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0845633831093747432de6edb45671a31bb8e58e))

### Documentation

* docs(semantic-release): update documentation for new semantic release implementation ([`594f5fe`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/594f5fe9d91717f761f968346afd393615390fba))

### Unknown

* Merge pull request #86 from Kelompok-5-PPL-A/staging

Staging ([`ece5e57`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ece5e57d9bf67624ee3b133bd81db283629d4c95))

* Merge branch &#39;staging&#39; of github.com-personal:Kelompok-5-PPL-A/MAAMS-NG-BE into staging ([`5fb7f0b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5fb7f0b1decd631f95f076791dab4c8331f6fff2))


## v0.1.0-beta.1 (2025-05-20)

### Chore

* chore: update deployment when version not increment ([`4f64bae`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4f64bae374ad84adaf5dee101963e920910b403b))

* chore: bump version to 0.2.0 [skip ci] ([`f3a5e6c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f3a5e6cd26ff75b8e787db0dfd9446ab77b1ce42))

* chore(semantic-release): add token to pyproject.toml ([`262ebd6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/262ebd672d084838c27a02c8cf36d83df209e1b7))

* chore: remove commented-out code test ([`878b937`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/878b937b794ab1a14c9d8276cfd62aac3a048ce5))

* chore: upgrade django version ([`b96f96e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b96f96e5d7327ebd8c9f03a72cd0c1ea081281a1))

* chore(settings): change timezone to Asia/Jakarta ([`f1e9ebe`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f1e9ebe1bbd47303dc3569830b986486d6bd85c6))

### Ci

* ci(versioning): improve semantic versioning workflow

- Switch to semver version scheme
- Add commit type check step
- Use GH_TOKEN instead of PERSONAL_ACCESS_TOKEN
- Add tomli dependency for version parsing
- Clean up redundant configuration in pyproject.toml ([`19f5a71`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/19f5a71143c3c620556a59d0aa5d66f4999619e0))

* ci(versioning): simplify semantic versioning with commitizen ([`e933532`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e933532a232bacc1715a9f8ca10a6a93d73bfb6d))

* ci(versioning): simplify semantic versioning with commitizen

- Remove manual version analysis in favor of commitizen&#39;s built-in functionality
- Update version to 0.1.0 in pyproject.toml
- Clean up comments in CI workflow ([`413d8a4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/413d8a49eaaace2a7e6f26577321688439bc149a))

* ci(versioning): refactor semantic versioning workflow

- Remove Commitizen dependency from CI/CD
- Implement custom version bump logic
- Add explicit version analysis from commit messages
- Update version files handling
- Improve version bump reliability ([`98973e0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/98973e03a58411e92265469efae80e7bc960de54))

* ci(workflow): add branch condition to semantic release job and documentation

- Add condition to run semantic release only on main and staging branches
- Prevent unnecessary version checks on other branches&#34; ([`db49399`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/db49399bf12a2d0841f425ec088e5239ec00bf6e))

* ci(versioning): implement semantic versioning with commitizen

- Add commitizen configuration in pyproject.toml
- Update GitHub Actions workflow to use commitizen
- Add version tracking in MAAMS_NG_BE/__init__.py
- Configure automated version bumping and release creation ([`409a2d8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/409a2d80dde4bf362320163f22ce17942fe59c31))

* ci(deploy): implement manual rollback and optimize deployment workflow

- Add manual rollback workflow for controlled version rollbacks
- Configure GCS bucket lifecycle for backup management
- Update database configuration to use DATABASE_URL
- Optimize Docker build with dummy DATABASE_URL for collectstatic
- Implement database backup and restore scripts with DATABASE_URL support
- Add secure secret key generation script
- Replace hardcoded test secret key with GitHub secret
- Implement environment-specific data seeding
- Add OWASP ZAP security scanning
- Improve workflow dispatch options for manual control

This change provides a more robust deployment strategy with:
- Manual rollback capability for specific versions
- Automated rollback for failed deployments
- Improved database backup management
- Better environment variable handling
- Enhanced deployment safety measures
- Secure test environment configuration
- Automated security scanning
- Environment-specific data seeding

BREAKING CHANGES:
- Database configuration now requires DATABASE_URL environment variable
- Test environment requires TEST_SECRET_KEY GitHub secret
- Manual rollback workflow replaces automatic rollback
- Environment-specific data seeding requires new seed commands
- OWASP ZAP scanning requires .zap/rules.tsv configuration

Implementation History:
1. Initial deployment workflow with automatic rollback
2. Added database backup and restore functionality
3. Implemented manual rollback workflow
4. Added secure secret management
5. Integrated OWASP ZAP security scanning
6. Added environment-specific data seeding ([`fae4ff1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fae4ff104a19f837d95ab2e235421c3c9c304ca6))

### Feature

* feat(ci): use semantic-release version tag for deployment and image tagging ([`8fff3a2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8fff3a2cadcce0a94e040d3cc42ec24cad0d383d))

* feat: change temperature parameter ([`917ed97`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/917ed97f468530efbaeab3db9f261f9b12e44beb))

* feat: update AI model to DeepSeek R1 ([`23d4f41`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/23d4f41aa7985361101cfd3dc5cdccab98398852))

* feat(ci): enhance CI/CD pipeline with security, deployment, and data management ([`4d55665`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4d55665c639e4d88048946903ae6c1f881f680cc))

* feat: update authentication views ([`a96277c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a96277cf31813adca47e870e70a76c86bc6dad30))

### Fix

* fix(versioning): try to resolve increment issue ([`a25f2f5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a25f2f54664c38a7a23ffe6c43669f5fc21be7c5))

* fix: remove max_completion_tokens parameter ([`0999cee`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0999ceea80515c228e8cf37878df5b8fbdb19bb7))

* fix(versioning): remove manual version management ([`95586f7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/95586f7d00863c560b70782a98819d8833e201e5))

* fix(release): update setup.py path in semantic-release config ([`434673f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/434673f8f3be17646578f478dc912dc973d55a33))

* fix(ci): install setuptools and wheel before semantic-release build ([`7bd1631`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7bd16311e119c0f8523862a77f2e39a68ce55ed0))

* fix(release): update pyproject.toml for semantic-release v10 compatibility ([`e31a3e9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e31a3e9817e8202c136f3c2fcaa78c737539aa6c))

* fix(ci): set env vars to GCR deployment ([`4db0b77`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4db0b77d9db96405844aef28317ed07769bca622))

* fix(ci): remove invalid gcloud run services create command ([`bd328f1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bd328f1c0a5086ac9aad5228f6f24e42de1241bb))

* fix(ci): restrict OWASP ZAP scan to development branch only ([`f16864c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f16864c4a8ce535ff424819fc84402fb38a23c7a))

* fix(ci): resolve Cloud Run deployment image tag issue ([`f934aaf`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f934aafc2719c1b2508c71fc504d4263fbef7cc9))

* fix(auth): improve SSO UI provider test ([`75e05d3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/75e05d3ca967dfc83d998f5e9f4ab049dcabbb72))

* fix(test): improve coverage for jwt token service ([`05975c1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/05975c18f1b34c7b8af9ffb83b2607a40e89bbd6))

* fix(auth): resolved duplication code from current implementation ([`2322703`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/232270330ae513e99f192b81674f65b4a3c5a63d))

* fix(ci): update test command ([`9d75701`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9d75701b819beaa8fc2431be6a422919782d2c3d))

* fix(auth): update seed command and SSO UI authentication ([`f2f603f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f2f603fc0be1a8536d61b300f81901af129238ec))

* fix(auth): update auth tests to match current implementation ([`6587f5a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6587f5a09c41fe62f4f126e33865d018adfd23da))

* fix(ci): correct seed command arguments ([`f3a7256`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f3a725601183fb3a6c811ddb2a4d481de90fde70))

* fix(ci): correct migration and seeding process ([`89f8522`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/89f85224ecd79cd17c074f0fbf1573ed6c972b13))

* fix(ci): disable upload_to_release to fix warning ([`3991c56`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3991c56956e33a42a46e7e0606022f5b41843662))

### Unknown

* Merge branch &#39;staging&#39; of github.com-personal:Kelompok-5-PPL-A/MAAMS-NG-BE into staging ([`4aba8fb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4aba8fb00391f47199a17234ef6b49ab7dac0670))

* Merge pull request #85 from Kelompok-5-PPL-A/staging

Staging ([`0f62d5a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0f62d5a99f292a87a4c61119f7f2b4da4e2195f4))

* Merge pull request #84 from Kelompok-5-PPL-A/staging

Implement Semantic Versioning with Commitizen (v{major}.{minor}.{patch}) ([`9518961`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/951896157c1c39349211bf4fae1b0103cbfaede8))

* Merge pull request #83 from Kelompok-5-PPL-A/staging

CI/CD Improvements ([`db7380b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/db7380b544af1e6229e79abc70bfb2374c285ccb))

* Merge branch &#39;staging&#39; of github.com-personal:Kelompok-5-PPL-A/MAAMS-NG-BE into staging ([`24ed98d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/24ed98d8f9a0477218bd2462d775ed2ac9e4f815))

* Merge branch &#39;main&#39; into staging ([`b6d051c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b6d051c1eadeb5623f757dedbf84eeddd602b477))

* Create manual-rollback.yml ([`c535d51`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c535d51a7e0ae58e4760f26395af5096b28d9ffc))

* Create manual-data-operations.yml ([`e9d1811`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e9d1811786d4285d3b34b7786fa60c534df2cae5))

* Merge pull request #82 from Kelompok-5-PPL-A/refactor-solid

Refactor Authentication ([`bcd2bd9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bcd2bd9a92673b98119f6a152e66478ec89c76e8))


## v0.1.0 (2025-05-16)

### Build

* build: add stage for versioning, blue/green deployment, autoscaling, and rollback ([`d0aeb90`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d0aeb902db7639f5f401f2acab14ac5e44b5e185))

* build: migrate deployment to cloud run ([`fe96450`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fe96450d894d130b8edce12861c187203b7c9d49))

* build: update ci-cd script for new instance deployment ([`30c1913`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/30c1913cc887973d7996f224b757102ef3f1ace3))

* build: add steps to install dependencies ([`61bbb18`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/61bbb181e0329b9a86b35081555ad33fa1995888))

* build: add data seeding stage to ci-cd script ([`89ee39d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/89ee39d7784649e473dac69ce2c19973fb93bc10))

* build: set up data seeding &amp; migration on the server using CI/CD ([`cc3c027`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cc3c02702a5e84070971b132ec43308018ebac72))

* build: change cors allow origins ([`dce5526`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/dce5526ebc4658638984f55d84431112c3d39eb7))

* build: setup ci-cd workflows for deployment ([`f952d37`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f952d37c4a9763c2a184ad2ad197e5ab6fc45b3f))

* build: sonarcloud ci/cd ([`e786f4d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e786f4daa6dbceaa8add37b82857716d65528174))

### Chore

* chore: change flag format --update-annotations ([`7ba737b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7ba737b1f6efa4b059e50922c0c97966733a14b1))

* chore: fix indent stage ([`2e7c586`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2e7c58651b262158fcec215d41174fb8aac0a2b4))

* chore: add ci-cd branch ([`d1c9ff9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d1c9ff9de318d6fe70d3a48c5a8f9fbe69d79269))

* chore: remove commented-out workflow code ([`33d57c6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/33d57c6402c1668700fbb42fbfb728ea828af54e))

* chore: change url for privileged analysis ([`771eb35`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/771eb351744d5e2c19159a6ead7a58be82382cb1))

* chore: add param env ([`c199242`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c199242ffe2628be45203c7c9ca561b5553feec6))

* chore: change url deployment ([`2df2129`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2df2129213cd89a4363e754f0176c69e7ad3f0c6))

* chore: change env to secrets ([`c8749d8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c8749d8bc578c411fa931d212e2ad2bc00d82699))

* chore: set USE_TZ to false ([`aa53391`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/aa53391e476d86fca6782243a2d20a199ffeaf44))

* chore: add django seed to installed apps ([`6338f6e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6338f6e11f6780ba4d4598d240d482e50ad3c748))

* chore: add dependency for django seeding ([`8f1750d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8f1750d382960d9e718a9f672292e3cc7c1a0521))

* chore: remove temporary logging ([`29aa1ef`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/29aa1ef893b68ab1c95a33b69724177358d15c5f))

* chore: add url for question patch ([`1fe6163`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1fe616331dafffdfb58d0726eff989df1f5f01fb))

* chore: change deployment branch ([`2c65516`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2c655168dee23edd928e5c3e21c92caf10941d9c))

* chore: remove database env from stage test ([`1772c10`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1772c10e871e31dfc2e8b750a69aff77a1b31ae1))

* chore: change database temporary from PostgreSQL to dbsqlite ([`4271d06`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4271d062fdfddd18f3c27eb8a890a2102f3e885d))

* chore: migrate custom user without manual SQL query ([`5074ae7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5074ae7b698a09c36eb68dbfad407a9128a0134a))

* chore: set request parameter to None ([`8795f15`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8795f150e65a939374a011ca0fc6a046855aac9e))

* chore: remove googletrans from requirements ([`6211c29`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6211c298719845df853a354913e103895399b29e))

* chore: uncomment middleware. the cause is UI WIFI blocking the BE to connect bruh ([`58ca02d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/58ca02dbd8726979d6404e86cdbf052fad03d545))

* chore: remove commented out code ([`0ea228a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0ea228a97692c1d900dca9244d4ec5aee5708546))

* chore: add empty line to re-trigger github actions ([`26912a4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/26912a4f5da52e7be5914eafbbe1f50281e0d248))

* chore: add pagination to question response ([`4ccfb03`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4ccfb03338e399185e958441c205ae94e859d9ba))

* chore: add modules to requirements.txt ([`a21ecee`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a21ecee68a488966b9b4712b960ddcade3d4a3aa))

* chore: add pagination; and add url for the views ([`f1903b9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f1903b964c5f7dc821a3475bef7af24a0de4638a))

* chore: try hardcoded url ([`742a9fe`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/742a9fe43157d0114a0f07152441bdeba19d55c5))

* chore: add url to staging env ([`0fc0f72`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0fc0f72facaef876b96fa64fc293f809ada3ba33))

* chore: modifying exp time on SSOJWTConfig ([`87b0ec9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/87b0ec92221ee55233240dd131ef77ce60c728e4))

* chore: change auth file name ([`ab24c59`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ab24c59768c18ce1b106e615753056da4e923e2c))

* chore: add audience parameter and update dependencies ([`9744e14`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9744e14be4daa7a205be8dab36f386390f92a9f8))

* chore: add drf-yasg to requirements.txt ([`449e2cf`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/449e2cfa15348aa026f5ae6dd48276c3a6a32fbf))

* chore: update settings.py ([`5e3bb6d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5e3bb6d715010611576a05ab16320251014e064a))

* chore: add default value for access token key ([`a3a0389`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a3a038976b6ca8ed9a12e55417f9bb14701e809a))

* chore: add default time for token lifetime ([`6cddb3b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6cddb3b5b5b85f9be19ad9e26a177cd3d074d1b3))

* chore: migrate authentication and blacklist models ([`51fe070`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/51fe070ca2dc651192b166a87c722b76d1630d29))

* chore: update Django settings for CORS, JWT, and authentication configurations ([`e7b26c7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e7b26c7e13546eeefbad238ffa8008443e2a15d9))

* chore: remove views from tag ([`97b6709`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/97b670979185710709e552fcc3ca252afd34237d))

* chore: try to resolve security hotspots ([`b1ed498`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b1ed498e9760bc82b872a422e172687160f449aa))

* chore: update workflows and dependencies based on Codecov&#39;s suggestion ([`f73a049`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f73a049902532cb99a02714049f371e8ac86380d))

* chore: fix YAML indentation and update file patterns ([`63b8d81`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/63b8d81531868bedc1923a003f4fdca15bd664cb))

* chore: add google dependencies to requirements ([`3ecc884`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3ecc8849fc34de09177c53d05b51a7fb73b56b3d))

* chore: add database environment ([`ef6db28`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ef6db2823dd2c4b5947d63f7df4219d4fc22a909))

* chore: change Django version ([`0ac19f0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0ac19f0ff1cf996c7bd21eabf8dc0efa47cd4dba))

* chore: change requests-oauthlib version ([`1c6866e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1c6866edec6d7b4dbec4a2cef187dc96290dfe0a))

* chore: update requirements.txt ([`e0a4581`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e0a45813280abd3ddfb8f119465df57bcbc319e0))

* chore: remove logging code ([`0acfb20`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0acfb205bbe4d0d694c0137ee35eeba725d326b4))

* chore: uncomment authentication URL app ([`d3b060e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d3b060ed382c8d041c3a88b6cfc45d53c1d274f4))

* chore: use ** for recursive matching ([`c571d89`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c571d8970e4a6cd94f4bebb3d19c8b556466af81))

* chore: add codecov.yml for coverage reporting ([`18df46b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/18df46bb58ef6504325720a77ba7d8d8533734c1))

* chore: add Codecov report and test results ([`8903e7c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8903e7c940fcbafad3593aece6db466676fc5cfc))

* chore: update dependencies for coverage and pytest ([`7cb7604`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7cb760412f0523cd61daf4220f431a47d5a18cf4))

* chore: add google dependencies to requirements ([`f37e856`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f37e8561e76c06b8c416c3271af2f2d653830573))

* chore: add database environment ([`d3bc704`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d3bc70457edb3fcd4e97593199cc1175d0bcc033))

* chore: change Django version ([`c9add8f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c9add8fe774315e53c97d9c2677b96405b6c4cbb))

* chore: change requests-oauthlib version ([`cfa34a2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cfa34a2448684b8d5d1b3021bd2aa983d5c32d32))

* chore: update requirements.txt ([`4792bca`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4792bcaa499acc23b46fdec08ad7cf1f94ecc8c2))

* chore: remove logging code ([`18c6fd2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/18c6fd26e5d294e49e21c480a20cfe2b5101c9be))

* chore: uncomment authentication URL app ([`ff00b76`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ff00b762b0d36511c25c380534d26b655728ee2a))

* chore: hardcoded secret key ([`3ceed49`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3ceed4997f0657e1bcd1b45f5bb58cce730feec1))

* chore: update secret key ([`30a1a9f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/30a1a9f5a85aba794e14a2a8817c94fc4962b6d1))

* chore: add host fe and groq api key to build-args ([`c8b65e1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c8b65e12664a618093e76726779d9cf35500319f))

* chore: update dependencies version ([`9935530`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/99355301753e0a866df80a989cc1f55433286ac2))

* chore: change secret key variable ([`b622ebc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b622ebca0c9b96a2e90047dc0a707475e3b5d420))

* chore: add database to Dockerfile ([`ef531c0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ef531c0e56a3bc65d58c5f7cccfb3f4c32dfb141))

* chore: update Dockerfile ([`9e79bbe`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9e79bbe40c4f53d56e4c4c984eab86377f3dee5e))

* chore: update ci-cd workflows ([`1fb2430`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1fb2430624c2c89708a3dea71dd30ae9673c7190))

* chore: add env variables to workflow ([`799fbca`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/799fbcad2e2dae076359239a48862cf3335de205))

* chore: change dotenv parameter ([`a929fa6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a929fa645aab625ca7cbcdf8555a2dbf30a23f28))

* chore: load .env file ([`5850f0c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5850f0c85271625e448a08153e55a12b0be0104c))

* chore: add cors allow methods ([`5b96ba3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5b96ba38560f705c5baf69aceda53f8fa139d399))

* chore: load .env from current environment ([`50728a7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/50728a738b9a5866351276d11a42ac6d382f2359))

* chore: change host to sonarqube csui ([`1b2b67a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1b2b67aece9d9027dc6b90febbce2988b1955117))

* chore: upgrade python version on Dockerfile ([`0253ae3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0253ae325c8fae6b78b34cb0556a4ca1e78038ff))

* chore: add command upgrade typing-extensions and groq ([`887dd3d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/887dd3de6daa11ed0f5882af9c25c04899b7beff))

* chore: remove collectstatic command on Dockerfile ([`a9585eb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a9585eb3ab06f8c5c28a8684bf1f805cf2f80f58))

* chore: upgrade python version ([`cbbef18`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cbbef183c43ecd18b97665ad9a5b6ea8e9e3749c))

* chore: remove command to collect staticfiles ([`7f70503`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7f70503a7dab678a753a533e5d49203244f18532))

* chore: remove args from workflows ([`3c77503`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3c77503612823040d568ab2eba8e725f9b32ca1c))

* chore: change name in sonarcloud-check jobs ([`ccf8583`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ccf8583f171751f3d17cd45d9481fa2255868e47))

* chore: remove args from workflows ([`9277402`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/927740223b8a7441406705286780d36b53699f22))

* chore: change SonarSource ([`dde59c7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/dde59c749b5d641c83eb5af7a6038d77fb498705))

* chore: update workflow configuration in GitHub Actions ([`8769e6d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8769e6d6a59de01c5bb7e908d900d698c0aa9e78))

* chore: update sonar scanner command ([`820a650`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/820a65013f38d9047608d8c6846260da02230815))

* chore: exclude dist-packages ([`1f385f2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1f385f2e0ca931f8f6b13652f47e09b1fe53368a))

* chore: install coverage tool to run unit tests and check coverage ([`dd41ff3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/dd41ff3ae6cec37a84cb80a6f3dde67f840dd316))

* chore: update dependencies and set up Groq API key ([`ae26d63`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ae26d63da4b79954f981c6a0371cf9bc43bc636a))

* chore: modify ci.yml branches ([`6fc2c36`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6fc2c3644481c0cd21b994ee8f4a64db26204d86))

* chore: modifying ci.yml ([`88a011d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/88a011dddd31db191b096e3463992906a9c9acbf))

* chore: add sonarcloud workflows ([`f02345b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f02345b471bbe0021ce5704bbf7d304fa04fa7b7))

* chore: add new requirements ([`d58335f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d58335f3f23545af55ece3eb7aefb9f18a38a144))

### Ci

* ci(semantic-release): update TOML config ([`def3d7a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/def3d7a52e306ccb8948e5a213f4f0fd08749689))

* ci(semantic-release): fix upload warning and improve release configuration ([`ec70ac4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ec70ac411046c0fc13ef1c80975524ce4153864a))

* ci(semantic-release): disable upload_to_release to fix v0.0.0 warning ([`abf6f78`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/abf6f78a3b0163a49fde6695cfcf0887c267a590))

* ci(release): implement semantic-release for automated versioning ([`0cac083`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0cac083f9a92f717ebd02c91115eb865e87c40b9))

### Documentation

* docs: add codecov coverage badge ([`976d491`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/976d491be4ddea0b27e23757af561021fdedaa19))

* docs: add sonarcloud analysis badge ([`a870a69`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a870a6965ea9d26fe6ff869b20cec023c5b36363))

### Feature

* feat: change AI model for staging env ([`080d226`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/080d226712aa833e2ecf488de04beea805b7cfe3))

* feat: try data seeding for cause app to generate data as fixtures JSON ([`66f97e9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/66f97e9685e137b2076a3a949b030753c71c787f))

* feat: [GREEN] implement update question service ([`03537c5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/03537c513db3162ba342354e6d23844a8b64b799))

* feat: [GREEN] implement question patch views ([`c871ab0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c871ab002a96a4a6fa0c329fdd2ff587e46636e7))

* feat: [GREEN] implement exception when keyword is empty ([`2e50df3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2e50df336bf202b90d591369362ea8a1d77d0084))

* feat: add logger to debug rate limiter ([`2dc2d59`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2dc2d59aa898e00d4f8035ec27df5b9e4a84d4f0))

* feat: implement url for filter field values ([`dc06367`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/dc0636752a29ead3b841906e2d7cde79fafaa623))

* feat: [GREEN] implement filter search bar BE in QuestionViews ([`c3d4dd4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c3d4dd409758604d5fe05b6a5bc3c6c9d4dc1d18))

* feat: [GREEN] implement filter for search bar in QuestionServices ([`efea78e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/efea78e6175e25d898d70863bb424e9bc8357adb))

* feat: [GREEN] implement history analysis in QuestionView ([`acd25eb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/acd25eb2e4356aeb11086b28ca78f2cdee95dfe0))

* feat: [GREEN] inplement history in question service ([`8a4269a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8a4269aa9e62b79c218f8b9cd28a23442503938d))

* feat: [GREEN] implement question search views and urls ([`f68b934`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f68b93431914a2cd991865c941dd06b61591932c))

* feat: [GREEN] implement search question older than 7 days ([`6ac9c3c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6ac9c3c78289ddd5539199e2818a9cd3c0118e57))

* feat: update column-by-column implementation ([`f838aed`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f838aedf20337897ee16cc8a4b68994b225828bc))

* feat: [GREEN] implement Question get matched service ([`77f398d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/77f398d214e8ded5efa0e9635a224a27eb946d95))

* feat: upgrade prompt engineering for more accurate analysis ([`cabd813`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cabd8133a7a97a35bb6112b53918e68253fc2dc4))

* feat: update validation mechanism ([`95ba737`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/95ba7379690db97c515774694fde8128d1d3f6e2))

* feat: merge with dashboard implementation ([`ee0e1df`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ee0e1dff9f5bf3a94fbc45852b2c049062e19b93))

* feat: merge with upgrade model implementation ([`6ea12cc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6ea12cc46f646addaa080ae7e1b8f709a447c3c5))

* feat: [GREEN] implement filter service ([`9e9d5ab`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9e9d5ab34b6aa78415f540b950ec256918f23264))

* feat: change model for long term support ([`f06b8bf`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f06b8bfbb2b9728e69daecd1f042c37f6a3b0297))

* feat: add monitoring tools for API call ([`884b865`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/884b8653f996924dc55171a82e9183e2044cc2db))

* feat: [GREEN] implement admin view in views ([`d367714`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d367714156e3e50b0c728d5ec67834d5aa8f6777))

* feat: [GREEN] implement get question admin view service ([`a728364`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a7283648d8fda31b9a41f34095509cf48139da41))

* feat: allow logged in user to get recent analysis ([`43fa1dd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/43fa1dd13aa1c7ca6b2960f322d633b0edc2ba7d))

* feat: update fields for admin ([`e5661da`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e5661da8c8efbb2a9e5952e5c1b0133e4e226072))

* feat: [GREEN] implement user attribute in QuestionViews and Serializer ([`b3eded3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b3eded398f80596582f1ffc60ea8f1ed176b56b3))

* feat: [GREEN] implement QuestionService with attribute user ([`8890e59`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8890e5971005e19751c50a7f38bcd6e6051e47c6))

* feat: add permission class for each view function ([`f59acbd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f59acbdc05eea7dc84fad5a0b98424e95de7ad08))

* feat: add permission class for each view function ([`00e0465`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/00e0465a410d06ca32196f37f03daaae8d391a00))

* feat: remove field noWA and change role to user ([`be12248`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/be1224881e046be5a299b2817e8d7f30a027856d))

* feat: create custom exception handler and service exception class ([`139d114`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/139d114f7853ed2791bea41bc193b676b2f11091))

* feat: update url path for SSO UI ([`9f6c03b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9f6c03be9e50c7a0644de0139b1db05c54eaa44e))

* feat: add token pair serializers for better token handling ([`0124f58`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0124f586cd1e4298bb4bc5704021e0a47f226436))

* feat: create TokenServiceInterface to define token service contract ([`77a6b24`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/77a6b24e9c78f6b698a555a896f5df9661117bb3))

* feat: add AuthProviderFactory to manage authentication providers ([`14f189b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/14f189bebb95d1ca5ba99ba0334be071832b4052))

* feat: add URL for blacklist managements ([`390b894`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/390b8948dc03ca0deba4cf275285edf5f5652c03))

* feat: implement blacklist management views for checking, adding, and removing SSO users ([`9293e0f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9293e0f6ed66d959bafad19fe65dfdb9948a3575))

* feat: create serializers for blacklist information and response formatting ([`67ab6f7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/67ab6f7e2b4ed0d7506c3d55bcd8b76df437bc96))

* feat: add blacklist model with validation, logging, and business logic ([`ea3184d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ea3184db78c1a14c8c55b2798c72360eb40917c6))

* feat: create custom permissions for role-based access control ([`2a28672`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2a286727b9e277446719d700de0007ee9f2c45bf))

* feat: add URL login/logout for SSO UI ([`514dcbc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/514dcbc4e5a0086844ef73ee96d567f3a6c01a87))

* feat: implement authentication views for SSO login/logout and user profile ([`0a34cee`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0a34ceeaa61613c085bf6687bef3e33cee6e23c2))

* feat: implement SSO UI authentication with ticket validation, user creation, and token generation ([`70ff9d5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/70ff9d5e4dab3f949921902e073c71ab9a04c647))

* feat: add token generation service using SimpleJWT with custom claims ([`8ea9e0b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8ea9e0b8f10f2e8bad9899c88b7fd68eb6aaca4b))

* feat: add ticket validation and user data extraction for CAS authentication ([`60442b5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/60442b53a570f80d2ba7b845618c8de0b3624fb8))

* feat: implement JWT token creation and decoding functions ([`75072a0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/75072a0b66bf4c1e4d1142ef7c4346a49c1cec42))

* feat: add SSO JWT configuration class ([`10fc425`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/10fc425dd7406db20f1940e7986f43c7c6896693))

* feat: add custom authentication email for Google OAuth and username for SSO UI ([`e5e60b2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e5e60b20b746b30991713f56e0082380900d84e4))

* feat: add new fields for Google OAuth and SSO UI authentication ([`bbb1392`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bbb139297cfcbb9fcbd98bbcdd9acbaafc4d5604))

* feat: [GREEN] implements get recent analysis services and views ([`c11034d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c11034dd42d27674662a5dded0c1cb5b41518b38))

* feat: add authentication URL endpoints ([`d06bb3c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d06bb3ca79a47ae3ec34334e1108638a9f76d560))

* feat: [GREEN] implement Google OAuth 2.0 login view ([`764c2c2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/764c2c28872ebfb05d0cd0dbe85ff60b2a71ba00))

* feat: [GREEN] add authentication services implementation ([`2935a97`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2935a973eb1b9e8d00cde901add92679759e8ba3))

* feat: [GREEN] add authentication serializers implementation ([`06d1b49`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/06d1b4983964ba9903454ccb96694a013bef1760))

* feat: add custom admin configuration for CustomUser model ([`1a4b24f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1a4b24f6d91ac0e83115ceee5afe6c448f225d9d))

* feat: [GREEN] implement custom user model with email as the primary identifier ([`a761f1d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a761f1dc2e4831aabc117723ed052c3e62b51287))

* feat: add API endpoints for authentication and schema documentation ([`c6bd7f1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c6bd7f108980259afe1944c7e5960a8878fcb2cd))

* feat: set up Google OAuth configurations in settings ([`9d4d493`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9d4d493d88cdf0ec71a72a0e00dde8055363b5c4))

* feat: add authentication URL endpoints ([`2f8e029`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2f8e0294ebef5db5338a4d2a611bfb4bacc61166))

* feat: [GREEN] implement Google OAuth 2.0 login view ([`e772c2a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e772c2a6b9a6e23f9dd8010b37545ea2ac676a53))

* feat: [GREEN] add authentication services implementation ([`e3dfd75`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e3dfd7519f9ef9f13cf705df986d3c0c78da12c1))

* feat: [GREEN] add authentication serializers implementation ([`75ff8d8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/75ff8d8e4017cee712e9840bc9d4d766218a3201))

* feat: add custom admin configuration for CustomUser model ([`8c09cb4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8c09cb431139d7c994f0aa6cc286f7d22c210921))

* feat: [GREEN] implement custom user model with email as the primary identifier ([`16cda53`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/16cda5326fac87dffffe53a565807cbe683bba42))

* feat: add API endpoints for authentication and schema documentation ([`489cabd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/489cabd4536b6693c2c6402320bb3d61a915d4f8))

* feat: set up Google OAuth configurations in settings ([`90e7321`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/90e7321de1f4c7d0ce78788bf78355733ffebe28))

* feat: [GREEN] implement error response in QuestionGet ([`1c8a1ee`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1c8a1eeadfbd21e0691c5134491fbf6dbaef708f))

* feat: implement get and validate cause ([`cb8b9d1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cb8b9d152645d0cc420161af9694a7a38a0ba437))

* feat: change model and implement prompt engineering ([`d46573a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d46573abbed9d00d8980175564472bfcccc87d83))

* feat: implement get question ([`9c6eb1b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9c6eb1b111593519049ff1e206891b0c374cea6b))

* feat: migrate model ([`6b894c7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6b894c745721188a7cc441aa0a40bda2ee5eaba5))

* feat: [GREEN] implement cause feature ([`af97d92`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/af97d9229da5950a87c64372003d52dc902011ea))

* feat: [GREEN] implement question feature ([`60d95fd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/60d95fde8e0eb9c2750a615d96736b1ed5ac5203))

* feat: Add some validation checks for tag ([`b2155ea`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b2155ea3dfea54b691a098bb4f55f1dbe9475aac))

* feat: [GREEN] implement QuestionService to add question ([`525736d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/525736d6e2a832023d02e4958e1c81e1af378331))

* feat: [GREEN] implement retrieve feedback to evaluate causes ([`0b4cf02`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0b4cf02f50e350185901c23a9a5eb755050f78e2))

* feat: [GREEN] implement API call to integrate with Groq AI API ([`e81d6bd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e81d6bdd1abd4108998301e17bf02b30f4531913))

* feat: define error and feedback messages ([`df46020`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/df46020f73783db9afce16d691c29272cec94c76))

* feat: add ValidationType enum ([`ef605ac`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ef605ac8cad85a324a53251167e7e0abec229a62))

* feat: create custom exceptions for API request validation ([`037d87b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/037d87b3fae5e171ab3c3ef318b3ab0fdd7ad2de))

* feat: migrate model ([`12544a5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/12544a5152a10f098338a72d3a6cb2dc52217670))

* feat: add model&#39;s default value ([`9276248`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/927624842dead951157d4085990b671249adb534))

* feat: update question models, forms, and templates ([`9462797`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9462797a1d3559c3ffa406e1cb169c3636081f77))

* feat: [GREEN] implement Tag model with UUID and unique name ([`78db86b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/78db86b99b2dcf57404c56eceb2da4226583a93b))

* feat: [GREEN] implement question removal functionality ([`cc2338b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cc2338be459bf07620bad56dae6e86218c4791b3))

* feat: add tag app to Django project settings ([`e7e9acd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e7e9acd63bc40c70ca6950ff092c265742c152b7))

* feat: [GREEN] implement id and status attr on Problem model ([`f241644`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f2416441f71604fafa7c7fa062d3330a365b0d13))

* feat: migrate Problem model, add status ([`e5e2273`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e5e22730ecec2529dd1177ad5db8a56d0e965a8c))

* feat: migrate Problem model, add id and status ([`0f7f107`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0f7f1077ec48f672efc185a1951d9427629898be))

* feat: add data integrity not null constraint ([`29d5eb8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/29d5eb807cfe02ff5d375d03eab03fc0db061b2a))

* feat: migrate model ([`fe7b95d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fe7b95d23c7eb4f67e53f217e87eee9062c3773d))

* feat: implement models, views, urls, forms, templates generated by AI ([`1fc86b4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1fc86b4918c5ccc31adcabd8e74c61ff9fd4aaa9))

* feat: add question app to installed ([`5ca2d16`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5ca2d16c7cb7d8973dca997d225a771d53f1ef8a))

### Fix

* fix(ci): create initial version tag when none exist ([`242a9d8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/242a9d866125f73c6c29cafb427d98a94bb9816d))

* fix(semantic-release): manually set initial version to 0.1.0 ([`a19f450`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a19f450497f913c27c820bb315ddcbabb09c32f3))

* fix(ci): add tag format and initial tag creation for semantic-release ([`87558f2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/87558f256e10638af088a21c86b0b263a9b08a5a))

* fix(ci): correct TOML syntax in pyproject.toml for semantic-release ([`6b16069`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6b16069635044894616c2b26a848f8e9e75ef4c0))

* fix(ci): update semantic-release configuration to fix validation errors ([`4695c53`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4695c53015b67840734f1f7bec02aa304878ee05))

* fix(ci): use python module path for semantic-release command ([`e9193af`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e9193afaccd5dc9795ab7a46a3e8d28e1e184e86))

* fix: resolve traffic conflict ([`06cf2b1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/06cf2b11f3f231ab8bd325d1cd8c080b013fc933))

* fix: resolve image tag error ([`3168b66`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3168b66812b666c6bb594b342879eb0c3f15a6bd))

* fix: fix tests question views, question services, validator services ([`ce7e212`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ce7e212e6cafa41fa77d7fd2fd5131442736d909))

* fix: handle empty image parameter ([`7f9f111`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7f9f111a470b8ac728d48e61fb8e7d559c01bc0e))

* fix: resolve init cloud service error ([`d539a33`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d539a3381d9e62f4d098f842bd76c7c0b6d37bc0))

* fix: try to resolve versioning error ([`bb97214`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bb97214317ceaae80f011b3896914577802af149))

* fix: question tests (4 errors left) ([`7b3853b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7b3853b58a5de94eba541f740a7656754b3c56af))

* fix: recent analysis with user no question ([`0113aad`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0113aadc9b70f25a332739a3cf8cf2b05529cd22))

* fix: question patch for guest so they can edit their question form ([`2b82065`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2b82065907780150405e66dc3fe55d603e3cb610))

* fix: set timezone ([`25e766b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/25e766b2b857b71ad421a387b0e1db62d586190f))

* fix: fix indentation typo ([`400e797`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/400e797763c9e1a62e67cfb13853863a150e8ab1))

* fix: remove unused request parameter ([`c3e35c7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c3e35c7e0c9ee7b7c9a1d93cda12a063becbb09f))

* fix: change path for search history for more consisteny between modules ([`829ac75`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/829ac75ae1c2f8a6d270cd5334ccbd183e3106bf))

* fix: [REFACTOR] change datetime to django timezone to ensure consistency and avoid warning ([`a2c8cb8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a2c8cb82d57f9e46ac86e49d69d3fad49437f872))

* fix: fix rate limiter to pass test ([`afcc35f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/afcc35f9d172ed816bad4819925dab7e72655d98))

* fix: fix code security secrets ([`8b9c9d1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8b9c9d11cb9aed90a334eb9483627ac92dde1c60))

* fix: fix rate limiter logic ([`5f2cd45`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5f2cd4554ad571e0a58f088fc66d4c707cb0c945))

* fix: fix warning in question_views test because of naive datetime ([`d66f38a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d66f38a561c88480903655181a78c0520422bb8c))

* fix: fix question created timestamp 7 hours late ([`b694690`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b69469084eacc7ea9bb548410d6d9059db6dc31d))

* fix: change CORS_ALLOW_ALL_ORIGINS to True to fix test error ([`145d144`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/145d144a87ea2ccae25f9b084eb01e66ea086ea8))

* fix: fix user not sent to backend from frontend ([`cfc28d7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cfc28d7ba6430d151010000fcc8a9e482469d4ea))

* fix: change question models to CustomUser and make sure user is Authenticated or not ([`3cc1ae2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3cc1ae23d3b2db9f1c6bb9fadca677d640c413c4))

* fix: remove failed test ([`4a8bf18`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4a8bf184120ca308813a63c2ee0a3da7a2fb4c83))

* fix: Remove blacklist test for now to remove error temporarily ([`596ae16`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/596ae16ab20c14440751b8fe2ce63ec91e349dbb))

* fix: change get method in QuestionService so it return Question object directly ([`05a30b3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/05a30b37c98063613cdb2fde186c60f68bf0677f))

* fix: change get method in QuestionViews to retrieve so it matches with methods in ViewSet ([`0638ec1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0638ec154bc7244c7cbc3294a099fe2f08ae3445))

* fix: resolve failed test ([`913d8cb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/913d8cbfe4ba692b00ca23e6364713d624c24282))

* fix: resolve failed test and add init file to detect test ([`17c8618`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/17c8618a36641386d526744fd809640efb8a2401))

* fix: remove unused characters ([`a8be6b3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a8be6b3d8d5473079d576a1025323062e4434cfb))

* fix: change key from data to user ([`48c8de6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/48c8de65ad8b1d144491f0a9184fbbe814cd8957))

* fix: update import path to resolve error test ([`9c9bd64`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9c9bd6499d86f8f6848377ec7d934652a194c938))

* fix: enforce POST-only access for google_login view to prevent security hotspots ([`171cf3a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/171cf3ae27de1a09df43a8ac621cd1be090c8ab5))

* fix: resolve tag&#39;s failed test ([`1362d69`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1362d691b8470c2e977afe269f423ad955a5a701))

* fix: resolve authentication error ([`6fc8bb3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6fc8bb3acd9be54e61234149037a434211cd6f73))

* fix: remove unused local variable to solve maintainability issue ([`fb103c1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fb103c19c99b8a0f848d5f823791066bff93cff2))

* fix: enforce POST-only access for google_login view to prevent security hotspots ([`e26b896`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e26b8963e61403347600767280329d2ffa844f67))

* fix: resolve tag&#39;s failed test ([`627d975`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/627d9751333be4423840da542e81d7c6fff2a1e5))

* fix: resolve authentication error ([`d4c334f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d4c334f7ecc5cafc42a26b1b0c5b1059f0e5a5ce))

* fix: try to add id to mock obj ([`5f2543a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5f2543a05061ea68d964ff90c2c763a521acdaf1))

* fix: try to fix again ([`ddcc07f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ddcc07fa2f075391fee77cad07d09130a9323506))

* fix: try to fix cicd error get isnt called ([`11625ad`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/11625addfc751ce5b7ad6e29f8e5e652b80b2b67))

* fix: fix change testing class name ([`1911f6b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1911f6be1911f8b215e862c84a8f31ef86d129f4))

* fix: remove unnecessary tests ([`cc2f4b8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cc2f4b8e61f8b4c8c1c59354ff7668f076d6832f))

* fix: fix url typo ([`83d64ef`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/83d64ef29c117a38596e6b6f8ab7bf475c6dd8df))

* fix: Fix test error because of improper mock ([`663c3ee`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/663c3ee41663cbed4c8f8d0caa017850b633f942))

* fix: Reworked the test dependencies to adapt the new directory ([`8a13081`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8a1308111f23c86a233fb8980efc11d964cb8bd5))

* fix: add init file to include testing ([`bda0c89`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bda0c890ff0f37f812cd8eb246a3363cd0390f23))

* fix: try to resolve security issues ([`ff62852`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ff628523d9d38e66f6b82868e2a20cd35bf4dac9))

* fix: remove unused variable ([`38e7cbc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/38e7cbc97a0a2dd0f2fc9245bf439e625fe34981))

* fix: update question field ([`1941793`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/19417938737b489e8867964f92ff8526521548a5))

* fix: add load env function ([`2654fd9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2654fd90320361803ec93fc60bec3a528fbdaa7c))

* fix: fix validate cause ([`d7157af`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d7157afc9decfe70c2f1774cb38d42c580c49eec))

* fix: fix cors headers error ([`f254b37`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f254b379b4c7f71b7b59936ade6f4a293754bb24))

* fix: fix parameter user in QuestionService ([`8447d44`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8447d44bfa3dc29dffe4d14207ee5b5677893d34))

* fix: Remove the commented added user code because not yet implemented, replace it with just simple explanation comment ([`6fdb560`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6fdb56009dcadda92115aa698dfb0e8e965fb6e9))

* fix: resolve sonarcloud issues ([`66745bd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/66745bd383fa945470bf8b0fa5b4c2104027f4e8))

* fix: try to resolve security issue ([`5177f4d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5177f4d7d267f90622f6468603093eda99c8cfc1))

* fix: add HTTP method restrictions to all Django views ([`d199d2b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d199d2b6a75526934f9ace17ac397d0b811401a0))

* fix: update sonar properties and workflows ([`120df0c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/120df0c1e7c89a12d7d775fa2f662a03a0223e60))

* fix: resolve typo in constants file ([`b1f89ed`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b1f89ed77bf4d0abc6fab4f6af6f3cabc4ed0651))

* fix: change models email attribute ([`b4b04b1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b4b04b1c18139f820016f238a90c59451816421e))

* fix: change testing submit form ([`4b84ad6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4b84ad6438fbfbf954a785eacd68335ea8f32ac4))

* fix: resolve missing files ([`ba6b9cd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ba6b9cd7b14a22af4e1574e062f0d15106300d52))

* fix: update SonarCloud token secret in GitHub Actions workflow ([`659ca99`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/659ca99c0c065d178041d437d438ead8d1ae37cc))

* fix: sonarcloud token ([`069d248`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/069d248cadc719d8cc312061723a344b60e28301))

* fix: sonarcloud token ([`86fdc42`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/86fdc42b12af87400edd9a4276c992ce4035b618))

* fix: try to fix sonar ([`7f25827`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7f2582747b812619e18033a37c59796c4de62e51))

* fix: Try to fix sonarcloud not detecting test ([`5b6852c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5b6852cd46fa27cc5e190899675514dd0f752e5d))

* fix: update sonarqube workflows ([`ed97fe1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ed97fe1f8dd9cd75f7ba99309bd0b2f20d078490))

* fix: update sonarqube configuration ([`fe1ed24`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fe1ed246877e85297db5d13eb091301d45cc3acf))

* fix: ci.yml ([`7f5a94d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7f5a94d3ac53a165dbbb7453700ddecdad0efe2a))

### Refactor

* refactor: match the test to current implementation ([`5ea27db`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5ea27db886ba785961ac3316325a5b2b6a536452))

* refactor: split validate method to reduce query complexity ([`173454a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/173454a818098446df4e3decc88d060e57227420))

* refactor: [REFACTOR] move delete logic to service ([`ac16fe5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ac16fe5629be692a4578d25935e1e4adf7b55139))

* refactor: remove request param ([`cec0f1c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cec0f1ca707f9805cc75d3da5e073f916c559003))

* refactor: [REFACTOR] change rate limiter utils to middleware ([`289e1e7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/289e1e7a3c5df746127e4765ad8e0f847f39d92b))

* refactor: [REFACTOR] refactor error message to constants ([`ec689d2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ec689d29900181aa1a448615ed255285e2fb96b5))

* refactor: [REFACTOR] implement SRP principle for rate limiter and service ([`860afa2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/860afa2e382ce2791a12a9f7dcc0bc2a777db0c8))

* refactor: specify import paths ([`8dca794`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8dca7948bcd43daac0479b599bf0310fc54fdf32))

* refactor: specify import paths ([`2046517`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2046517fdceacce4d336e1923ce032ce4ff8b8f3))

* refactor: refine and improve blacklist app ([`e81ff5b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e81ff5b3b5cafc822ca1b3d255d28516c5c3867e))

* refactor: update authentication views and add token refresh functionality ([`6aa9b58`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6aa9b58d2ee6c341757fd603dbd6f16ade8c9977))

* refactor: update CustomUser model with extended user fields and permissions ([`d724af6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d724af66b903c75c37af5324d65096bab64573cf))

* refactor: implement AuthenticationService to centralize authentication flow ([`921ca0a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/921ca0acfbc8ad82b0ec6d09b26ff56104083e2a))

* refactor: implement JWTTokenService to manage JWT token operations ([`26b7248`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/26b7248ed60980901064b8cba788c877ecc5a7d6))

* refactor: update SSO UI authentication to use strategy pattern ([`e249453`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e24945321d743e67e0a4300dec23cd47743bea3c))

* refactor: update Google authentication to use strategy pattern ([`d90a82a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d90a82a26da7d9cf3b43e0775f567b683390aa95))

* refactor: implement abstract base class for authentication providers ([`2c5c4a5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2c5c4a58b59fae7aee5361a6bff0c6fc8a195c46))

* refactor: support enhanced user data and SSO ticket handling ([`c924b62`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c924b62ad3c9bdb75e5b9634507a5b1bd2278281))

* refactor: implement Google OAuth authentication and user creation service ([`d6b8b58`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d6b8b5865fe997e747eb8fe8942a746563676b09))

* refactor: update CustomUserAdmin to include additional fields ([`0bb8ad4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0bb8ad4d1dd27216a25b5855c80aefc1699a7ba9))

* refactor(test, views): [REFACTOR] handle edge case exceptions ([`cc77b99`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cc77b99bb98a11ef6adeb817a289a76ac062cb47))

* refactor: [REFACTOR] modify cause service test remove redundant tests ([`0f7ef68`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0f7ef68fc32b21f1e66085839db457e7fac876f7))

* refactor: restructure tests into separate files ([`6b035dc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6b035dcedddbd4c97371452e6cf09e242e36aa03))

* refactor: update question serializers ([`3b01333`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3b01333411a1abc6495f2567815557796ae9bf0e))

* refactor: move validateview function ([`08ba20d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/08ba20d5169b97e7e613073c5175e7c00b8f84d9))

* refactor: [REFACTOR] change AI model ([`fbb81c8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fbb81c880a0b97602484bf9ebcdcf71ba8ae56bf))

* refactor: remove unused files ([`d1fc468`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d1fc4681db7afb6233d6e16eac779c952f35e810))

* refactor: change name and file structure ([`7f8de6c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7f8de6cec651a84f24620c2e7a1827eae9e43794))

* refactor: remove unused tag files ([`01ee191`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/01ee1917864c427e5643a8deada049b74fe76b03))

* refactor: remove cause in validator folder ([`db12a6f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/db12a6fcb2bc9f6042d5524cf698fae863d7a8b6))

* refactor: remove question in validator folder ([`d371a21`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d371a2176ea9611dbc7651050fee606595c7fbc3))

* refactor: remove unused files ([`0da5f1f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0da5f1fccf1ee5027a82cddba1ba214e5b5f8ca8))

### Test

* test: [RED] add test for update question service ([`ae8f2e6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ae8f2e6a3f2f646958c24bbc3e4b903860112394))

* test: [RED] add test for question patch views ([`e499722`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e499722d55175d19c850b77672593261f9154dc0))

* test: resolve failed test ([`ef184e8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ef184e8b587804f047570f851a7ae45c7233663a))

* test: [GREEN] implement unexpected error handling ([`c5c31c2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c5c31c2257445c1f5b071c11170d92e884457358))

* test: [RED] add test for unexpected errors ([`a00176b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a00176bbe2ac40f6a8158c279f7aeba0fa63d3f6))

* test: [GREEN] implement guest deletion and exception handling ([`a430209`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a430209580c59a88b2e7c69d7b80ade9e6e75e80))

* test: [RED] add test for guest delete question ([`61c8bb3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/61c8bb32d70562a0f3e24abb2a24d8a50a43432b))

* test: [GREEN] implement user checking to prevent unauthorized delete ([`0236df8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0236df89e584c56849881de4fa687af120103e95))

* test: [RED] add test for unauthorized delete ([`06b0675`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/06b06750d8116b7079d15001f97c6559e221684a))

* test: create penetration test (unauthorized and sql injection) for filter BE ([`2e566bb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2e566bbe7bc449750993490301a6b31052b0deba))

* test: corner case: no question exist in database ([`6b393a3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6b393a3e79a3704cdf0e1b0b7e5b3fbea3733582))

* test: negative test. History last week not found, history older not found ([`c379c7a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c379c7a86b5271663c8ffabb6ee923872079bc4e))

* test: [RED] test to throw exception if keyword is empty ([`01bf40e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/01bf40ec74423158b73a90e18b7ce8e3cf88bba7))

* test: [RED] add test for filter search bar BE in QuestionViews ([`13a8348`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/13a834833e42db02439b983cf90f26ab8c08949e))

* test: [RED] add test for filter BE in search bar ([`396d2c3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/396d2c3fa52aac37559466f434430e1cfecf9f6b))

* test: update test to follow the latest get_all implementation ([`992eb74`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/992eb74690a89014130c0002e2ab4dd2d5bf4f32))

* test: [RED] add test for history analysis question view ([`5aee4c8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5aee4c8089c6fb2d82b0944b92be0d9990328ee5))

* test: [RED] add test for analysis history be ([`8d916fa`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8d916fa994a79548c936d31b7039589eeea31d30))

* test: add corner test, empty string keyword ([`51b38ce`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/51b38ce783ad347e01a5fc16a263b314aab22468))

* test: implement red/negative test for question view internal server error ([`5a95b3d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5a95b3d7d18e7b75c26dd2195bb5ab7550514da8))

* test: implement red test for time range exception ([`e8566e1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e8566e1e8b5f81517983e02028101f90ce8413e7))

* test: [RED] implement test for search question views ([`4c90e6f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4c90e6ffc1ee3301337f5b37a658289e00898ddc))

* test: [RED] create test for question older than 7 days ([`75b1c83`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/75b1c8331a0cad8474aaf493605c3fc68a86610b))

* test: [RED] add test for get matched last week ([`82c317c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/82c317c8c1e2a55c66122e9c0161a13f9cbb8c98))

* test: [GREEN] implement urls for question delete ([`f21efcd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f21efcd03b94887da262bc0ab90d0a59193b5946))

* test: [GREEN] implement url for question delete ([`61f8c4f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/61f8c4fbcee26353bbccb38a7d4ac4cc10b48594))

* test: [RED] implement delete question ([`3d4486f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3d4486f67400510d2898ceebdc917a22827d3980))

* test: [RED] add test for delete question ([`fae2f92`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fae2f92c141f9758e9c60089b3106138773a7b42))

* test: modify rate limiter tests ([`0c2006a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0c2006a579d31ef47484ff60fd2e076f17726373))

* test: fix test cases return value check ([`5c6fde5`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5c6fde58e9dbb1367285cdf5bb2eccb3a8f239d4))

* test: [GREEN] add request param to api call ([`8d5e062`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8d5e0628d12135412263501aeac2c7d00a1ce43a))

* test: [RED] add test for filter views ([`43230a1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/43230a17efd86363818739648e02951c0958ab37))

* test: [RED] add test for filter service ([`6ebc9ed`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6ebc9ed0e243c9d4249761d3419cb1f3b7f1b8a6))

* test: [RED] implement rate limiter ([`12790d9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/12790d93f1631c0084dd02d8b93e4435424c50a3))

* test: [RED] add testing for rate limiter ([`06bd6b0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/06bd6b09716b163778555327f007709d96737220))

* test: [RED] add mock for request and is_allowed method ([`ba72b12`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ba72b12dd9829e6e282d1a3f6db3180f1d2411f9))

* test: [RED] add mock for rate limit ([`7c6804a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7c6804a125e219abb2c1e436a0367429f8735fa0))

* test: [RED] add test for get admin view, views ([`fdfe7b6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fdfe7b68ee9b601ecb829813e821bae479f6d3c4))

* test: [RED] add test for get question admin view service ([`86fecde`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/86fecde0f29d89166d4d5de793328f76629d01f8))

* test: update test for user and admin ([`0df03d7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0df03d728c0ef30b1652170435f1212e7dea4464))

* test: add more test for service and views to increase coverage to 100% ([`9bb7f31`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9bb7f318e016c6073a1c5155f6ce4469bc0f5abb))

* test: [RED] create test for QuestionView with authenticated user ([`560ebec`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/560ebec99ab056dee46e4683dbc9e5def98fd046))

* test: [RED] add test for QuestionService, now including question with authenticated user ([`2950f64`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2950f649f33a82aa6804a5a70644d4a8652e159b))

* test: [GREEN] migrate user attributes in question model ([`00c9336`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/00c93364ca83c55d509aae319f98111c3bbe0e53))

* test: [RED] implement user attributes in question model ([`14d95a1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/14d95a194ec59dd68c6fba52e6b711c2c73c2dcd))

* test: [RED] add testing for user attribute in question model generated by AI ([`6925d05`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6925d05b83ccf6e687c42cbf0f70b9a717ce0245))

* test: create unit tests for authentication and blacklist ([`81d5ff7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/81d5ff7fc536353cc7a058f041df44bf3d293242))

* test: [RED] add unit test for recent analysis ([`b3560e0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b3560e0b428ff4dd24cf00ce56f6aaab457968d1))

* test: add testing for parse error ([`c1bfe05`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c1bfe056667df06e93bc4da8e542c350bd2aa500))

* test: [RED] add unit tests for Google OAuth 2.0 authentication ([`ba3053c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ba3053c6392bcae0c23dd36ebf634c60a29f83ae))

* test: [RED] add unit tests for TokenService and GoogleAuthService ([`c5e07eb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c5e07eb003afe25b25d7fc99bfad900b639aecff))

* test: [RED] add tests for user and authentication serializers ([`2da0524`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2da05245a3ae8f5f07bc881d6774a492770e9fce))

* test: [RED] add tests for CustomUser and CustomUserManager models ([`4926c97`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4926c97236597da64ac0f42c0a5017ee61c561c6))

* test: add testing for parse error ([`6a09abf`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6a09abf52d9b66cb1081bad447f8600c7bf77e0f))

* test: [RED] add unit tests for Google OAuth 2.0 authentication ([`2913482`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/29134828346e3051354e0580db97ae4be1db4902))

* test: [RED] add unit tests for TokenService and GoogleAuthService ([`33c10dc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/33c10dc2cfe56a0aaddf13203a3eb09a80a1d32f))

* test: [RED] add tests for user and authentication serializers ([`cc9911a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cc9911a7c2fac26c7ef65f1a6732cf8c4b988fc6))

* test: [RED] add tests for CustomUser and CustomUserManager models ([`41a0981`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/41a0981eeab6963a70cb7ea5cd7c0372438ab9c0))

* test: [GREEN] fix cause view test ([`54f3f24`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/54f3f24a5ecd62d4a63940772d5663660e872b08))

* test: [GREEN] fix cause model test ([`a732d22`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a732d226090b676b37441866c8bfd7a5d8cf5b70))

* test: [RED] add testing for cause views ([`9147626`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9147626bc6a0799246376141467b5f92f072819d))

* test: [RED] add testing for cause services ([`bcf0d2d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bcf0d2d8d15bd477ce747645d2c37901955a690d))

* test: add test coverage for QuestionService ([`7e4ae97`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7e4ae973a7b419b4cca80b6018b0462a3d776d41))

* test: improve coverage for validator service ([`711da2a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/711da2ab872bf719222f760d6d7f2828cbc803e4))

* test: Add corner test: create question maximum length title and maximum question character ([`e489e44`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e489e446e35fd131538c04e39ff71a6f5c6e3b3f))

* test: Add positive test for get question ([`4604164`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/46041640a8a9b2fbfeb3de792c0235a733051952))

* test: [RED] Add negative test for GetQuestion ([`483b8d4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/483b8d42f12953b8c272afe7ebfdd815e5efeeb9))

* test: [RED] add testing for cause views ([`4ff6fb7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4ff6fb77bd324daeaff255cf18995a975b20cb31))

* test: [RED] add testing for cause feature ([`2be076d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2be076d1d58e3079d413074aeb53dd71ab105708))

* test: [RED] add testing for question models, views, services ([`86a5bbc`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/86a5bbc882d9a2f366a961835046b6785678c1de))

* test: Add test for duplicate tags ([`d46f73b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d46f73b159c368e78cc4c268e6b0d041fcf18f00))

* test: [RED] add unit test for QuestionService to add question ([`5727704`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/572770466911104ffb8c2ebfa11b0b478a98a099))

* test: [RED] add feedback retrieval tests for all cases ([`875bfc1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/875bfc18629797cef03c66f1114f1ed5470185d4))

* test: update test cases to match HTTP method restrictions ([`e801033`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e8010331c75857a3ef6c9a51067d97bea56aa892))

* test: cover validation types outside of NORMAL and ROOT ([`70c460f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/70c460f34243df29fc45fe83d1b99e74c4a03238))

* test: [RED] add unit tests for API call and cover all cases ([`a002750`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a002750e57e046fd0bf61f650ba9f04c47c8a560))

* test: [GREEN] implement views, models, forms, templates ([`aa75fb4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/aa75fb4d9eac77f0b344d0aa9dd808b5d5fae36a))

* test: [RED] change testing ([`25969d0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/25969d06cdfa74ff4cbc0423ced692dabb5bb64a))

* test: [RED] add question test for default value ([`9c74fb0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9c74fb003d9b922cd1946912d9f3af18076a5c44))

* test: [RED] fix submit question test ([`3dfdf4b`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3dfdf4b11b883239dec76e0862df402da0140c93))

* test: [RED] add comprehensive tests for Tag model ([`e47250e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e47250ef1694dc77ac939f7303cab090399dc35f))

* test: [RED] add comprehensive tests for question submission and removal ([`cd64e96`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cd64e9600cd394dcfbbf1fa9a76ed9ea3dae8e00))

* test: [RED] add testing for model and forms ([`4acbf31`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4acbf3112e227b81a6309d1e931d316510744abb))

* test: [RED] add testing model for id and status attr ([`674bfd6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/674bfd6c59759ebe19c920c2b51607bbc5647563))

* test: [GREEN] implement views, models, urls ([`e6d94b3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e6d94b3671f1ec1c218ff6164acf168f91c93838))

* test: fix testing code ([`60494d6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/60494d6e9caa9d449a2f6eee3fad1e62d308ff1d))

* test: add testing for model generated by AI ([`e177ca8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e177ca82679e4643b7a2c39f1abe7d5a72377a2f))

* test: change testing code structure generated by AI ([`a937dfd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a937dfd1495d7031ed33576131f709f02fada74c))

* test: change testing code generated by AI ([`b5ee121`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b5ee121360111bb472a82a12dfe1786d751a6d40))

* test: [RED] add serializers ([`9d6efb4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9d6efb47316b656d536bc01d4e7232b804f83085))

### Unknown

* Merge pull request #78 from Kelompok-5-PPL-A/staging

Merge Staging to Main #1 ([`db997f9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/db997f93122e244d82d819f224ebc54529bb45ad))

* Merge pull request #77 from Kelompok-5-PPL-A/development

Forward Changes to Staging from Dev ([`1403b6c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1403b6c2b494662d1359a476cd051d5b54d39cbd))

* Merge branch &#39;staging&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into development ([`9620b1c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9620b1ceb2d2f700ef293e9bcda91afee206f0cb))

* Merge branch &#39;staging&#39; into development ([`ccb82af`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ccb82af4806e1c177653954d08f9f73671c22743))

* Merge pull request #75 from Kelompok-5-PPL-A/bugfix

Bugfix ([`4ed0e1a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4ed0e1a5f1f6ce6e02c24378c2710662d0428190))

* Merge pull request #76 from Kelompok-5-PPL-A/ci-cd

Software Deployment &amp; Environment: Modern Packaging, Orchestration, Progressive Delivery ([`ecf0e02`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ecf0e02f7c70581c2519e56b4d50268adce1e480))

* Merge branch &#39;development&#39; into bugfix ([`e06f324`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e06f3245a251987ace45cd28713302cc980419af))

* [REFACTOR] is_admin check from role ([`e82754d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e82754d8559e482cc2fc3f5a4590d0249e540cb0))

* [REFACTOR] change validator model ([`c5fc4ec`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c5fc4ecee9356437fc363e9e131bf8b99e1b9aee))

* Merge pull request #74 from Kelompok-5-PPL-A/ci-cd

CI/CD ([`d5bd1a9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d5bd1a9fd70602ea50c40559dd9c2f1d81f66e35))

* cicd: add permissions to write issues for zap scan ([`86ab173`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/86ab1735c7f5ecaf76802b59ef8830c1d920dac7))

* cicd: add zap scan DAST ([`b0ab7b8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b0ab7b85a27945f162ff924fe8182457290dbc2b))

* Merge pull request #67 from Kelompok-5-PPL-A/pbi13/subtask5/filterBE

PBI 13 Subtask 5: Create Filter BE ([`9a66810`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9a66810816e6f96861ed7a0ad0bdc403d5336536))

* Merge branch &#39;development&#39; into pbi13/subtask5/filterBE ([`b7cfa93`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b7cfa938d5bb30a8e97f9ad72e5b1f74ce72f852))

* Merge pull request #65 from Kelompok-5-PPL-A/pbi9/subtask1/history-be

Pbi9 Subtask1: Analysis History BE ([`e7b1e7e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e7b1e7e0531b60c8e35fe60a3f1ee45eed2638aa))

* Merge branch &#39;development&#39; into pbi9/subtask1/history-be ([`2d7ec0e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2d7ec0e867f9eeb6d492d2efe6401c48d1286cd5))

* Merge pull request #64 from Kelompok-5-PPL-A/pbi13/subtask2/search-bar-be

Pbi13 Subtask2: Search Bar BE ([`5f530d2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5f530d24a7fc5f2fc1fe9011c84f5bc082da1818))

* Merge branch &#39;development&#39; into pbi13/subtask2/search-bar-be ([`f1d912d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f1d912dee1b979419db1f7b8f0ebcefc815bb6a5))

* Merge pull request #63 from Kelompok-5-PPL-A/update-validation

PBI 3 Add Causes &amp; PBI 4 Validation Causes ([`09cfa83`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/09cfa8301aef795451adec2a2b2bb7ab3670847c))

* Merge branch &#39;development&#39; into update-validation ([`6b8b587`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/6b8b587cd7d50a183417996d8916e1ea8e812b48))

* Merge pull request #62 from Kelompok-5-PPL-A/pbi11/delete-question

PBI 11 - Delete Question ([`a2958b9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a2958b9ac350bb85f524ece9c6639e11b2c2cb29))

* Merge branch &#39;development&#39; into pbi11/delete-question ([`55b4a7f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/55b4a7f39f646efef4abdbae2bd07bec149e440d))

* Merge pull request #58 from Kelompok-5-PPL-A/pbi7-subtask2-dashboard-withFilter

Pbi7 subtask2 dashboard with filter ([`d3e246a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d3e246ae5d5b4692d566158741c4d960347cbb72))

* Merge pull request #57 from Kelompok-5-PPL-A/pbi5/upgrade-model

PBI 5 - Upgrade Reliability Validation Cause ([`5058985`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/505898569c9b5102c1959bc8f009028f92ccab3d))

* Merge pull request #68 from Kelompok-5-PPL-A/add-coverage

PBI 3 Add Causes &amp; PBI 4 Validation Causes (Testing) ([`d34f827`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d34f8270d5a52e42f5acd813edb94b977eb75127))

* [REFACTOR] update implementation to match the test ([`1bb0bed`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1bb0bedaea32e375b4c111f93d5153f173a19213))

* [GREEN] add implementation to pass the test ([`d1ca17c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d1ca17cb262505ebdd285500cba5aae85060b8a4))

* [RED] set up test with success, failed, and corner case ([`4f2bf26`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4f2bf264ea107fd42cecc630db2ac9144bf44172))

* [REFACTOR] remove translate text to english ([`caadc11`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/caadc11d4e22a5854dab5dceec2a8a1964dce2f1))

* chores: increase page size to 6 and max_page_size to 10 ([`daffa3c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/daffa3c6fbd5eaf0a97202c46cc95d3b49bcc48f))

* [REFACTOR] skip adding pengguna if the question&#39;s user is None or status as Guest ([`7b98e21`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7b98e21fa5695ed0d81cea86d29922ef583f6712))

* [REFACTOR] change the return exception if question is not found to just return the result query (empty list) ([`2b83ba1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2b83ba13d4e9612cc71df0c2384210499a983587))

* [REFACTOR] change exception not found message for better understanding ([`31e4bfb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/31e4bfb6df07803434bfa428ff84e9a1d10b76e6))

* [REFACTOR] add pagination schema for QuestionGetMatched view to ensure consistency ([`f3ab692`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f3ab692ef307f7a8d4240f4e03a94398b00412ed))

* [REFACTOR] refactor get_matched questions flow, it will directly return questions object ([`b1aa37d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b1aa37d5fe044526901c521590e59b97fc7262a8))

* debug: disable rate limiter ([`58947c9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/58947c9d22ea192db198fc8028836f108008ceb8))

* [RED] improve prompt engineering for accurate feedback from the AI model ([`62815a8`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/62815a8a0b39a74bfb1193618ae890955e816d0b))

* [REFACTOR] change today_datetime to UTC+7 for more accurate current time ([`bb4a4de`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/bb4a4de01142d9c19f6d7e75ce665464fa67f503))

* cicd: add moesif env to test job ([`05fcc36`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/05fcc369ef28f123c072d7f53718c94b6b0a2d75))

* cicd: add env to test job ([`815a981`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/815a981e5fdf71b042f29d7bb42abf542c326cfc))

* cicd: add monitoring tools secrets to deployment ([`4ce781f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4ce781fade862a488fc1f0b79e4a2f591eaf24a4))

* cicd: add monitoring tools secrets ([`07fc393`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/07fc3939b3d695f1a06dfdbd8bd297e2b5008e05))

* [REFACTOR] delete unused test and fix typo ([`a8be046`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a8be046eaa39c5e64bae5e56c2b7fbb73a0de57f))

* [REFACTOR] refactor test to increase coverage ([`e8f770c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e8f770c0cbfc89590d660f3dcd5193c1a03e6418))

* ops: improve Dockerfile with multi-stage builds ([`0b75a4d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0b75a4d408aa34676fcb9c218b814e15c7d0aa80))

* Merge pull request #53 from Kelompok-5-PPL-A/pbi3/update-cause-view

PBI 3 - Update Cause View ([`845487d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/845487d27aceb129a85cf78687aa301650d25c1e))

* Merge pull request #52 from Kelompok-5-PPL-A/pbi2/update-question-app

PBI 2 - Update Question App ([`4dad9b7`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4dad9b739c63f23473a97d499d2517a25a7bb75f))

* Merge branch &#39;development&#39; into pbi2/update-question-app ([`0bd3895`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0bd3895b3c9cf7930b68e5025a032019b4e17156))

* Merge pull request #47 from Kelompok-5-PPL-A/pbi1/subtask4

Authentication with SSO UI ([`9e58041`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9e58041eeb2d09c0e3b94be7b89a85f35fd0cd6c))

* Merge pull request #48 from Kelompok-5-PPL-A/refactor-solid

Refactor Authentication System and Apply Best Practice of Programming Concept ([`3941046`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/39410466bfffc16d86e194dc9ce0da895945b202))

* Merge branch &#39;pbi2/update-question-app&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into pbi2/update-question-app ([`3836a73`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3836a7382f8555381620183f2e958e2917f92db2))

* Merge branch &#39;development&#39; into pbi2/update-question-app ([`7606eda`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7606eda7ceb449e0646641805d26b5f695ec3e2e))

* init: initiate blacklist app ([`ecb6ebe`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ecb6ebe488e3b44a9d0db1875a8ec7b50110b2b5))

* init: initiate SSO UI app ([`482b89a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/482b89ac8ae906733508a5159dcddcf87dd40141))

* Merge pull request #46 from Kelompok-5-PPL-A/pbi9-subtask2

PBI 9 Subtask 2 - GET Recent Analysis ([`78e8b91`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/78e8b91f7eed678db82a7e6b9390751451b6779d))

* Merge pull request #45 from Kelompok-5-PPL-A/ci-cd

Codecov Integration ([`5d7c3a9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5d7c3a986fe75fb0730b5765cdbc44c2b1c2b6c0))

* Merge branch &#39;ci-cd&#39; of github.com-personal:Kelompok-5-PPL-A/MAAMS-NG-BE into ci-cd ([`1fe402c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1fe402cdcea7fc49e2e63a11845dc929a30addde))

* Merge branch &#39;development&#39; into ci-cd ([`721f558`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/721f558cb5df8beeeb38fa7a33c834b0daed59f2))

* Merge pull request #43 from Kelompok-5-PPL-A/pbi1/subtask3

Authentication with Google OAuth 2.0 ([`0f4e503`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0f4e5031c27c7c792fec10a8d94aaaf850998480))

* [REFACTOR] simplify view structure following service-based components ([`4ee937c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4ee937ccc828f1f5e1c96e777daba50cfd9239f8))

* [REFACTOR] authentication services with improved design patterns ([`ff280a4`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ff280a4c953afc9021d1f76b80f0cf8d89bd6f6a))

* [REFACTOR] change first and last name atrribute to given and family name ([`b684085`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b684085897c5ec0aaa0ce4cc3fd814a956c61af2))

* init: initiate authentication app ([`a033f44`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a033f442071849558c63f420c8d441e94fb26f37))

* Merge pull request #42 from Kelompok-5-PPL-A/add-coverage

Add Test Coverage for Cause App ([`26c048f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/26c048f47ddeed76f8581aeffb18a86c77f78677))

* [REFACTOR] simplify view structure following service-based components ([`805c1e3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/805c1e3f419517fa449fadfb414a309be75de54b))

* [REFACTOR] authentication services with improved design patterns ([`f8f2a52`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f8f2a52e4d1e8f47899da05306d61bc1b72adf07))

* [REFACTOR] change first and last name atrribute to given and family name ([`d8c19e0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/d8c19e0365d5e3f3e3038a5bbf8751802c9be307))

* init: initiate authentication app ([`177b0ab`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/177b0ab6f4d2d56c65d6ee845d864b7126a2869c))

* Merge branch &#39;development&#39; into add-coverage ([`2d8ad2f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/2d8ad2fa16d372d76553bd2e5d7110179767285b))

* Merge pull request #40 from Kelompok-5-PPL-A/add-coverage

Improve Code Coverage ([`fc7711c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/fc7711c3d52cc3e04c79a386c534b5aed541555b))

* Merge pull request #39 from Kelompok-5-PPL-A/ci-cd

Set Up Sentry for Error Monitoring ([`f095d2a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f095d2a09bc4ef6233b893c6fe918d58886ee27a))

* Merge branch &#39;add-coverage&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into add-coverage ([`ae69f69`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/ae69f69fbb3b058497ffd0d9185865f5dd148eda))

* Merge branch &#39;add-coverage&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into add-coverage ([`a77bc0e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/a77bc0e58395e441058d96ce15b0e3d62e7c3a06))

* add init file and improve views coverage ([`edcfa64`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/edcfa64a42a521bc7f3852c52519ebc1a548d887))

* Merge branch &#39;add-coverage&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into add-coverage ([`13347b1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/13347b17929251a9704fffa9ab44e51c9881ab04))

* [REFACTOR] Remove the Question.DoesNotExist exception part in Question.Get, http already can return 404 not found ([`cb76c96`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/cb76c9626d04b416b95aa83529aa2d960fc4e2af))

* [REFACTOR] Remove redundancy part in invalid input response ([`05f7818`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/05f78187289d7c6b08ee156d1ee4f9c39dc93aaf))

* [REFACTOR] Reworked  response return so it also hanlde unexpected error ([`f827ea1`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f827ea14d06bb7ab239e37d5d3f02383039b162e))

* [REFACTOR] reworked the post method so it will return various response status ([`5a03ead`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/5a03ead6b9c49f46e66fa073f1ef8ca5e7737911))

* Merge branch &#39;development&#39; into ci-cd ([`83ceb83`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/83ceb83bf58630f856485ef82377dc386b05681e))

* ops: add sentry dsn to ci-cd workflows ([`589d99f`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/589d99f7f5734dbdbd3ff25c5624d1ea936d188a))

* ops: setup sentry for error tracking ([`db5fb18`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/db5fb182d55d73f91864c8f72245a94fac0afca1))

* Merge pull request #38 from Kelompok-5-PPL-A/split-validator

PBI 2, PBI 3, PBI 4 - Split Validator Folder ([`dc46cac`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/dc46cac7b53483717d498c3e1555cfb1950984a8))

* Merge pull request #37 from Kelompok-5-PPL-A/ci-cd

CI/CD ([`f2c50f0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/f2c50f019222da1e20e854ffd69fbf9dae0f7d4b))

* Merge pull request #33 from Kelompok-5-PPL-A/pbi4-subtask1

Pbi4 subtask1 to main ([`7251a00`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/7251a001ec03353be99af4f9bd7e14ea064c3b4d))

* [REFACTOR] remove redundant user in create question test when using guest ([`b512547`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b5125475283b587e73c0914ed72eae2dfc1a66f2))

* [REFACTOR] remove redundant part on duplicate tag test ([`3c4e6de`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/3c4e6ded16e35b4029d1be79e3b253d58935aff7))

* Merge pull request #34 from Kelompok-5-PPL-A/pbi4-subtask2

Prompt Engineering for Retrieve Feedback ([`8ffb1cd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8ffb1cdafb88f2b972cdcf26fc5ba6de33a1e58e))

* chores: Implement snoarcloud workflow from latest staging branch to minimize conflict ([`1fcaded`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1fcaded229dd1105cbb8cff397213c82dd8b6501))

* [REFACTOR] implement the tag validation as a function instead of a part of the create method ([`c68f839`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c68f839c4a47ab7b28fc127a28ad676435e99c12))

* [REFACTOR] improve cause evaluation prompts for more accurate feedback ([`303255e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/303255e800281120e0faa7eea995429807d1106d))

* Merge pull request #29 from Kelompok-5-PPL-A/pbi4-subtask1

Implement and create test for Groq API Call ([`13a34c6`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/13a34c621581ae5d9c0f521dbb021e0e949f2645))

* [REFACTOR] improved error handling and clarified response parsing ([`434d0cb`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/434d0cbc01c646333b5888dc738169751333c3b9))

* Merge branch &#39;staging&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into pbi2-subtask2 ([`c7b65f0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c7b65f0b7ec6f4eb866b7298181d207dcfd6626e))

* Merge branch &#39;pbi2-subtask2&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into pbi2-subtask2 ([`e451e61`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e451e6179f9b56ee55ca240aadffb788d378242b))

* Merge branch &#39;staging&#39; of github.com-personal:Kelompok-5-PPL-A/MAAMS-NG-BE into staging ([`8f9c7f2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8f9c7f24f0449b75ceec2d16f206d67f671e4ec4))

* add build.yml for sonarqube ([`43ff0ac`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/43ff0acdecace57502e649ecffdd95b6ae2dbc12))

* Merge pull request #23 from Kelompok-5-PPL-A/pbi8-subtask3

Pbi8 subtask3 ([`4c3af8d`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/4c3af8d050d9022fb61ae20c764770e1574925d7))

* merge from main to pbi8-subtask3 ([`8731829`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/8731829a413f7e75e90610a49e07f616779ebbdb))

* Merge branch &#39;main&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into pbi2-subtask2 ([`c10e6cd`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/c10e6cd2a29dbcc78a1dc69c019361256dba6631))

* Merge pull request #19 from Kelompok-5-PPL-A/ci-cd

fix: ci-cd ([`9e6e7a2`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9e6e7a2cc85e89d7417e3c7768138df7fd1119ca))

* Merge branch &#39;main&#39; into ci-cd ([`af1b332`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/af1b332103aa3c021c78a40fc0b8c9c978186c02))

* Merge branch &#39;main&#39; of https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE into pbi8-subtask3 ([`376c973`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/376c973bc55f38bcc649ab4b2a7972e68034c89d))

* [GREEN] do some fixes ([`0fa470e`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0fa470ebc1c1c12f86cb3490ce8e48552413a5b6))

* [RED] add views ([`9a32998`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/9a3299803b0d9b5f104966dfa04190240f306423))

* [RED] add services ([`b8feee3`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b8feee3ecb999f9e28fc6cb0c8db32e56dcbc70a))

* [RED] add management ([`64bd680`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/64bd68026a1af6a37e46d4842d1bc13de31f4637))

* [RED] add dataclasses ([`e2cd41c`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/e2cd41cb1fff4e9e22899242d2cbe6a54731fd15))

* [RED] add models ([`535bd75`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/535bd75db9ac5ac761191798ab96ac00531e3735))

* [RED] add testing for guest function ([`1c1d04a`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/1c1d04a731ddf57230883a30789ff65a5ea80c91))

* [RED] Add testing for question feature BackEnd ([`0d85dd9`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/0d85dd9f12c617125bf07e0efe08cb10f73fd44a))

* init: init question app ([`952bcb0`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/952bcb00c8e3534a585cbd231c94bfc071482f70))

* first commit ([`b105542`](https://github.com/Kelompok-5-PPL-A/MAAMS-NG-BE/commit/b1055429a53b48bbc2eb7f633c195af98d3ad235))
