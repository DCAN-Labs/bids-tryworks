# AIRC Bidsgui SOP
This document contains specific information related to:
- Starting Bidsgui2 on airclogin-a1
- Indexing the Dicom Data Base for Bidsgui2 on airlogin-a1
- Launching and Navigating to Bidsgui2 on localhost@airclogin-a1

### Recommended Software and Access
- X2Go Client, when accessing any server remotely X2Go is recommended you'll have faster response to graphical elements such
as web browsers when using X2Go over ssh clients such as MobaXterm. X2Go is available on all platforms (Windows, Linux, and Mac)
- If connecting remotely OHSU's vpn client packaged w/ CiscoAnyconnect for more detail about setting up this client on your work
or personal PC see [here](https://o2.ohsu.edu/information-technology-group/help-desk/it-help-pages/faq-vpn.cfm)
- access to airclogin-a1
#### Macintosh Only
- XQuartz, if using X2Go. X2Go requires an Xserver application and one is not packaged with X2Go on Mac.

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
not appear in the bidsgui2 search because they don't exist in the database. However,
there is no need to despair. 

If one writes a bash script that does the following things:
1) Activate the bidsgui2 virtual environment at: `/group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/venv`
2) runs the index command: `python /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/manage.py index -d <target directory to index>`
3) re-runs that command on some interval (every other day?) but only points it to 
the current month of scans, eg:
`python /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/manage.py index -d /dicoms/2020/<current month>`

Then bidsgui2 should stay indexed with a minimum of fuss.

### Indexing right away
If a user wishes to index a directory right away the steps would be the same as the 
above, minus the loop. eg:
```bash
source /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/venv/bin/activate  
python /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/manage.py index -d <target directory to index>
```

### Launching the Server/Starting the app
Typically it's best practice to simply leave bidsgui2 running in the background as it's not terribly resource intensive, however if one needs to launch it can be done with the following commands:

```bash
galassi@airclogin-a1:/group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/launch.sh 
```

## Locating/Navigating to the App
Presently bidsgui2 is located at `http://localhost/8080/dicoms` on airclogin-a1. If it's unreachable at this webaddress then the webserver is either down or it's located at a different address. To determine which of those two states is the case:

It's recommended to try launching it via the above step.

Or to locate which port it's been assigned by entering `ps aux | grep manage.py` into a terminal and look for the last 4 numbers following 
`manage.py runserver`, in our case below we can see that the server is up and running at port `8080`:
```bash
(base) galassi@airclogin-a1:~$ ps aux | grep manage.py
galassi  17226 10.5  0.0 198952 57944 ?        Sl   Feb13 117:19 /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/venv/bin/python /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2_dev/bidsgui2/manage.py runserver 8080
```
Replace the 4 numbers in the web address `http://localhost/8080/dicoms` with those found via `ps aux | grep manage.py`
like so `https://localhost/<4 new numbers>/dicoms` and navigate to the app/site. 

For additional information on how to operate the application once you've reached it see the sop at [this link](sop.md).

## Gotchas and Other Info.
