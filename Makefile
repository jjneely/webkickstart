VERSION=3.0
NAME=webkickstart
TAG = $(VERSION)

.PHONY: archive clean

all:
	@echo "Nothing to build"

clean:
	rm -f `find . -name \*.pyc -o -name \*~`

archive:
	git archive --prefix=$(NAME)-$(VERSION)/ \
		--format=tar master | bzip2 > $(NAME)-$(VERSION).tar.bz2
	@echo "The archive is in $(NAME)-$(VERSION).tar.bz2"

