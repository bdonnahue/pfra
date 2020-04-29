#!/bin/bash

set -e
set -x


# Install the software for the dns server (this is the service we are testing with)
	yum -y install bind bind-utils net-tools

# Install the pacemaker software
	yum -y install pcs	

# Install the mock service
#	https://linuxhint.com/systemd_unit_file_service/

	SCRIPT_DIR=$(dirname "$0")
 	yes | cp -f ${SCRIPT_DIR}/MockService/MockService.service /usr/lib/systemd/system/
	systemctl daemon-reload
