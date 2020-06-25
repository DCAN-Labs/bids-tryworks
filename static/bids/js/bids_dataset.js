class BidsDataset {
    /* a class to encapsulate a BIDS Dataset description, including the hierarchy Subjects >> Sessions >> Series (aka Images) 
    This is intended to be a data structure and appropriate operations only, no User Interface elements
    */
    constructor(data) {
        this.data = data;
    }

    getSelections() {
        return this.data;
    }

    toggleSelection(id_obj, new_selected_value) {
        //id_obj should have subject_id, session_id, series_number, series_description
        var subject = this.data[id_obj.subject_id];

        if (subject) {
            var series_list = subject.sessions[id_obj.session_date];

            if (series_list) {
                for (var idx in series_list) {
                    var series_row = series_list[idx];
                    if (series_row.SeriesNumber == id_obj.SeriesNumber && series_row.SeriesDescription == id_obj.SeriesDescription) {
                        series_row.selected = true;
                        return;
                    }
                }
            }
        }


        alert("Not found. Selection not stored.");

    }
    
    getSelectedCountsBySession() {
        /*
            returns an object with keys = subject_id and values = 
                and object with keys = session_date and value = count of selected images/series 
                in that session
        */
        var results = {};
        for (var subj_id in this.data) {
            var subject = this.data[subj_id];
            var subj_sessions = {};
            for (var date in subject.sessions) {
                
                var count = 0;
                
                var session = subject.sessions[date];
                
                for (var idx in session) {
                    var series = session[idx];
                    if (series.selected) {
                        count++;
                    }
                }
                subj_sessions[date] = count
                
            }
            results[subj_id] = subj_sessions;
        }
        return results;
    }
    getAllSelectedSeries() {
        
        var results = [];
        for (var subj_id in this.data) {
            var subject = this.data[subj_id];
            
            for (var date in subject.sessions) {
                var session = subject.sessions[date];
                
                for (var idx in session) {
                    var series = session[idx];
                    if (series.selected) {
                        
                        var series_plus_context = Object.assign({"subject_id":subj_id, "date":date}, series)
                        results.push(series_plus_context);
                    }                    
                }
            }
        }
        return results;
    }
    
    getAllSelectedSubjectIds() {
        var selected_series = this.getAllSelectedSeries();
        
        var subj_ids = {}
        
        for (var i in selected_series) {
            var series = selected_series[i];
            subj_ids[series.subject_id]=true;
        }
        
        return Object.keys(subj_ids);
    }
    forEachSeries(f) {
        /* apply function f to each series and collect the non-empty results in an array*/
        var results = [];
        for (var subj_id in this.data) {
            var subject = this.data[subj_id];
            
            for (var date in subject.sessions) {
                var session = subject.sessions[date];
                
                for (var idx in session) {
                    var series = session[idx];
                    var result = f(series);
                    if (result) {
                        results.push(result);
                    }
                }
            }
        }
        return results;
    }
    
    getSeries(subject_id, session_date) {
        return this.data[subject_id].sessions[session_date];
    }
    
    getAvailableSelectionFilters() {
        var choices = this.forEachSeries(this.mapNameSelectionFilterDesc);
        choices = $.unique(choices);
        
        return choices;
    }
        
    mapNameSelectionFilterDesc(series) {
        var name = series.json_path;
        var parts = name.split("/");
        name = parts[parts.length-1]
        name = name.split(".json")[0];
        
        //now we have the BIDS name of the file and we will parse that and throughout the variable by subject/session/run parts
        
        parts = name.split("_");
        
        var keep = $.map(parts, function(name_segment) {
            var key = name_segment.substring(0,4);
            
            if (key == "sub-" || key == "ses-" || key == "run-") {
                return null;
            } else {
                return name_segment;
            }
        });
        
        var final = keep.join("_");
        return final;
    }
    
    toggleSelectionByMappingRule(condition, value) {
        var mapper = this.mapNameSelectionFilterDesc;
        
        var count_matched_condition = 0;
        var count_changed = 0;
        this.forEachSeries(function(series) {
            
            if (mapper(series).indexOf(condition)>=0 ) {
                count_matched_condition += 1;
                var should_be = value ? true : false;
                
                if ((series.selected ? true : false ) != should_be) {
                    series.selected = should_be;
                    count_changed += 1
                }
                
            }
        })
        return {"matching":count_matched_condition, "changed": count_changed};
    }
    
    selectBySidecarPath(sidecars) {
        
        var sidecars_as_object = sidecars.reduce(function(o,k){o[k]=true;return o},{});
        
        var matches = {}
        this.forEachSeries(function(series){
            var sidecar_path = series.json_path;
            if (sidecar_path && sidecar_path in sidecars_as_object) {
                series.selected = true;
                matches[sidecar_path] = true;
            }
        })
        
        var match_count = Object.keys(matches).length;
        var mismatches=[];
        if (match_count < sidecars_as_object.length) {

            for (var i=0;i<sidecars_as_object.length;i++) {
                var sidecar = sidecars[i];
                if (! sidecar in matches) {
                    mismatches.push(sidecar)
                }
            }
        }
        mismatches.push("dogcatdogcat")
        return {"match_count":match_count, "mismatches":mismatches}
    }
}


