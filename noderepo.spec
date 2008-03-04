#
# $Id: bootstrapfs.spec 7668 2008-01-08 11:49:43Z thierry $
#
%define url $URL: svn+ssh://thierry@svn.planet-lab.org/svn/BootstrapFS/trunk/bootstrapfs.spec $

# build is expected to export the following rpm variables
# %{distroname}     : e.g. Fedora
# %{distrorelease}  : e.g. 8
# %{node_rpms_plus} : as a +++ separated list of rpms from the build dir

%define name noderepo-%{distroname}-%{_arch}
%define version 4.2
%define taglevel 1

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

Summary: The initial content of the yum repository for nodes
Name: %{name}
Version: %{version}
Release: %{release}
License: BSD
Group: System Environment/Base
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: rsync createrepo

%define debug_package %{nil}

%description
This rpm contains all the rpms designed for running on a PlanetLab node
they come organized into a yum repository 

%prep
%setup -q

%build
echo nothing to do at build time for noderepo

%install
rm -rf $RPM_BUILD_ROOT

pushd BootstrapFS
repo=planetlab-%{distroname}-%{_arch}
install -d -m 755 $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo
rpms=$(echo %{node_rpms_plus} | sed -e s,+++, ,g)
for rpm in $rpms; do rsync $RPM_BUILD_ROOT/$rpm $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo/ ; done
### yumgroups
install -D -m 644 $RPM_BUILD_ROOT/RPMS/yumgroups.xml $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo
createrepo -g yumgroups.xml $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo
popd

%clean
rm -rf $RPM_BUILD_ROOT

%post


%files
%defattr(-,root,root,-)
/var/www/html/install-rpms/planetlab-%{distroname}-%{_arch}

%changelog
* Tue Mar 4 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> -
- Initial build.
