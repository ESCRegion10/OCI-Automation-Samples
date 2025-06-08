#!/bin/python

#-------------------------------------------------------------------------
#
# Script:       /home/opc/scripts/occ_start_stop_mysql.py
#
# Purpose:      Start and stop OCC MySQL DB resource(s)
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
#               source venv/bin/activate
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
#                       venv/                   -- Python virtual enviroment libraries and configuration files
#                       bin/                    -- python 3.11.5 and pip 24.2 installation directory
#                       scripts/                -- location of Python scripts for OCI OCC automation and maintenance
#                       .ssh/                   -- SSH authorized keys files (filename: authorized_keys)
#
#               Configuraion file:
#               ==================
#               /home/opc/.oci/config
#
# Usage:        python /home/opc/scripts/occ_start_stop_mysql.py [start | stop] [fullpath_filename_to_mysql_db_list]
#
# Revision History:
# Date          Author          Remarks
# 20250115      TE              original version
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

#--------------------------------------------------
#
# Get details of a MySQL DB System base on the OCID
#
#--------------------------------------------------
def get_mysql_db_system(client, db_system_id):
    try:
        response = client.get_db_system(db_system_id)
        return response.data
    except oci.exceptions.ServiceError as e:
        sys.stderr.write(f"Error fetching DB system details: {e}")
        return None

#------------------------
#
# Start MySQL
#
#------------------------
def start_mysql_db(client, db_system_id):
    try:
        print(f"Starting MySQL DB System with OCID: {db_system_id}...")
        response = client.start_db_system(db_system_id)
        oci.wait_until(client, client.get_db_system(db_system_id), 'lifecycle_state', 'ACTIVE')
        print("MySQL DB System is now ACTIVE.")
    except oci.exceptions.ServiceError as e:
        sys.stderr.write(f"Error starting MySQL DB System: {e}")

#------------------------
#
# Stop MySQL
#
#------------------------
def stop_mysql_db(client, db_system_id):
    try:
        print(f"Stopping MySQL DB System with OCID: {db_system_id}...")
        response = client.stop_db_system(db_system_id)
        oci.wait_until(client, client.get_db_system(db_system_id), 'lifecycle_state', 'STOPPED')
        print("MySQL DB System is now STOPPED.")
    except oci.exceptions.ServiceError as e:
        sys.stderr.write(f"Error stopping MySQL DB System: {e}")

#++++++++++++++++++++
#
#  Main
#
#++++++++++++++++++++
print("Program started ...")
now = datetime.now()
print(now.strftime("%m/%d/%Y, %H:%M:%S"))

# Replace with your OCI configuration file path and profile
config = oci.config.from_file("~/.oci/config", "DEFAULT")
# Validating configuration file, making sure the connection is established
oci.config.validate_config(config)
print("Config validated ...")

mysql_client = oci.mysql.DbSystemClient(config)

print("MySQL list read from file ...")

mysql_dbs = []
with open(sys.argv[2], "r") as f:
    for line in f:
        if not line.startswith("#"):
            mysql_dbs.append(line.strip())

print(', '.join(map(str, mysql_dbs)))      # list of oci mysql dbs

print("MySQL instances being put in the " + sys.argv[1] +  " state ...")
for dbs_oci in mysql_dbs:
    if sys.argv[1] == 'stop':
        stop_db_system_response = mysql_client.stop_db_system(db_system_id=dbs_oci,stop_db_system_details=oci.mysql.models.StopDbSystemDetails(shutdown_type="SLOW"))
        print(stop_db_system_response.headers)
    elif sys.argv[1] == 'start':
        start_db_system_response = mysql_client.start_db_system(db_system_id=dbs_oci)
        print(start_db_system_response.headers)
    else:
        sys.stderr.write(f"Error on command-line options, use 'stop' or 'start' ...")
        pass

now = datetime.now()
print(now.strftime("%m/%d/%Y, %H:%M:%S"))
print("Program ended ...")
sys.exit(0)