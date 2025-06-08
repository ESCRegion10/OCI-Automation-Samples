#!/bin/python

#-------------------------------------------------------------------------
#
# Script:       /home/opc/scripts/occ_start_stop_instances.py
#
# Purpose:      Start and stop OCC resource(s)
#
# Notes:        Notes on usage and Python virtual environment and directory structure
#
#               Authorized key(s) file:
#               =======================
#               /home/opc/.ssh/authorized_keys
#
#               To enter/activate Python virtual environment:
#               =============================================
#               login as 'opc' (which is done by default)
#               source .venv/bin/activate
#
#               To exit current Python virtual environment:
#               ===========================================
#               deactivate
#
#               Directory structure within Python virtual environment:
#               ======================================================
#               /home/opc/                      -- user opc home directory
#                       .oci/                   -- OCI configuration and API keys directory
#                           config              -- OCI configuration file and API key file
#                       .venv/                  -- Python virtual enviroment libraries and configuration files
#                       bin/                    -- python 3.11.5 and pip 24.2 installation directory
#                       scripts/                -- location of Python scripts for OCI OCC automation and maintenance
#                       .ssh/                   -- SSH authorized keys files (filename: authorized_keys)
#
#               Configuraion file:
#               ==================
#               /home/opc/.oci/config
#
# Usage:        python /home/opc/scripts/oci_dev_web.py [start | stop] [fullpath_filename_to_computers_list]
#
# Log:          /home/opc/logs/occ_start_stop_instances.py.log
#
#
# Revision History:
# Date          Author          Remarks
# 20240807      TE              original version
#
#-------------------------------------------------------------------------

#-------------------
#
# Packages
#
#-------------------
import sys
import oci
import os
from datetime import datetime
from collections import deque

#-------------------
#
# Functions
#
#-------------------
# save only last 1000 lines of log file
def save_last_1000_lines(input_file, output_file):
    with open(input_file, 'r') as infile:
        last_1000_lines = deque(infile, maxlen=1000) # Keeps only the last 1000 lines
        with open(output_file, 'w') as outfile:
            outfile.writelines(last_1000_lines)

# create and write to log file
def log(txt, logfile):
    f = open(logfile, "a")
    f.write(txt + '\n')
    f.close()

#-------------------
#
#  Main program
#
#-------------------
pathname, extension = os.path.splitext("/home/opc/logs/" + os.path.basename(__file__))
filename = pathname.split('/')

logfile = filename[-1]  + ".log"
log("Program started ...", logfile)
save_last_1000_lines(logfile, logfile)

now = datetime.now()
log(now.strftime("%m/%d/%Y, %H:%M:%S"), logfile)

#setting config path, default path is ~/.oci/config (make sure not on VPN)
config = oci.config.from_file()

#validating configuration file, making sure the connection is established
oci.config.validate_config(config)

log("Config validated ...", logfile)

# Initialize service client
core_client = oci.core.ComputeClient(config)
core_client.base_client.set_region('<YOUR_REGION>')

log("Client initialized ...", logfile)

# Send the request to service, there are more available parameters to send in the request
list_instances = core_client.list_instances(compartment_id="<YOUR_COMPARTMENT_OCID>")  

log("Service requested ...", logfile)

with open(sys.argv[2]) as f:
    computers = f.read().splitlines()

log("Computers list read from file ...", logfile)

log(', '.join(map(str, computers)), logfile)

log("Computers stopping or starting ...", logfile)
# For every instance send stop or start command
for i in list_instances.data:
    if i.display_name in computers and sys.argv[1] == 'stop':
        core_client.instance_action(i.id,'SOFTSTOP')
        log(f"Sent SOFTSTOP command to instance : {i.display_name}", logfile)
    elif i.display_name in computers and sys.argv[1] == 'start':
        core_client.instance_action(i.id,'START')
        log(f"Sent START command to instance : {i.display_name}", logfile)
    else:
        pass

now = datetime.now()
log(now.strftime("%m/%d/%Y, %H:%M:%S"), logfile)
log("Program ended ...", logfile)
sys. exit(0)
                                     

                                                   
