#!/bin/bash
#
# Build PlanetLab-Bootstrap.tar.bz2, the reference image for PlanetLab
# nodes.
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Marc E. Fiuczynski <mef@cs.princeton.edu>
# Copyright (C) 2005-2007 The Trustees of Princeton University
#
# $Id: buildnode.sh,v 1.12.6.1 2007/08/30 20:09:20 mef Exp $
#

PATH=/sbin:/bin:/usr/sbin:/usr/bin

# In both a normal CVS environment and a PlanetLab RPM
# build environment, all of our dependencies are checked out into
# directories at the same level as us.
if [ -d ../build ] ; then
    PATH=$PATH:../build
    srcdir=../
else
    echo "Error: Could not find $(cd ../.. && pwd -P)/build/"
    exit 1
fi

export PATH

. build.common

pl_process_fedora_options $@
shiftcount=$?
shift $shiftcount

# pldistro expected as $1 - defaults to planetlab
pldistro=planetlab
[ -n "$@" ] && pldistro=$1

# Do not tolerate errors
set -e

# Some of the PlanetLab RPMs attempt to (re)start themselves in %post,
# unless the installation is running inside the BootCD environment. We
# would like to pretend that we are.
export PL_BOOTCD=1

# "Parse" out the packages and groups into the options passed to mkfedora
# -k = exclude kernel* packages
pkgsfile=$(pl_locateDistroFile ../build/ ${pldistro} bootstrapfs.pkgs)

echo "+++++++++++++pkgsfile=$pkgsfile (and -k)"

# Populate a minimal /dev and then the files for the base PlanetLab-Bootstrap content
vref=${PWD}/base
install -d -m 755 ${vref}
pl_mkfedora ${vref} -k -f $pkgsfile 

for pkgs in ../build/config.${pldistro}/bootstrapfs-*.pkgs ; do
    NAME=$(basename $pkgs .pkgs | sed -e s,bootstrapfs-,,)

    echo "--------START BUILDING PlanetLab-Bootstrap-${NAME}: $(date)"

    # "Parse" out the packages and groups for yum
    packages=$(pl_getPackages ${pl_DISTRO_NAME} $pkgs)
    groups=$(pl_getGroups ${pl_DISTRO_NAME} $pkgs)
    echo "${NAME} has the following packages : ${packages}"
    echo "${NAME} has the following groups : ${groups}"

    vdir=${PWD}/${pldistro}-filesystems/${NAME}
    rm -rf ${vdir}/*
    install -d -m 755 ${vdir}

    # Clone the base reference to the bootstrap fs
    (cd ${vref} && find . | cpio -m -d -u -p ${vdir})
    rm -f ${vdir}/var/lib/rpm/__db*

    # Install the system vserver specific packages
    [ -n "$packages" ] && yum -c ${vdir}/etc/yum.conf --installroot=${vdir} -y install $packages
    [ -n "$groups" ] && yum -c ${vdir}/etc/yum.conf --installroot=${vdir} -y groupinstall $groups

    if [ -f "${vdir}/proc/cpuinfo" ] ; then
	echo "WARNING: some RPM appears to have mounted /proc in ${NAME}. Unmounting it!"
	umount ${vdir}/proc
    fi

    # Create a copy of the ${NAME} bootstrap filesystem w/o the base
    # bootstrap filesystem and make it smaller.  This is a three step
    # process:

    # step 1: clean out yum cache to reduce space requirements
    yum -c ${vdir}/etc/yum.conf --installroot=${vdir} -y clean all

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

    echo "--------STARTING tar'ing PlanetLab-Bootstrap-${NAME}.tar.bz2: $(date)"
    tar -cpjf ${pldistro}-filesystems/PlanetLab-Bootstrap-${NAME}.tar.bz2 -C ${vdir} .
    echo "--------FINISHED tar'ing PlanetLab-Bootstrap-${NAME}.tar.bz2: $(date)"
    echo "--------DONE BUILDING PlanetLab-Bootstrap-${NAME}: $(date)"
done

# Build the base Bootstrap filesystem
# clean out yum cache to reduce space requirements
yum -c ${vref}/etc/yum.conf --installroot=${vdir} -y clean all
echo "--------STARTING tar'ing PlanetLab-Bootstrap.tar.bz2: $(date)"
tar -cpjf PlanetLab-Bootstrap.tar.bz2 -C ${vref} .
echo "--------FINISHED tar'ing PlanetLab-Bootstrap.tar.bz2: $(date)"

exit 0
