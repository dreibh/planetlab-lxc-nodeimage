<?php
//
// part of yum config on nodes
//
// Thierry Parmentelat 
// Copyright (C) 2008 INRIA
//
// $Id: myplc.repo.php 9818 2008-07-04 07:54:06Z thierry $
//

// For PLC_NAME and PLC_BOOT_HOST
include('plc_config.php');

$PLC_NAME = PLC_NAME;
$PLC_BOOT_HOST = PLC_BOOT_HOST;

// Get admin API handle
require_once 'plc_api.php';
global $adm;

if (isset($_REQUEST['gpgcheck'])) {
  $gpgcheck = $_REQUEST['gpgcheck'];
} else {
  $gpgcheck = 0;
}

# we assume the node is not so old that it would not send node_id
# get node family
if ( ! isset($_REQUEST['node_id'])) {
  echo "# myplc.repo.php: node_id is needed";
  echo "# looks like you're running a very old NodeManager...";
  echo "# bailing out..";
  exit;
 }

$node_id = intval($_REQUEST['node_id']);
$nodeflavour=$adm->GetNodeFlavour($node_id);
$nodefamily=$nodeflavour['nodefamily'];

$topdir=$_SERVER['DOCUMENT_ROOT'] . "/install-rpms/" . $nodefamily;
$topurl="https://$PLC_BOOT_HOST" . "/install-rpms/" . $nodefamily;

if (! is_dir (realpath($topdir))) {
  echo "# WARNING: plc-side yum repo $topdir NOT FOUND !!";
 }

echo <<< __PLC_REPO__
[$id]
name=$name
baseurl=$topurl
gpgcheck=$gpgcheck

__PLC_REPO__;

?>
