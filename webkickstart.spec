%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           webkickstart
Version: 3.2.2
Release:        1%{?dist}
Summary:        Dynamically generate complex Red Hat Kickstarts.

Group:          System Environment/Daemons
License:        GPLv2+
URL:            https://secure.linux.ncsu.edu/moin/WebKickstart
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

Requires: python-abi = %(%{__python} -c "import sys ; print sys.version[:3]")
Requires: mod_python, python-cherrypy, python-genshi
Requires(post): httpd

%description
WebKickstart is an implementation to generate Kickstarts from a Cheetah
template based off a config file of 'keyword option option ...' lines for
each client.  Combined with file system sematics you can give different
groups access to different directories to keep configuration information
private while making use of a single template.

%prep
%setup -q


%build


%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
 
%clean
rm -rf $RPM_BUILD_ROOT

%post

# Log file fun...
if [ ! -e /var/log/webkickstart.log ] ; then
    touch /var/log/webkickstart.log
    chown apache:apache /var/log/webkickstart.log
fi

if [ ! -e /var/log/webkickstart-cherrypy.log ] ; then
    touch /var/log/webkickstart-cherrypy.log
    chown apache:apache /var/log/webkickstart-cherrypy.log
fi

%files
%defattr(-,root,root,-)
%doc README AUTHORS COPYING docs
%config(noreplace) %{_sysconfdir}/*
%{_datadir}/webKickstart
%{_bindir}/*
%{python_sitelib}/webKickstart


%changelog
* Thu Mar 26 2009 Jack Neely <jjneely@ncsu.edu> 3.1.0-1
- port all templating to genshi

* Tue Nov 18 2008 Jack Neely <jjneely@ncsu.edu> 
- Ditch python's distutils in favor of a working Makefile
- some tweaks to finish up the spec

* Mon Aug 11 2008 Jack Neely <jjneely@ncsu.edu> 3.0-1
- Initial packaging

