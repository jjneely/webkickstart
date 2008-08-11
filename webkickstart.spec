%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           webkickstart
Version:        3.0
Release:        1%{?dist}
Summary:        Dynamically generate complex Red Hat Kickstarts.

Group:          System Environment/Daemons
License:        GPL
URL:            https://secure.linux.ncsu.edu/moin/WebKickstart
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel

Requires: python-abi = %(%{__python} -c "import sys ; print sys.version[:3]")
Requires: mod_python, python-cherrypy, python-kid, python-cheetah

%description
WebKickstart is an implementation to generate Kickstarts from a Cheetah
template based off a config file of 'keyword option option ...' lines for
each client.  Combined with file system sematics you can give different
groups access to different directories to keep configuration information
private while making use of a single template.

%prep
%setup -q


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%dir /etc/webkickstart

%{_bindir}/*
%{python_sitelib}/webKickstart/*

%config(noreplace) /etc/webkickstart/*

%changelog
* Wed Jul 09 2008 Jack Neely <jjneely@ncsu.edu> 3.0-1
- Initial packaging

