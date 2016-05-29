.PHONY: external

SHELL=bash -e
STATIC_DIR=showdocs/static

tests:
	nosetests tests/
	cram --shell /bin/bash tests/

clean:
	rm -r externaltmp/ || true
	find showdocs tests external -name '*.py[cdo]' -exec rm -f '{}' ';'

.PHONY: clean externalcss tests
