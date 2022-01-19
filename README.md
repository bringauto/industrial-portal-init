
# Init script for BringAut Industrial Portal

Script for initialization of the database of Industrial Portal.

## Usage

Prerequisites:

- The Industrial Portal must be deployed and works

!!! **script will delete all entries in the database!** !!!

If you do not want to delete database content comment out `delete_all` function call

Usage:

- Install requirements by `pip3 install -r requirements`
- Edit endpoint and login info in main.py script
- Edit config.json script
- run `python3 main.py` --> Script will delete the content of the database and fill up data from config script

As a main config file the config.json is used.
