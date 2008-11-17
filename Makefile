VERSION=3.0
NAME=webkickstart
SPEC=webkickstart.spec

.PHONY: archive clean

all:
	@echo "WebKickstart Makefile"
	@echo
	@echo "make clean 		-- Clean the source directory"
	@echo "make archive		-- Build a tar.bz2 ball for release"
	@echo "make srpm		-- Build a src.rpm for release"
	@echo

srpm: archive
	rpmbuild -ts $(NAME)-$(VERSION).tar.bz2

clean:
	rm -f `find . -name \*.pyc -o -name \*~`
	rm -f $(NAME)-*.tar.bz2

release: archive
	git tag -f -a -m "Tag $(VERSION)" $(VERSION)

archive:
	if ! grep "Version: $(VERSION)" $(SPEC) > /dev/null ; then \
		sed -i '/^Version: $(VERSION)/q; s/^Version:.*$$/Version: $(VERSION)/' $(SPEC) ; \
		git add $(SPEC) ; git commit -m "Bumb version tag to $(VERSION)" ; \
	fi
	git archive --prefix=$(NAME)-$(VERSION)/ \
		--format=tar HEAD | bzip2 > $(NAME)-$(VERSION).tar.bz2
	@echo "The archive is in $(NAME)-$(VERSION).tar.bz2"

