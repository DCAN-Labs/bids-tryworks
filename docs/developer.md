# This document contains developer notes for setting up and maintaining bids_tryworks
There are presently two deployed versions of bidsgui, one of them exists on airc at:
`/group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks` 

and the other exists on rushmore at:  
`/mnt/max/home/firmmproc/bids_tryworks_docker/bids_tryworks`

The gui interface on both verisions is identical, what differs between the two is 
how the backend is set up and run. The version on AIRC is a complete stand alone 
django project, while the verison on rushmore makes use of docker to run 4 simultaneous processes at once. Further details are listed below.

## AIRC Version
### Dicom Folder Structure on AIRC
The airc version is an older version that relies on the AIRC's unique method of
organizing MRI scans, that is to say that the AIRC divides each scan into it's own folder such that a scan with a T1, T2, Resting State, Task 1, Task 2 would each possess it's own folder.

```bash
(base) galassi@airclogin-a1:/dicom/2021/12/ID_PI_PI/ID$ ls
001-localizer_quiet             008-T1w_MPR              015-rfMRI_REST_AP
002-T1w_MPR                     009-T1w_MPR              016-rfMRI_REST_AP
003-T1w_MPR                     010-SpinEchoFieldMap_AP  017-rfMRI_REST_AP
004-TESTED_t2_space_sag_p2_iso  011-SpinEchoFieldMap_PA  018-rfMRI_REST_AP
005-TESTED_t2_space_sag_p2_iso  012-rfMRI_REST_PA        019-rfMRI_REST_AP
006-TESTED_t2_space_sag_p2_iso  013-rfMRI_REST_PA        099-Phoenix_Document
007-TESTED_t2_space_sag_p2_iso  014-rfMRI_REST_AP
```

### Keeping Records and scans up to date
There is no automatic way to index the AIRC at the time of this writing. That is to say that any scans made after the command `python manage.py index -d /dicom` will
not appear in the bids_tryworks search because they don't exist in the database. However,
there is no need to despair. 

If one writes a bash script that does the following things:
1) Activate the bids_tryworks virtual environment at: `/group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks/venv`
2) runs the index command: `python /group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks/manage.py index -d <target directory to index>`
3) re-runs that command on some interval (every other day?) but only points it to 
the current month of scans, eg:
`python /group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks/manage.py index -d /dicoms/2020/<current month>`

Then bids_tryworks should stay indexed with a minimum of fuss.

### Indexing right away
If a user wishes to index a directory right away the steps would be the same as the 
above, minus the loop. eg:
```bash
source /group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks/venv/bin/activate  
python /group_shares/fnl/bulk/code/internal/GUIs/bids_tryworks_dev/bids_tryworks/manage.py index -d <target directory to index>
```

### Launching the Server/Starting the app
Typically it's best practice to simply leave bids_tryworks running in the background as it's not terribly resource intensive, however if one needs to launch it can be done with the following commands:


## Docker Version (Deployed on Rushmore)
The docker version is a much more mature and functional piece of software
than the version of bids_tryworks deployed on the AIRC. The docker version 
differs from the straight Django (AIRC) version in a number of ways:
- Runs 4 containers, 3 bids_tryworks and 1 Postgres via docker-compose
- Postgres container provides persistent data storage and a high throughput database that can be hit with requests from many sources.
- bids_tryworks container runs the main service of bidsgui, searching and converting dicoms to bids
- bidsgui_autoindexer container launches a container that watches a single folder for incoming dicoms and then indexes any newly made folders w/in that folder if new dicoms arrive.
- daily_indexer container runs the indexer over the entire contents of the watched/src dicom directory once per day to pick up on any dicoms that may have been missed if the auto_indexer container service was stopped or closed.

### Setup 
0) Collect source code: `git clone https://gitlab.com/Fair_lab/bids_tryworks`
1) cd into cloned dir
2) copy sample.env file to .env `cp sample.env .env`
3) fill out the other side of the variable assignments in your `.env` file. Docker compose will look in this file for values corresponding to `${VALUE}` in your `.env` file. eg:
    ```bash
    # code folder var, aka where the top level of bids_tryworks is.
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


