# Rushmore/Standard bids-tryworks SOP
This document contains specific information related to bids-tryworks as installed on rushmore under user firmmproc. All information is current as of 2020-03-18 (AG)
The following details are documented below:
- Starting bids-tryworks on rushmore
- Indexing the Dicom Data Base for bids-tryworks on rushmore
- Launching and Navigating to bids-tryworks on rushmore

## Starting the App
### First Setup
0) Collect source code: `git clone https://gitlab.com/Fair_lab/bids-tryworks`
1) cd into cloned dir
2) copy sample.env file to .env `cp sample.env .env`
3) fill out the other side of the variable assignments in your `.env` file. Docker compose will look in this file for values corresponding to `${VALUE}` in your `.env` file. eg:
    ```bash
    # code folder var, aka where the top level of bids-tryworks is.
    CODE_FOLDER=
    # Folder containing dicoms to index/convert
    BASE_DICOM_DIR=
    # Folder to convert dicoms to nifti/bids in, conversions occur here, but
    # they don't necessarily stay in this location after conversion is done.
    CONVERTED_FOLDER=
    # Logs (if you've implemented them yet are stored here
    LOG_FOLDER=
    # intermediary files for conversion (aka the config json that dcm2bids needs) are stored here
    DCM2BIDS_FILES=
    # Group and user ids
    UID=
    GID=
    POSTGRES_PASSWORD=password
    POSTGRES_USER=postgres
    ```
    User will have to create directories for the CONVERTED_FOLDER, LOG_FOLDER, and DCM2BIDS_FILES. UID and GID can be ignored for now. CODE_FOLDER must point to the full path of the folder of the repo you cloned in step 0, and BASE_DICOM_DIR must point to the folder where your dicoms are stored.
4) run `docker-compose build .` 
5) run `docker-compose up`
6) navigate to `localhost:8770/dicoms` in your webrowser to begin.
### Post Setup Startup
1) navigate to the directory the cloned bids-tryworks repo is at and execute the following command:
    ```docker-compose up```
### Stoping the app
1) navigate to the directory the cloned bids-tryworks repo is at and execute the following command:
    ```docker-compose down```

## Indexing the Database
### Automatic Indexing
On first startup bids-tryworks will determine whether or not it's indexed the folder specified in the `.env` file prepared earlier at `BASE_DICOM_DIR=`. If it hasn't it will index all dicoms located in that folder. Otherwise, bids-tryworks will index a new folder of flat dicoms (other folder structures have not been extensively tested) once it is created or copied into the `BASE_DICOM_DIR` folder. However, it only detects when new folders are created at the base level of that folder, if you deliver dicoms to an already existing folder in `BASE_DICOM_DIR` it will not pick up on that (03/18/20).

### Routine Indexing
Bidsgui2 will index the `BASE_DICOM_DIR` once per day to catch any files that may have arrived when the application was stopped and not monitoring the folder.

### Manually Indexing
Involves docker exec <id of container> /bin/bash && python manage.py index -d <folder to index> etc etc, not advisable for average users.
## Locating/Navigating to the App
By default Bidsgui2 locates itself at https://localhost/8770/dicoms simply navigate to that webaddress with a browser of choice on the machine that bidsgui2 is installed on to reach the app.
## Gotchas and Other Info.
