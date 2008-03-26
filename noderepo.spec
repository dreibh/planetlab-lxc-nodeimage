#
# $Id: bootstrapfs.spec 7668 2008-01-08 11:49:43Z thierry $
#
%define url $URL: svn+ssh://thierry@svn.planet-lab.org/svn/BootstrapFS/trunk/bootstrapfs.spec $

# build is expected to export the following rpm variables
# %{distroname}     : e.g. Fedora
# %{distrorelease}  : e.g. 8
# %{node_rpms_plus} : as a +++ separated list of rpms from the build dir

%define nodefamily %{pldistro}-%{_arch}

%define name noderepo-%{nodefamily}
%define version 1.0
%define taglevel 0

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
# other archs must be able to install this
BuildArch: noarch

BuildRequires: rsync 
Requires: myplc

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

repo=%{nodefamily}
install -d -m 755 $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo
rpms=$(echo %{node_rpms_plus} | sed -e 's,+++, ,g')
for rpm in $rpms; do rsync %{_topdir}/$rpm $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo/ ; done
### yumgroups
install -D -m 644 %{_topdir}/RPMS/yumgroups.xml $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo/yumgroups.xml
# do not do this yet, as plc.d/packages will do it anyway
#createrepo -g yumgroups.xml $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo

%clean
rm -rf $RPM_BUILD_ROOT

%post
service plc start packages

%files
%defattr(-,root,root,-)
/var/www/html/install-rpms/%{nodefamily}

%changelog
* Wed Mar 26 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-0.1-2 BootstrapFS-1.0-0
- naming scheme changed, tarball name now contains ''nodefamily'' as <pldistro>-<arch>
- new package named 'noderepo' allows to ship the full set of node rpms to another (arch) myplc

* Tue Mar 4 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> -
- Initial build.
