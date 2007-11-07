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

# Do not tolerate errors
set -e

# Some of the PlanetLab RPMs attempt to (re)start themselves in %post,
# unless the installation is running inside the BootCD environment. We
# would like to pretend that we are.
export PL_BOOTCD=1

# "Parse" out the packages and groups into the options passed to mkfedora
# -k = exclude kernel* packages
options="-k"
packages=$(pk_getPackages base.lst)
groups=$(pk_getGroups base.lst)
for package in ${packages} ; do  options="$options -p $package"; done
for group in ${groups} ; do options="$options -g $group"; done

# Populate a minimal /dev and then the files for the base PlanetLab-Bootstrap content
vref=${PWD}/base
install -d -m 755 ${vref}
pl_makedevs ${vref}
pl_setup_chroot ${vref} -k ${options}

for bootstrapfs in bootstrap-filesystems/*.lst ; do
    NAME=$(basename $bootstrapfs .lst)

    echo "--------START BUILDING PlanetLab-Bootstrap-${NAME}: $(date)"

    # "Parse" out the packages and groups for yum
    packages=$(grep "^package:.*" $bootstrapfs | awk '{print $2}')
    groups=$(grep "^group:.*" $bootstrapfs | awk '{print $2}')

    vdir=${PWD}/bootstrap-filesystems/${NAME}
    rm -rf ${vdir}/*
    install -d -m 755 ${vdir}

    # Clone the base reference to the bootstrap fs
    (cd ${vref} && find . | cpio -m -d -u -p ${vdir})
    rm -f ${vdir}/var/lib/rpm/__db*

    # Install the system vserver specific packages
    [ -n "$systempackages" ] && yum -c ${vdir}/etc/yum.conf --installroot=${vdir} -y install $systempackages
    [ -n "$systemgroups" ] && yum -c ${vdir}/etc/yum.conf --installroot=${vdir} -y groupinstall $systemgroups

    # Create a copy of the system vserver w/o the vserver reference files and make it smaller. 
    # This is a three step process:

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
    tar -cpjf bootstrap-filesystems/PlanetLab-Bootstrap-${NAME}.tar.bz2 -C ${vdir} .
    echo "--------FINISHED tar'ing PlanetLab-Bootstrap-${NAME}.tar.bz2: $(date)"
    echo "--------DONE BUILDING PlanetLab-Bootstrap-${NAME}: $(date)"
done

# Build the base Bootstrap filesystem
echo "--------STARTING tar'ing PlanetLab-Bootstrap.tar.bz2: $(date)"
# clean out yum cache to reduce space requirements
yum -c ${vref}/etc/yum.conf --installroot=${vdir} -y clean all
tar -cpjf PlanetLab-Bootstrap.tar.bz2 -C ${vref} .
echo "--------FINISHED tar'ing PlanetLab-Bootstrap.tar.bz2: $(date)"

exit 0
