/*
This class wraps all calls to the BIDSGUI server
*/
class BidsAPI {
    constructor(optional_general_error_handler_function) {
        /* a function passed to this constructor will be called for any failed responses.  if not provided, 
        a default function will be used that outputs the error in the browsers debug console.
        */
        
        if (optional_general_error_handler_function) {
            this.generalErrorHandler = optional_general_error_handler_function;
        }
    }
    generalErrorHandler(r) {
        
        console.log("Received an error from the server:")
        console.log(r);
    }
    
        
    login(passcode) {
        return $.post('login',{"passcode":passcode}).fail(this.generalErrorHandler);
    }
    
    
    /*conversion related */
    
    search_dicoms_by_subject_ids(subject_ids) {
        
        var data = {
            "subject_ids": subject_ids
        };
        
        return $.get("/search", data, null, 'json').fail(this.generalErrorHandler);
    }
    
    convert_to_bids(series_descriptions, selected_sessions, target_dir) {
        var post_data = series_descriptions;
    
        post_data.sessions = selected_sessions;

        post_data.study_dir = target_dir

        var json = JSON.stringify(post_data);
        
        return $.post("convert_to_bids", json, null, 'json').fail(this.generalErrorHandler);
    }

    /* processing related */
    getSidecarPreview(path) {
        return $.get('sidecar',{"path":path}).fail(this.generalErrorHandler);
    }
    
    postSidecarUpdate(path, key, value) {
        
        var json = JSON.stringify({"path":path,"key":key, "value":value});
        return $.post('sidecar_update', {"path":path,"key":key, "value":value}).fail(this.generalErrorHandler)
    }
    

    
    
    launch_processing_job(payload) {

        payload = JSON.stringify(payload);
        return $.post("launch_processing_job", payload, null, 'json').fail(this.generalErrorHandler);

    }
    
    saveSelections(payload) {

        payload = JSON.stringify(payload);
        return $.post("bids_selection_file", payload, null).fail(this.generalErrorHandler);

    }
    
    loadBidsDataset(request_data) {
        return $.getJSON("load_bids_dataset", request_data).fail(this.generalErrorHandler);
    }
    
    getSavedSelections(path) {
        return $.getJSON("saved_selections", {
            "path": path
        }).fail(this.generalErrorHandler);
    }
    
    loadStudies() {
        return $.getJSON('studytree').fail(this.generalErrorHandler);
    }
    
    rebuildIndex() {
        return $.post('rebuild_index').fail(this.generalErrorHandler);
    }
}