# ⠋ Ranko ⣠ [![Build Status](https://img.shields.io/travis/cloverfeed/ranko.svg)](http://travis-ci.org/cloverfeed/ranko) [![Coverage Status](https://img.shields.io/coveralls/cloverfeed/ranko.svg)](https://coveralls.io/r/cloverfeed/ranko) [![Dependency Status](https://img.shields.io/gemnasium/cloverfeed/ranko.svg)](https://gemnasium.com/cloverfeed/ranko)

![Ranko](https://i.imgur.com/QxAyIvW.jpg)

A tool to upload and review documents.

## How to code

Master is always deployable (github-flow).
Make a branch! Don't directly commit to master.

## How to test

Unit tests:

    nosetests --with-coverage --cover-package=app

Coverage is nice but not absolute. A metric that becomes an objective is not a
metric anymore.

UI tests are ran with:

    casperjs test tests.coffee

Linters are available but not enforced: pep8, coffeelint.

## How to deploy

  - ensure that unit tests are OK.
  - deploy master to a vagrant VM (`vagrant up` + `scripts/deploy --to=test` should do this).
  - test upgrade using `scripts/deploy --to=test --branch=YOURBRANCH`.
  - If everything is fine, merge the branch (no FF):
    - `git checkout master`
    - `git merge --no-ff YOURBRANCH`
    - `git push origin master :YOURBRANCH`
    - `git branch -d YOURBRANCH`
  - Deploy master to prod: `scripts/deploy`.
