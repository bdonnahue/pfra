#!/bin/bash

# ===================================================
# Author and Liscense
# ===================================================

# ===================================================
# Resource Parameters
# ===================================================
# Assign the default values specified if values were not supplied by the user

: ${OCF_RESKEY_promote_script_default="/tmp/promote.sh"}
: ${OCF_RESKEY_demote_script_default="/tmp/demote.sh"}

# ===================================================
# Initialize
# ===================================================

: ${OCF_FUNCTIONS_DIR=${OCF_ROOT}/lib/heartbeat}
. ${OCF_FUNCTIONS_DIR}/ocf-shellfuncs

# ===================================================
# Usage
# ===================================================
# The following actions must be supported by any resource agent
#       start - starts the resource.
#       stop - shuts down the resource.
#       monitor - queries the resource for its state.
#       meta-data - dumps the resource agent metadata.
#
# In addition, resource agents may optionally support the following actions:
#       promote - turns a resource into the Master role (Master/Slave resources only).
#       demote - turns a resource into the Slave role (Master/Slave resources only).
#       migrate_to and migrate_from - implement live migration of resources.
#       validate-all - validates a resource’s configuration.
#       usage or help - displays a usage message when the resource agent is invoked from the command line, rather than by the cluster manager.
#       status - historical (deprecated) synonym for monitor.

usage() {
    cat <<EOF
        usage: $0 start|stop|monitor|meta-data|promote|demote
        $0 manage resources which support a master-slave configuration.
        The 'start' operation starts named server.
        The 'stop' operation stops  named server.
        The 'monitor' operation reports whether named is running.
        The 'metat-data' operation dumps the resource agent metadata.
        The 'promote' operation configures a resource to perform the master role.
        The 'demote' operation configures a resource to perform the slave role
EOF
  return $OCF_ERR_ARGS
}

# Note: The $OCF_ERR_ARGS error code indicates that the resource agent was invoked with 
# incorrect arguments. This is a safety net "can’t happen" error which the resource agent should only return when invoked with, for example, an incorrect number of command line arguments.

# ===================================================
# Actions
# ===================================================