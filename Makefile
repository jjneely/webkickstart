VERSION=3.1.2
NAME=webkickstart
SPEC=webkickstart.spec

ifndef PYTHON
PYTHON=/usr/bin/python
endif
SITELIB=`$(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`

.PHONY: archive clean

all:
	@echo "WebKickstart Makefile"
	@echo
	@echo "make clean 		-- Clean the source directory"
	@echo "make archive		-- Build a tar.bz2 ball for release"
	@echo "make srpm		-- Build a src.rpm for release"
	@echo "make install     -- Do useful things - define a DESTDIR"
	@echo

install:
	install -d -m 755 $(DESTDIR)/usr/share/webKickstart
	install -d -m 755 $(DESTDIR)$(SITELIB)/webKickstart
	install -d -m 755 $(DESTDIR)$(SITELIB)/webKickstart/webtmpl
	install -d -m 755 $(DESTDIR)$(SITELIB)/webKickstart/static/css
	install -d -m 755 $(DESTDIR)$(SITELIB)/webKickstart/plugins
	install -d -m 755 $(DESTDIR)/etc/webkickstart/hosts
	install -d -m 755 $(DESTDIR)/etc/webkickstart/pluginconf.d
	install -d -m 755 $(DESTDIR)/etc/webkickstart/profiles
	install -d -m 755 $(DESTDIR)/usr/bin
	
	install -m 644 webKickstart/webtmpl/*.xml $(DESTDIR)$(SITELIB)/webKickstart/webtmpl/
	install -m 644 webKickstart/static/css/*.css $(DESTDIR)$(SITELIB)/webKickstart/static/css/
	install -m 644 webKickstart/static/*.gif webKickstart/static/*.png $(DESTDIR)$(SITELIB)/webKickstart/static/
	install -m 644 webKickstart/plugins/*.py $(DESTDIR)$(SITELIB)/webKickstart/plugins/
	install -m 644 webKickstart/*.py $(DESTDIR)$(SITELIB)/webKickstart/
	
	install -m 755 scripts/makekickstart.py $(DESTDIR)/usr/share/webKickstart
	install -m 755 scripts/simplewebkickstart.py $(DESTDIR)/usr/share/webKickstart
	ln -s /usr/share/webKickstart/makekickstart.py $(DESTDIR)/usr/bin/makekickstart
	ln -s /usr/share/webKickstart/simplewebkickstart.py $(DESTDIR)/usr/bin/simplewebkickstart
	
	install -m 644 etc/webkickstart.conf $(DESTDIR)/etc/webkickstart/
	install -m 644 etc/profiles/*.tmpl $(DESTDIR)/etc/webkickstart/profiles/
	install -m 644 etc/pluginconf.d/*.example $(DESTDIR)/etc/webkickstart/pluginconf.d/

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

