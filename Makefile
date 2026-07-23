.RECIPEPREFIX := >
PYTHON ?= python3

.PHONY: check doctor test compile

check: doctor test

doctor:
>./scripts/doctor.sh

test:
>./scripts/test.sh

compile:
>$(PYTHON) -m compileall -q checks scripts tests
