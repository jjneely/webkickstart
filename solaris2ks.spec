Summary: 
Name: solaris2ks
Version: 
Release: 1
URL: 
Source0: %{name}-%{version}.tar.gz
License: 
Group: 
BuildRoot: %{_tmppath}/%{name}-root
Requires: openssl

%description

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)


%changelog
* Thu Aug  8 2002 Jack Neely <slack@quackmaster.net>
- Initial build.


