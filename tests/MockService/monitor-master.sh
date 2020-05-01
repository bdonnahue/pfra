#!/bin/bash

# Load our utility functions so we can return the right error codes
#     We assume the first parameter passed to the script is the path to the OCF_ROOT
: ${OCF_FUNCTIONS_DIR="$1"}
. ${OCF_FUNCTIONS_DIR}/ocf-shellfuncs

exit $OCF_RUNNING_MASTER