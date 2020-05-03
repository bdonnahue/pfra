#!/bin/bash

set -e

# ===================================================
# Author and Liscense
# ===================================================

# ===================================================
# Resource Parameters
# ===================================================
# Set the defaults

OCF_RESKEY_service_name_default="foobar"
OCF_RESKEY_promote_script_default="/tmp/promote.sh"
OCF_RESKEY_demote_script_default="/tmp/demote.sh"
OCF_RESKEY_monitor_script_default="/tmp/monitor.sh"

# Assign the default values specified if values were not supplied by the user

: ${OCF_RESKEY_service_name=${OCF_RESKEY_service_name_default}}
: ${OCF_RESKEY_promote_script=${OCF_RESKEY_promote_script_default}}
: ${OCF_RESKEY_demote_script=${OCF_RESKEY_demote_script_default}}
: ${OCF_RESKEY_monitor_script=${OCF_RESKEY_monitor_script_default}}

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
    echo "usage"
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
# Metadata
# ===================================================

pfra_meta_data() {
    CURRENT_DIR=$(dirname $0)
    cat ${CURRENT_DIR}/pfra-metadata.xml
    exit $OCF_SUCCESS
}

# ===================================================
# Actions
# ===================================================

# The start and stop action relies on the service script returning a non zero exit code if the 
# service cannot be started successfully.

pfra_meta_start(){

    # We will check to see if our cluster has a master yet
#    ocf_log info "Checking if any master nodes exist in the cluster"
#    CURRENT_MASTERS=$(pcs status | grep -A 2 named | grep -E '^(\s+)Masters: \[.*\]' || true)

    # If there is no master currently, promote this node and start
#    if [ -z "${CURRENT_MASTERS}" ]; then
#        ocf_log info "A master was not found. Promoting to master"
#        pfra_meta_promote
   # If there is already a master, demote this node and start
#    else
#        ocf_log info "A master was found. Demoting to slave"
        pfra_meta_demote
#    fi

    ocf_log info "Starting the ${OCF_RESKEY_service_name} service using systemctl."
    systemctl reset-failed ${OCF_RESKEY_service_name} || true
    systemctl start $OCF_RESKEY_service_name
    last_exit_code=$?
    ocf_log info "Starting the service returned ${last_exit_code} exit code"
    if [ "$last_exit_code" == "0" ]; then
        ocf_log info "Starting the service succeeded"
        ocf_exit_reason "Starting the service succeeded"
        return $OCF_SUCCESS
    else
        ocf_exit_reason "Starting the service returned a non successful error code: ${last_exit_code}"
        return $last_exit_code
    fi
}

pfra_meta_stop(){
    ocf_log info "Stopping the ${OCF_RESKEY_service_name} service using systemctl."
    systemctl stop $OCF_RESKEY_service_name
    last_exit_code=$?
    ocf_log info "Stopping the service returned ${last_exit_code} exit code."
    if [ "$last_exit_code" == "0" ]; then
        ocf_log info "Stopping the service succeeded."
        ocf_exit_reason "Stopping the service succeeded"
        return $OCF_SUCCESS
    else
        ocf_exit_reason "Stopping the service returned a non successful error code: ${last_exit_code}"
        return $last_exit_code
    fi
}

service_is_running(){
  SERVICE_STATUS=$(systemctl status ${OCF_RESKEY_service_name} | grep -E '^   Active: active \(running\)' || true)
  echo $SERVICE_STATUS
  if [ -z "${SERVICE_STATUS}" ]; then
    return 1
  fi

  return 0 # True
}

pfra_meta_monitor(){
  ocf_log info "Determining the state of the resource."

  if ! service_is_running ; then
    ocf_log info "The service '${OCF_RESKEY_service_name}' is not running."
    ocf_exit_reason "The service '${OCF_RESKEY_service_name}' is not running."
    return $OCF_NOT_RUNNING
  fi

  if [ ! -f ${OCF_RESKEY_monitor_script} ]; then
    ocf_log error "The monitor script does not exist at path: ${OCF_RESKEY_monitor_script}"
    ocf_exit_reason "The monitor script does not exist"
    return $OCF_ERR_GENERIC
  fi

  ocf_log info "Executing the monitor script."
  bash $OCF_RESKEY_monitor_script "$OCF_FUNCTIONS_DIR"

  last_exit_code=$?
  ocf_log info "Monitor Script returned ${last_exit_code} exit code."
  ocf_exit_reason "Monitor Script returned ${last_exit_code} exit code."
  return $last_exit_code

}

pfra_meta_promote(){

#    if ! service_is_running ; then
#      ocf_log error "The service '${OCF_RESKEY_service_name}' cannot be promoted because it is not running."
#      return $OCF_ERR_GENERIC
#    fi

    if [ ! -f ${OCF_RESKEY_promote_script} ]; then
      ocf_log error "The promotion script does not exist at path: ${OCF_RESKEY_promote_script}"
      ocf_exit_reason "The promotion script does not exist"
      return $OCF_ERR_GENERIC
    fi

    ocf_log info "Executing the promotion script."
    bash ${OCF_RESKEY_promote_script}

    last_exit_code=$?
    ocf_log info "The Promotion script returned ${last_exit_code} exit code."
    if [ "$last_exit_code" == "0" ]; then
        ocf_log info "The Promotion script exiting successfully"
        return $OCF_SUCCESS
    else
        ocf_log info "The Promotion script exiting unsuccessfully"
        return $last_exit_code
    fi
}

pfra_meta_demote(){

# We need to be able to demote the notde even if the service is not running

#    if ! service_is_running ; then
#      ocf_log error "The service '${OCF_RESKEY_service_name}' cannot be demoted because it is not running."
#      return $OCF_ERR_GENERIC
#    fi

    if [ ! -f ${OCF_RESKEY_demote_script} ]; then
      ocf_log error "The demotion script does not exist at path: ${OCF_RESKEY_demote_script}"
      ocf_exit_reason "The demotion script does not exist"
      return $OCF_ERR_GENERIC
    fi

    ocf_log info "Executing the demotion script."
    bash ${OCF_RESKEY_demote_script}

    last_exit_code=$?
    ocf_log info "The Demotion script returned ${last_exit_code} exit code."
    if [ "$last_exit_code" == "0" ]; then
        ocf_log info "The Demotion script exiting successfully"
        return $OCF_SUCCESS
    else
        ocf_log info "The Demotion script exiting unsuccessfully"
        return $last_exit_code
    fi
}

# ===================================================
# Main
# ===================================================

case "$1" in
    start)
        pfra_meta_start ;;
    stop)
        pfra_meta_stop ;;
    monitor)
        pfra_meta_monitor ;;
    promote)
        pfra_meta_promote ;;
    demote)
        pfra_meta_demote ;;
    meta-data)
        pfra_meta_data ;;
    *)
        usage ;;
esac
