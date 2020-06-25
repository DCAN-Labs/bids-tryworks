# bids-tryworks Conversion SOP
Bidsgui
For server specific setup instructions and or server specifics see documents:  
- [Standard Install](rushmore.md) 
- [AIRC](airc.md)

## Navigate to Site/App
- bids-tryworks Linked to FIRMM on Rushmore is located at [http://localhost:8770/dicoms/](http://localhost:8770/dicoms/)
- bids-tryworks on Rushmore is located at [http://localhost:8870/dicoms/](http://localhost:8870/dicoms/)
- bids-tryworks on Airc is located at [http://localhost:8080/dicoms/](http://localhost:8080/dicoms/)

## Searching for Dicoms
The first page upon navigating to `localhost:<port>/dicoms` can be seen below:  
![search page image](/images/search.png)  
There are several ways to search for dicoms with bids-tryworks:
1) Search by Subject ID
    - One can search by an exact or partial subject ID
    - If one is attempting to find multiple subjects that share a common id string (such as NDAR) in the ABCD Study. A search of ndar or NDAR will return all such 
    subjects since searches are not case sensitive.
2) Search by Study Description
    - One can can retrieve all scans related to a specific study by searching the exact or partial study description
3) Start Date
    - Will only return scans that occur on or after this date if this field is filled. If left blank,it defaults to epoch time (Jan 1 1970).
4) End Date
    - Will only return scans that occur on or before this date, if left blank defaults to today's date.
5) Multi Search
    - Multi Search Allows the user to search for multiple subjects using a text file with one subject per line. Formatting of the file should be identical to below:
        ```txt
        subject1
        subject2
        subject3
        ...
        subjectn
        ```

## Selecting Search Results
Once your execute your search you'll arrive at the page below.
![selected subjects](/images/selected_subjects.png)
Here you can select some, none, or all of the subjects that turned up as a result from your
search. 
### Renaming Subjects
Sometimes the PatientID contained in the the dicom header differs from the actual subject's ID, if you come across
this use case simple select the subject(s) and click on the rename button. A field will pop up for each subject you've selected
and you'll be able to rename the subject according  to the information you enter into the text field as seen below.  
![renaming_subjects](images/rename_before.png)  
The Patient ID is still kept (since we want to keep the dicom data atomic) and the new name can now be seen in the selection
window under the 2nd column of information listed there in.  


Once you've made your selection click on the `Choose These Sessions` button to convert these subjects. 

## Building a Conversion Form/Reusing a Conversion Form
When you first arrive at the conversion page you will see
the following:
![convert builder page](/images/convert_page_first_load.PNG)  
### Uploading your own dcm2bids conversion JSON
If you already possess a valid dcm2bids configuration file you can upload it to bidsgui to be used
on the subjects and sessions you selected previously in your search results. Simply click on the 
upload button and select the desired file using the
file selection menu as seen here:  
![file_selection_menu](/images/convert_page_file_browser.PNG)  
You can visually inspect the contents of the file within the text window but you will not 
be able to modify the file from this view, instead edit the file locally with your editor 
of choice should you wish to make changes.  
![file_contents_text_window](/images/convert_page_upload_json_before_submit.PNG)  
Once you've determined that the file you've uploaded is correct press the `Use Uploaded JSON to Convert` button,
your screen should now resemble the image below:
![file_submitted](/images/convert_page_upload_json_after_submit.PNG)  

Note, if you instead wish to create a conversion json via the gui simply hit the back button
and start over from the search selection page.
### Reusing a Previously Saved Conversion File
If you wish to re-use a previously created conversion file first check the tick box labled:
`Choose a previously used conversion file`. Then select the desired conversion file from the drop down here:  
![select_previously_used_file](/images/select_previously_used_file.PNG)  
### Creating a New Conversion File
Otherwise, if you wish to build a new file select the checkbox labeled `Create New Conversion Form`. 
Doing so should make something like the following appear on your page:  
![converter builder menu](/images/convert_page_create_new_conversion_file_selected.PNG)  

## Transferring Converted Subjects
Once you've built/uploaded/selected your conversion file with the above you'll need to pick 
a destination to deliver your subjects to. Once you've filled in the 
following fields with the appropriate values bids-tryworks will begin to 
convert your dicoms into bids and deliver them.

The fields below need to filled as followed:
- Output Folder Name For This Session
    - This will be the parent folder for all sessions selected during this
    conversion.
- Name for new Config
    - The name you wish to save your newly created conversion file to,
    you can ignore if you're reusing a previously created conversion file.
- Remote Server
    - this can be either the local or a remote server you wish to move the
    converted session files to. Even if you're moving the files locally
    you need to fill out this field with your machine's hostname. Filling
    out this field and the user fields below helps to ensure your converted
    files end up with the correct file permissions on their arrival to
    their output destination
- Username
    - Use the username of the remote/destination folder you're delivering
    these files to.
- Password
    - the Password associated with the username entered above. Note:
    passwords are not stored within this application.
![Tranferring Subjects](/images/remote_transfer.PNG)

To start your conversion click the `Convert` button and wait. You'll recieve a message once all of your conversions are done.

