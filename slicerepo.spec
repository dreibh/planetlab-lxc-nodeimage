#
# $Id$
#
%define url $URL$

# build is expected to export the following rpm variables
# %{distroname}     : e.g. Fedora
# %{distrorelease}  : e.g. 8
# %{slice_rpms_plus} : as a +++ separated list of rpms from the build dir

%define nodefamily %{pldistro}-%{distroname}-%{_arch}
%define obsolete_nodefamily %{pldistro}-%{_arch}

%define name slicerepo-%{nodefamily}
%define version 2.0
%define taglevel 0

# pldistro already in the rpm name
#%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}
%define release %{taglevel}%{?date:.%{date}}

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

# 5.0 now has 3-fold nodefamily
%define obsolete_nodefamily %{pldistro}-%{_arch}
Obsoletes: slicerepo-%{obsolete_nodefamily}

%define debug_package %{nil}

%description
This rpm contains all the rpms designed for running on a PlanetLab node
they come organized into a yum repository 

%prep
%setup -q

%build
echo nothing to do at build time for slicerepo

%install
rm -rf $RPM_BUILD_ROOT

repo=slice-%{nodefamily}
install -d -m 755 $RPM_BUILD_ROOT/var/www/html/install-rpms/$repo
rpms=$(echo %{slice_rpms_plus} | sed -e 's,+++, ,g')
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
/var/www/html/install-rpms/slice-%{nodefamily}
# don't overwrite yumgroups.xml if exists
%config(noreplace) /var/www/html/install-rpms/slice-%{nodefamily}/yumgroups.xml

%changelog
