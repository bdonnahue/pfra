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
	else
		: ${OCF_FUNCTIONS_DIR="$1"}
		. ${OCF_FUNCTIONS_DIR}/ocf-shellfuncs
	fi

# Update the config files

	yes | cp -f /etc/named/zones/barfoo.com.conf.slave.bak /etc/named/zones/barfoo.com.conf

# Reload the updated config file
#       If the service is already running we can use rndc to reload the configs

        SERVICE_STATUS=$(systemctl status named | grep -E '^   Active: active \(running\)' || true)

        if [ -z "${SERVICE_STATUS}" ]; then
		systemctl reset-failed named
                systemctl start named
                exit $OCF_SUCCESS
        fi

#       Note: We need to run this command first: rndc-confgen
#       If the service is not running, start it and exit

 
	rndc -V -k /etc/named/zones/foreman.key reload

# Retrun the correct return code

	exit $OCF_SUCCESS 
