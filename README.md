# Init script for BringAuto Fleet

Script for initialization of the database of [BringAuto Fleet]

## Usage

Prerequisites:

- The [BringAuto Fleet] must be deployed and works

!!! **script will delete all entries in the database!** !!!

If you do not want to delete database content comment out `delete_all` function call

Usage:

- Install requirements by `pip3 install -r requirements.txt`
- Edit endpoint and login info in main.py script
- Edit config.json script
- run `python3 main.py` --> Script will delete the content of the database and fill up data from config script

As a main config file the config.json is used.


[BringAuto Fleet]: https://github.com/bringauto/fleet