# build is expected to export the following rpm variables
# %{distroname}     : e.g. Fedora
# %{distrorelease}  : e.g. 8
# %{node_rpms_plus} : as a +++ separated list of rpms from the build dir

%define nodefamily %{pldistro}-%{distroname}-%{_arch}
%define obsolete_nodefamily %{pldistro}-%{_arch}

%define name noderepo-%{nodefamily}
%define version 5.2
%define taglevel 7

# pldistro already in the rpm name
#%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}
%define release %{taglevel}%{?date:.%{date}}

# we don't really need the standard postinstall process from rpm that
# strips files and byte-compiles python files. all files in this
# package are comming from other rpm files and they've already went
# through this post install processing. - baris
%define __os_install_post %{nil}

Vendor: OneLab
Packager: PlanetLab Europe <build@onelab.eu>
Distribution: PlanetLab %{plrelease}
URL: %{SCMURL}

Summary: The yum repository for nodes, to be installed on the myplc-side
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
Obsoletes: noderepo-%{obsolete_nodefamily}

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
# it would at first glance seem to make sense to invoke service plc start gpg here as well, 
# as noderepo might get installed before myplc gets even started 
# this however exhibit a deadlock, as rpm --almatches -e gpg-pubkey waits for transaction lock
# that is help by the calling yum/rpm
if [ ! -e /bin/systemctl ] ; then
   echo "Systemd is not there. Just starting PLC to handle packages (may fail if PLC is not configured) ..."
   service plc start packages
elif /bin/systemctl status plc >/dev/null ; then
   echo "Restarting PLC to handle packages ..."
   service plc restart packages
else
   echo "PLC is not running. Skipping a restart ..."
fi

%files
%defattr(-,root,root,-)
/var/www/html/install-rpms/%{nodefamily}
# don't overwrite yumgroups.xml if exists
%config(noreplace) /var/www/html/install-rpms/%{nodefamily}/yumgroups.xml

%changelog
* Sun Jul 10 2016 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-7
- yum config ; deprecates old fedora releases, add support for f23/f24

* Fri Nov 13 2015 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-6
- fix for f22 and dnf.conf

* Fri Jun 26 2015 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-5
- the yum config for nodes on f21 and f22
- define a new config_file for /etc/dnf/dnf.conf so that /etc/yum.myplc.d
- is taken into account on f22

* Wed Feb 18 2015 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-4
- minor change; start plc packages only at run-time, not build-time
- only available on systems that have systemctl

* Tue Jul 22 2014 Thomas Dreibholz <dreibh@simula.no> - nodeimage-5.2-4
- Post-install fix: trying to start PLC only when it is running, in order to avoid false-positive error message during build.

* Fri Mar 21 2014 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-3
- template for f20 yum config

* Sun Jul 14 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-2
- more timestamps during build

* Thu Mar 07 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-5.2-1
- add support for f18 yum config

* Mon Feb 11 2013 Stephen Soltesz <soltesz@opentechinstitute.org> - nodeimage-2.1-4

* Mon Nov 26 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-2.1-3
- fix /etc/plc.d/packages for empty install dirs

* Fri Sep 28 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-2.1-2
- exclude slice repos when running plc.d/packages start

* Fri Apr 13 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - nodeimage-2.1-1
- renamed as nodeimage - works on both mainline and lxc

* Thu Feb 16 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-14
- changes needed for build with yumexcludes defined in a separate pkgs file

* Wed Aug 31 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-13
- plc.d/packages: rewrote comments about some corner cases where it fails
- plc.d/packages: marginally more robust

* Fri Jun 10 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-12
- minor tweak in plc.d/packages

* Mon Jun 06 2011 Baris Metin <bmetin@verivue.com> - bootstrapfs-2.0-11
- sl6 templates

* Thu Feb 17 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-10
- bugfix for multi-flavour deployments

* Fri Feb 04 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-9
- for multi-flavours : 'packages' step in plc.d now handles vserver links and related hacks in yumgroups

* Thu Jan 27 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-8
- no semantic change - attempt to speed up build

* Sun Jan 23 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - bootstrapfs-2.0-7
- yum repo template for f14 nodes
- tweaks the way /etc/plc.d/packages works

* Mon Jul 05 2010 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - BootstrapFS-2.0-6
- add sha1sum
- module name changes

* Tue Apr 27 2010 Talip Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - BootstrapFS-2.0-5
- support different flavours of vservers on nodes

* Mon Apr 12 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-2.0-4
- fix unmatched $ in URL svn keywords

* Fri Apr 02 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-2.0-3
- choice between various pldistros is not made at build time, but at run time
- relies on GetNodeFlavour to expose the node's fcdistro - requires PLCAPI-5.0-5
- in addition, the baseurl for the myplc repo is http:// and not https:// anymore
- the https method does not work on fedora 12, and GPG is used below anyway

* Fri Mar 12 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-2.0-2
- new slicerepo package for exposing stuff to slivers

* Fri Jan 29 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - BootstrapFS-2.0-1
- first working version of 5.0:
- pld.c/, db-config.d/ and nodeconfig/ scripts should now sit in the module they belong to
- nodefailiy is 3-fold with pldistro-fcdistro-arch
- new module nodeyum; first draft has the php scripts and conf_files for tweaking nodes yum config

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

* Tue Mar 4 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> -
- Initial build.

%define module_current_branch 1.0
