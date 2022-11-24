# Init script for BringAuto Fleet

Script for initialization of the database of [BringAuto Fleet]
    - Script will delete the content of the database and fill up data from config script

## Prerequisites:

- The [BringAuto Fleet] must be deployed and works

!!! **script will delete all entries in the database!** !!!

If you do not want to delete database content comment out `delete_all` or `delete_users` functions calls

## Arguments
* -c or --config=```<file>``` - config file (default: config/config.ini)
* -d or --directory=```<directory>``` - directory with input files (default: maps/)

## Config file
Example:

[DEFAULT]
```
Username = <username>
Password = <password>
Url = localhost
Port = 8011
```

### Sections
All parameters in ```DEFAULT``` section are required to let script works.

## Build and run
Install requirements:
```
pip3 install -r requirements.txt
```

Example run:
```
python3 main.py
```

[BringAuto Fleet]: https://github.com/bringauto/fleet