#
# $Id$
#
%define url $URL$

%define nodefamily %{pldistro}-%{_arch}

%define name bootstrapfs-%{nodefamily}
%define version 1.0
%define taglevel 7

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

%prep
%setup -q

%build
pushd BootstrapFS
./build.sh %{pldistro} 
popd BootstrapFS

%install
rm -rf $RPM_BUILD_ROOT

pushd BootstrapFS
arch=$(uname -i)

install -D -m 644 bootstrapfs-%{pldistro}-${arch}.tar.bz2 \
	$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-%{pldistro}-${arch}.tar.bz2
install -D -m 644 bootstrapfs-%{pldistro}-${arch}.tar \
	$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-%{pldistro}-${arch}.tar

for pkgs in $(ls ../build/config.%{pldistro}/bootstrapfs-*.pkgs) ; do 
    NAME=$(basename $pkgs .pkgs | sed -e s,bootstrapfs-,,)
    install -D -m 644 %{pldistro}-filesystems/bootstrapfs-${NAME}-${arch}.tar.bz2 \
		$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-${NAME}-${arch}.tar.bz2 
    install -D -m 644 %{pldistro}-filesystems/bootstrapfs-${NAME}-${arch}.tar \
		$RPM_BUILD_ROOT/var/www/html/boot/bootstrapfs-${NAME}-${arch}.tar 
done

popd

%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo
if [ -n "$SUDO_USER" ] ; then
    # Allow user to delete the build directory
    chown -h -R $SUDO_USER .
    # Some temporary cdroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
    # Allow user to delete the built RPM(s)
    chown -h -R $SUDO_USER %{_rpmdir}/%{_arch}
fi

%post

%files
%defattr(-,root,root,-)
/var/www/html/boot/bootstrapfs*.tar.bz2

%files plain
%defattr(-,root,root,-)
/var/www/html/boot/bootstrapfs*.tar

%changelog
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
