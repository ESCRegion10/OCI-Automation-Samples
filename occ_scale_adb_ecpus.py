#!/bin/python

#-------------------------------------------------------------------------
#
# Script:       /home/opc/scripts/occ_scale_adb_ecpus.py
#
# Purpose:      Scales up or down the ADB ECPU count
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
# Usage:        python /home/opc/scripts/occ_scale_adb_ecpus.py [ECPU count] [OCI ADB console database name]
#
# Example:      python /home/opc/scripts/occ_scale_adb_ecpus.py 5 MY_ADB
#
# Revision History:
# Date          Author          Remarks
# 20250320      TE              original version
#
#-------------------------------------------------------------------------

# Packages
import oci
import numbers
import sys
import platform

# Load the default OCI configuration
os = platform.system()
if os == "Windows":
    config = oci.config.from_file("C:/Users/<YOUR_WINDOWS_USER_NAME>/%HOMEDRIVE%%HOMEPATH%/.oci/config")  # for Windows
elif os == "Linux":
    config = oci.config.from_file("~/.oci/config", "DEFAULT")  # for Linux
else:
    print(f"Unknown operating system {os} ...") 
    sys.exit(2)  

# Initialize the database client
database_client = oci.database.DatabaseClient(config)

# Function to get current Autonomous Database details
def get_autonomous_db(db_id):
    response = database_client.get_autonomous_database(db_id)
    return response.data

# Function to scale Autonomous Database ECPU
def scale_autonomous_db(db_id, new_ecpu_count):
    update_details = oci.database.models.UpdateAutonomousDatabaseDetails(
        compute_count=new_ecpu_count  # Specify the new ECPU count
    )
    response = database_client.update_autonomous_database(db_id, update_details)
    return response.data

# Main execution
if __name__ == "__main__":

    if len(sys.argv) > 2:
        try:
            new_ecpu = int(sys.argv[1])  # Get the desired ECPU count from the 1st command-line argument
           
            # Get the Autonomous Database OCID from the 2nd command-line argument
            if (sys.argv[2] == '<YOUR_DEV_ADB_NAME>'):   
                ADB_OCID = "<YOUR_DEV_ADB_OCID>"  
            elif (sys.argv[2] == '<YOUR_PROD_ADB_NAME>'):  
                ADB_OCID = "<YOUR_PROD_ADB_OCID>" 
            else:
                print(f"Please provide a valid ADB name for the second command-line argument ...")            
        
        except ValueError:    
            print(f"Please provide a number as the first command-line argument for new ECPU count ...") 
    else:
        print(f"Please provide the new ECPU count the first command-line argument and the ADB name to scale as the second command-line argument ...") 
        sys.exit(3)

    try:
        # Fetch current database details
        db_info = get_autonomous_db(ADB_OCID)
        print(f"Current ECPU: {int(db_info.compute_count)}")

        # Scale the database
        print(f"Scaling database {sys.argv[2]} to {new_ecpu} ECPU ...")

        try:
            scale_autonomous_db(ADB_OCID, new_ecpu)
            print(f"Scaling operation initiated successfully ...")
        except oci.exceptions.ServiceError:
            print(f"Scaling not needed because current configuraion already at requested scale ...")
            sys.exit(0)      

    except oci.exceptions.ServiceError as ex:
        print(f"OCI Service Error: {ex}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

sys.exit(0)