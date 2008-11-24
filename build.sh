#!/bin/bash
#
# Build bootstrapfs-*.tar.bz2, the reference image(s) for PlanetLab nodes.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Marc E. Fiuczynski <mef@cs.princeton.edu>
# Copyright (C) 2005-2007 The Trustees of Princeton University
#
# $Id: buildnode.sh,v 1.12.6.1 2007/08/30 20:09:20 mef Exp $
#

#
# This will build the bootstrafs-*.tar.bz2 images, which comprises
# the base root image on the node, then create the ${NAME} bootstrap image
# which is made up of just the additional files needed for a ${NAME} nodegroup 
# node.
#

PATH=/sbin:/bin:/usr/sbin:/usr/bin

# in the PlanetLab build environment, our dependencies are checked out 
# into directories at the same level as us.
if [ -d ../build ] ; then
    PATH=$PATH:../build
    srcdir=../
else
    echo "Error: Could not find ../build in $(pwd)"
    exit 1
fi

export PATH

. build.common

pl_process_fedora_options $@
shiftcount=$?
shift $shiftcount

# expecting fcdistro and pldistro on the command line
pldistro=$1; shift
fcdistro=${pl_DISTRO_NAME}

# Do not tolerate errors
set -e

# Some of the PlanetLab RPMs attempt to (re)start themselves in %post,
# unless the installation is running inside the BootCD environment. We
# would like to pretend that we are.
export PL_BOOTCD=1

# Populate a minimal /dev and then the files for the base bootstrapfs content
vref=${PWD}/base
install -d -m 755 ${vref}
pl_root_makedevs $vref

pkgsfile=$(pl_locateDistroFile ../build/ ${pldistro} bootstrapfs.pkgs)
echo "* Building Bootstrapfs for ${pldistro}: $(date)"
# -k = exclude kernel* packages
pl_root_mkfedora ${vref} ${pldistro} $pkgsfile

# optionally invoke a post processing script after packages from
# $pkgsfile have been installed
pkgsdir=$(dirname $pkgsfile)
pkgsname=$(basename $pkgsfile .pkgs)
postfile="${pkgsdir}/${pkgsname}.post"
[ -f $postfile ] && /bin/bash $postfile ${vref} || :

displayed=""

# for distros that do not define bootstrapfs variants
pkgs_count=$(ls ../build/config.${pldistro}/bootstrapfs-*.pkgs 2> /dev/null | wc -l)
[ $pkgs_count -gt 0 ] && for pkgs in $(ls ../build/config.${pldistro}/bootstrapfs-*.pkgs); do
    NAME=$(basename $pkgs .pkgs | sed -e s,bootstrapfs-,,)

    [ -z "$displayed" ] && echo "* Handling ${plistro} bootstrapfs extensions"
    displayed=true

    extension_plain=bootstrapfs-${NAME}-${pl_DISTRO_ARCH}.tar
    extension_name=bootstrapfs-${NAME}-${pl_DISTRO_ARCH}.tar.bz2

    echo "* Start Building $extension_name: $(date)"

    # "Parse" out the packages and groups for yum
    packages=$(pl_getPackages $fcdistro $pldistro $pkgs)
    groups=$(pl_getGroups $fcdistro $pldistro $pkgs)
    echo "${NAME} has the following packages : ${packages}"
    echo "${NAME} has the following groups : ${groups}"

    vdir=${PWD}/${pldistro}-filesystems/${NAME}
    rm -rf ${vdir}/*
    install -d -m 755 ${vdir}

    # Clone the base reference to the bootstrap fs
    (cd ${vref} && find . | cpio -m -d -u -p ${vdir})
    rm -f ${vdir}/var/lib/rpm/__db*

    # Install the system vserver specific packages
    [ -n "$packages" ] && yum -c ${vdir}/etc/mkfedora-yum.conf --installroot=${vdir} -y install $packages
    [ -n "$groups" ] && yum -c ${vdir}/etc/mkfedora-yum.conf --installroot=${vdir} -y groupinstall $groups

    if [ -f "${vdir}/proc/cpuinfo" ] ; then
        echo "WARNING: some RPM appears to have mounted /proc in ${NAME}. Unmounting it!"
        umount ${vdir}/proc
    fi

    # optionally invoke a post processing script after packages from
    # $pkgs have been installed
    pkgsdir=$(dirname $pkgs)
    pkgsname=$(basename $pkgs .pkgs)
    postfile="${pkgsdir}/${pkgsname}.post"
    [ -f $postfile ] && /bin/bash $postfile ${vdir} || :


    # Create a copy of the ${NAME} bootstrap filesystem w/o the base
    # bootstrap filesystem and make it smaller.  This is a three step
    # process:

    # step 1: clean out yum cache to reduce space requirements
    yum -c ${vdir}/etc/mkfedora-yum.conf --installroot=${vdir} -y clean all

    # step 2: figure out the new/changed files in ${vdir} vs. ${vref} and compute ${vdir}.changes
    rsync -anv ${vdir}/ ${vref}/ > ${vdir}.changes
    linecount=$(wc -l ${vdir}.changes | awk ' { print $1 } ')
    let headcount=$linecount-3
    let tailcount=$headcount-1
    # get rid of the last 3 lines of the rsync output
    head -${headcount} ${vdir}.changes > ${vdir}.changes.1
    # get rid of the first line of the rsync output
    tail -${tailcount} ${vdir}.changes.1 > ${vdir}.changes.2
    # post process rsync output to get rid of symbolic link embellish output
    awk ' { print $1 } ' ${vdir}.changes.2 > ${vdir}.changes
    rm -f ${vdir}.changes.*

    # step 3: create the ${vdir} with just the list given in ${vdir}.changes 
    install -d -m 755 ${vdir}-tmp/
    rm -rf ${vdir}-tmp/*
    (cd ${vdir} && cpio -m -d -u -p ${vdir}-tmp < ${vdir}.changes)
    rm -rf ${vdir}
    rm -f  ${vdir}.changes
    mv ${vdir}-tmp ${vdir}
    
    echo -n "* tar $extension_name s=$(date +%H-%M-%S)"
    tar -cpf ${pldistro}-filesystems/$extension_plain -C ${vdir} .
    echo -n " m=$(date +%H-%M-%S) "
    bzip2 --compress --stdout $extension_plain > $extension_name
    echo " e=$(date +%H-%M-%S) "
done

# Build the base Bootstrap filesystem
# clean out yum cache to reduce space requirements
yum -c ${vref}/etc/mkfedora-yum.conf --installroot=${vref} -y clean all

bootstrapfs_plain=bootstrapfs-${pldistro}-${pl_DISTRO_ARCH}.tar
bootstrapfs_name=bootstrapfs-${pldistro}-${pl_DISTRO_ARCH}.tar.bz2
echo -n "* tar $bootstrapfs_name s=$(date +%H-%M-%S)"
tar -cpf $bootstrapfs_plain -C ${vref} .
echo -n " m=$(date +%H-%M-%S) "
bzip2 --compress --stdout $bootstrapfs_plain > $bootstrapfs_name
echo " e=$(date +%H-%M-%S) "

exit 0
