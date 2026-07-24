.RECIPEPREFIX := >
PYTHON ?= python3

.PHONY: help status catalog check doctor test compile

help:
>@printf '%s\n' \
>  'Engineering Standards commands:' \
>  '  make status   Show repository health' \
>  '  make catalog  Print the machine-readable repository index' \
>  '  make doctor   Run policy and repository checks' \
>  '  make test     Run unit tests' \
>  '  make compile  Compile Python sources' \
>  '  make check    Run all required verification'

status:
>$(PYTHON) scripts/standards.py status

catalog:
>$(PYTHON) scripts/standards.py catalog --json

check:
>$(PYTHON) scripts/standards.py check

doctor:
>$(PYTHON) scripts/standards.py doctor

test:
>$(PYTHON) scripts/standards.py test

compile:
>$(PYTHON) -m compileall -q checks scripts tests
