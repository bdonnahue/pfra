#!/bin/bash

# This script is responsible for promoting a zone to the role of master
#
# It was designed to plug into the pacemaker framework and return exit codes
# as specified in the developer guide
#
# It is assumed that if we got here, the bind service is running

set -e

# Load our utility functions so we can return the right error codes
# 	We assume the first parameter passed to the script is the path to the OCF_ROOT
#	If this is not the case, we will manually set the value of the return code

	if [ -z "$1" ]; then
		OCF_SUCCESS=0
		OCF_NOT_RUNNING=7
		OCF_RUNNING_MASTER=8
	else
		: ${OCF_FUNCTIONS_DIR="$1"}
		. ${OCF_FUNCTIONS_DIR}/ocf-shellfuncs
	fi

# Determine if the service is running

	echo "Determining if the service is running"

	SERVICE_STATUS=$(systemctl status named | grep -E '^   Active: active \(running\)' || true)
	
	if [ -z "${SERVICE_STATUS}" ]; then
		echo "The service is not running"
		exit $OCF_NOT_RUNNING 
	fi

# Determine if the server is configured to be the master
#
#	Note: To do this, we rely on the promote.sh script. We assume that if the service is running,
#	      It is running the config file found at the specified location.

	echo "Determining if this node is configured as a cluster master"

	MASTER_STATEMENTS=$( cat /etc/named/zones/barfoo.com.conf | grep -E "^(\s+)type master;" || true)

	if [ -z "${MASTER_STATEMENTS}" ]; then
		echo "This node is configured as a cluster slave"
		exit $OCF_SUCCESS 
	else
		echo "This node is configured as a cluster master"
		exit $OCF_RUNNING_MASTER
	fi

