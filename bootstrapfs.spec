%define name bootstrapfs
%define version 0.1
%define release 0%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.2
URL: http://svn.planet-lab.org/svn/BootStrapFS/

Summary: The PlanetLab Bootstrap Filesystems
Name: %{name}
Version: %{version}
Release: %{release}
License: BSD
Group: System Environment/Base
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: tar, gnupg, sharutils, bzip2

AutoReqProv: no
%define debug_package %{nil}

%description

The PlanetLab Bootstrap Filesystem(s) are downloaded by the
BootManager to instantiate a node with a new filesystem.

%prep
%setup -q

%build
pushd BootstrapFS
./build.sh %{pldistro}
popd BootstrapFS

%install
rm -rf $RPM_BUILD_ROOT

pushd BootstrapFS

install -D -m 644 PlanetLab-Bootstrap.tar.bz2 \
	$RPM_BUILD_ROOT/var/www/html/boot/PlanetLab-Bootstrap.tar.bz2

for bootstrapfs in $(ls ../build/config.%{pldistro}/bootstrap-*.pkgs) ; do 
    NAME=$(basename $pkgs .pkgs | sed -e s,bootstrapfs-,,)
    install -D -m 644 %{pldistro}-filesystems/PlanetLab-Bootstrap-${NAME}.tar.bz2 \
		$RPM_BUILD_ROOT/var/www/html/boot/PlanetLab-Bootstrap-${NAME}.tar.bz2
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
/var/www/html/boot/PlanetLab-Bootstrap*.tar.bz2

%changelog
* Fri Sep  2 2005 Mark Huang <mlhuang@cotton.CS.Princeton.EDU> - 
- Initial build.
