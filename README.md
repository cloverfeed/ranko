# ⠋ Ranko ⣠ [![Build Status](https://secure.travis-ci.org/cloverfeed/ranko.png)](http://travis-ci.org/cloverfeed/ranko) [![Coverage Status](https://coveralls.io/repos/cloverfeed/ranko/badge.png)](https://coveralls.io/r/cloverfeed/ranko) [![Dependency Status](https://gemnasium.com/cloverfeed/ranko.svg)](https://gemnasium.com/cloverfeed/ranko)

![Ranko](http://us.tintin.com/wp-content/uploads/2011/09/characters-ranko-the-gorilla-sm.jpg)

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
