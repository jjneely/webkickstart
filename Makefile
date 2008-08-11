VERSION=3.0
NAME=webkickstart
TAG = $(VERSION)

.PHONY: archive clean

all:
	@echo "WebKickstart Makefile"
	@echo
	@echo "make clean 		-- Clean the source directory"
	@echo "make archive		-- Build a tar.bz2 ball for release"
	@echo "make srpm		-- Build a src.rpm for release"
	@echo

clean:
	rm -f `find . -name \*.pyc -o -name \*~`
	rm -f $(NAME)-*.tar.bz2

archive:
	git archive --prefix=$(NAME)-$(VERSION)/ \
		--format=tar master | bzip2 > $(NAME)-$(VERSION).tar.bz2
	@echo "The archive is in $(NAME)-$(VERSION).tar.bz2"

srpm: archive
	rpmbuild -ts $(NAME)-$(VERSION).tar.bz2

