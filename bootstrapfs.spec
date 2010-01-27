#
# $Id$
#
%define url $URL$

%define nodefamily %{pldistro}-%{distroname}-%{_arch}
%define extensionfamily %{distroname}-%{_arch}

%define name bootstrapfs-%{nodefamily}
%define version 2.0
%define taglevel 0

# pldistro already in the rpm name
#%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}
%define release %{taglevel}%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

Summary: The PlanetLab Bootstrap Filesystems for %{nodefamily}
Name: %{name}
Version: %{version}
Release: %{release}
License: BSD
Group: System Environment/Base
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
# other archs must be able to install this
BuildArch: noarch

Requires: tar, gnupg, sharutils, bzip2

# 5.0 now has 3-fold nodefamily
%define obsolete_nodefamily %{pldistro}-%{_arch}
Obsoletes: bootstrapfs-%{obsolete_nodefamily}

AutoReqProv: no
%define debug_package %{nil}

%description

The PlanetLab Bootstrap Filesystem(s) are downloaded by the
BootManager to instantiate a node with a new filesystem.

%package plain
Summary: The (uncompressed) PlanetLab Bootstrap Filesystems for %{nodefamily}
Group: System Environment/Base
%description plain
This package provides the same functions as %{name} but with uncompressed tarball for faster tests.

%package -n nodeyum
Summary: the MyPLC-side utilities for tweaking nodes yum configs
Group: System Environment/Base
%description -n nodeyum 
Utility scripts for configuring node updates. This package is designed
for the MyPLC side.
# need the apache user at install-time
Requires: httpd 

%prep
%setup -q

%build
pushd BootstrapFS
./build.sh %{pldistro} 
popd

# xxx in a multi-flavour myplc, we should ship for all fcdistros
# and let the php scripts do the right thing

pushd BootstrapFS/nodeconfig/yum
# scan fcdistros and catenate all repos in 'stock.repo' so db-config can be distro-independant
for fcdistro in $(ls); do
    [ -d $fcdistro ] || continue
    # get kexcludes for that distro
    KEXCLUDE="exclude=$(../../../build/getkexcludes.sh -f $fcdistro)"
    pushd $fcdistro/yum.myplc.d
    echo "* Handling KEXCLUDE in yum repo for $fcdistro ($KEXCLUDE)"
    for filein in $(find . -name '*.in') ; do
	file=$(echo $filein | sed -e "s,\.in$,,")
	sed -e "s,@KEXCLUDE@,$KEXCLUDE,g" $filein > $file
    done
    rm -f stock.repo
    cat *.repo > stock.repo
    popd
done
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd BootstrapFS
#arch=$(uname -i)

install -D -m 644 bootstrapfs-%{nodefamily}.tar.bz2 \
	$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-%{nodefamily}.tar.bz2
install -D -m 644 bootstrapfs-%{nodefamily}.tar \
	$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-%{nodefamily}.tar

for pkgs in $(ls ../build/config.%{pldistro}/bootstrapfs-*.pkgs) ; do 
    NAME=$(basename $pkgs .pkgs | sed -e s,bootstrapfs-,,)
    install -D -m 644 %{pldistro}-filesystems/bootstrapfs-${NAME}-%{extensionfamily}.tar.bz2 \
		$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-${NAME}-%{extensionfamily}.tar.bz2 
    install -D -m 644 %{pldistro}-filesystems/bootstrapfs-${NAME}-%{extensionfamily}.tar \
		$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-${NAME}-%{extensionfamily}.tar 
done
popd

pushd BootstrapFS/nodeconfig
echo "* Installing MyPLC-side yum stuff"
# expose (fixed) myplc.repo.php as				            https://<plc>/yum/myplc.repo.php
install -D -m 644 ./yum/myplc.repo.php			     $RPM_BUILD_ROOT/var/www/html/yum/myplc.repo.php
# expose the fcdistro-dependant yum.conf as				    https://<plc>/yum/yum.conf
install -D -m 644 ./yum/%{distroname}/yum.conf		     $RPM_BUILD_ROOT/var/www/html/yum/yum.conf
# expose the (fcdistro-dependant) stock.repo as				    https://<plc>/yum/stock.repo
install -D -m 644 ./yum/%{distroname}/yum.myplc.d/stock.repo $RPM_BUILD_ROOT/var/www/html/yum/stock.repo
popd

pushd BootstrapFS
echo "* Installing db-config.d files"
mkdir -p ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
cp db-config.d/* ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
chmod 444 ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d/*
popd

%clean
rm -rf $RPM_BUILD_ROOT

%post -n nodeyum
# the boot manager upload area
mkdir -p /var/log/bm
chown apache:apache /var/log/bm
chmod 700 /var/log/bm


%files
%defattr(-,root,root,-)
/var/www/html/boot/bootstrapfs*.tar.bz2

%files plain
%defattr(-,root,root,-)
/var/www/html/boot/bootstrapfs*.tar

%files -n nodeyum
%defattr(-,root,root,-)
/var/www/html/yum
/etc/planetlab/db-config.d

%changelog
* Mon Jan 04 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-11
- for building on fedora12

* Thu Oct 22 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-10
- cosmetic change in message at build-time

* Fri Oct 09 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-9
- can use groups in the pkgs file with +++ for space

* Tue Apr 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-8
- bugfix for when a .post script is not needed

* Tue Apr 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-7
- search post-install scripts (.post) in path (distro, then planetlab)
- mostly useful for externally-defined pldistros

* Thu Jan 08 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-6
- fix build bug when dealing with extensions

* Thu Dec 04 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-5
- optional package bootstrapfs-<pldiftr>-<arch>-plain comes with uncompressed images for faster tests

* Fri Nov 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-4
- cosmetic changes in build: displays duration, and shows up in summary

* Mon Sep 01 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-3
- Do not overwrite yumgroups.xml upon updates of noderepo

* Thu Jul 03 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-2
- uses the right yum.conf when building images

* Mon May 05 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-1.0-1
- rpm release tag does not need pldistro as it is already part of the rpm name

* Wed Mar 26 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-0.1-2 BootstrapFS-1.0-0
- naming scheme changed, tarball name now contains ''nodefamily'' as <pldistro>-<arch>
- new package named 'noderepo' allows to ship the full set of node rpms to another (arch) myplc

* Fri Jan 18 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-0.1-1 bootstrapfs-0.1-2
- search more carefully for alternate pkgs files
- handling of sysconfig/crontab and creation of site_admin reviewed
- (this tag is set with module-tag.py)

* Fri Sep  2 2005 Mark Huang <mlhuang@cotton.CS.Princeton.EDU> - 
- Initial build.

%define module_current_branch 1.0
