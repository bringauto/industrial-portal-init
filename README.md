# Init script for BringAuto Fleet Management

Script for initialization of the [BringAuto Fleet Management] database
    - Script will delete all of the database content and fill up data from map json files

## Prerequisites:

- The [BringAuto Fleet Management] must be deployed and work

!!! **this script will delete all entries in the database** !!!

If you do not want to delete the database content, comment out the `delete_all` function call

## Arguments
* -c or --config=```<file>``` - config file (default: config/config.ini)
* -d or --directory=```<directory>``` - directory with input files (default: maps/)

## Config file
Example:

[DEFAULT]
```
ApiKey = <apikey>
Url = localhost
```

### Sections
All parameters in ```DEFAULT``` section are required to let the script work.

## Build and run
Install requirements:
```
pip3 install -r requirements.txt
```

Example run:
```
python3 main.py -c config/config.ini -d maps
```

[BringAuto Fleet Management]: https://github.com/bringauto/fleet-management-http-api