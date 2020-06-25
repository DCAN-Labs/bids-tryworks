
class ConvertGui {
    constructor(app) {
        this.app = app;
    }
    
    initUI() {
        //as the user adds or removes a target directory value the Run Conversion button's 
        //enabled status must be updated
        var that = this;
        var updater = function(){that.updateStatus()}
        $('#convert_target_dir').keyup(updater).change(updater);
                
        $('#btn_create_bids').click(function(e){that.onClickCreateBids(e)});
        
        $('#rebuild_index').click(function(){that.onClickReindex()})
    }

    onClickReindex() {
        var ok = confirm("This will reindex all dicoms your mounted /dicoms volume and could take a while to complete. Are you sure you want to continue?")
        var that = this;
        if (ok) {
            this.app.api.rebuildIndex().done(
                function(){
                    that.app.alert("Reindexing successfully initiated.");
                }) 
        }
    }
    
    onClickCreateBids(event) {
        event.preventDefault();

        this.updateStatus();

        var selected_sessions = this.getSelectedSessions();

        if (selected_sessions.length == 0) {
            alert("Please select some sessions on the Session Selection tab first.");
            return;
        }

        if (!this.validateSeriesMappings()) {
            alert("Please set the Scan Type for each Series Description.");
            return;
        }


        var target_dir = $('#convert_target_dir').val()

        if (!target_dir) {
            alert("Please provide a target directory for the conversion.");
            return;

        }

        this.app.api.convert_to_bids(this.getUserSeriesDescriptions(), selected_sessions, target_dir).done(function(a, b) {console.log("Response from conversion request");});
    
        return false;
    }
    


    
    updateStatus() {
        var sess = this.getSelectedSessions();

        var n_sess = sess.length;
        /*  
          var unique_subjects = {};
          for (var i=0; i< n_sess; i++) {
              unique_subjects[sess[i].subject_id]= true;
          }
          */
        //    var n_subj = Object.keys(unique_subjects).length;

        $('#status_sessions_selected').text(n_sess);

        $('#status_sessions_selected').toggleClass("bg-warning", n_sess == 0);

        $('#convert_target_dir').toggleClass("bg-warning", $('#convert_target_dir').val().length == 0)

        var ok_to_proceed = n_sess > 0 && $('#convert_target_dir').val().length > 0;

        $('#btn_create_bids').attr("disabled", !ok_to_proceed);

    }

    validateSeriesMappings() {
        /*make sure each series description is mapped to a ScanType */
        var is_valid = true;

        var selects = $("#series_descriptions select");

        if (selects.length == 0) {
            return false;
        }
        selects.each(function(i, elem) {

            if (!$(elem).val()) {
                is_valid = false;
                return false;
            }
        })
        return is_valid;
    }

    loadSubjectSearchResults(data) {
        /* Expects data of the form
    
        {
            subjects:[],
            series_descriptions:[]
        }    
        */
        window.bidsGui.startConvertMode();

        $('#loaded_study_dir').text(data.study_dir)

        var subjects_data = data.subjects;

        if (data.not_founds) {
            if (data.not_founds.length > 0) {
                var msg;

                msg = "The following subject id" + (data.not_founds.length == 1 ? " was" : "s were") + " not found: " + data.not_founds.join(",");

                window.bidsGui.alert(msg);
            }

        }
        var tbl = $('#session_choice tbody')

        tbl.empty();

        var subj;

        for (subj in subjects_data) {
            var subject = subjects_data[subj];
            for (var datekey in subject) {

                var display_subjid;

                display_subjid = subj + '<a href="#" class="edit_subjectid">Edit</a>';


                var chk = '<input class="form-check-input" type="checkbox" value="">'

                var session_data = subject[datekey]

                var tr = $(tablerow_from_array([display_subjid, datekey, chk]));

                tr.data('subj_date_path', [subj, datekey, session_data.common_path]);
                
                tbl.append(tr);
            }
        }

        var onClickEdit = function(e) {
            var $t = $(e.currentTarget);

            var $td = $($t.parent());
            $td.append()
            $t.remove();
            var $i = $('<input type="text" class="new_subjectid" placeholder="new Subject Id">');
            $td.append($i);
            $i.focus();

        }
        tbl.find('a.edit_subjectid').click(onClickEdit)
        var that = this;
        
        $('#session_choice tbody tr').click(function(a, b) {

            var $target = $(a.currentTarget);
            that.loadSeriesDetail(...$target.data('subj_date_path'));

            var activeClassName = 'table-primary' // see https://getbootstrap.com/docs/4.0/content/tables/ for more standard options
            $target.siblings().removeClass(activeClassName);
            $target.addClass(activeClassName);


        });

        $('#session_choice input.form-check-input').click(function(a, b) {
            window.bidsGui.convertGui.updateStatus();
        });

        this.displaySeriesDescriptions(data.series_descriptions);

        subjectsToTreeView(subjects_data);

        window.search_result_data = data;

        window.bidsGui.convertGui.updateStatus();
    }
    
    loadSeriesDetail(subject_id, date) {
        var tbody = $('#series_table tbody').empty();

        var session_data = window.search_result_data.subjects[subject_id][date]
        if (session_data) {
            var sorted_series_in_session = [];

            for (var series_key in session_data.series) {
                sorted_series_in_session.push(session_data.series[series_key]);
            }

            sorted_series_in_session.sort(function(a, b) {
                parseInt(b.series) - parseInt(a.series)
            });
            for (var idx in sorted_series_in_session) {
                var series = sorted_series_in_session[idx];

                //series.sort(function(a,b) { parseInt(b.series)-parseInt(a.series)});

                var data = [series.desc, series.time, series.series, series.dcmcount, "(unmapped)"]

                tbody.append(tablerow_from_array(data))
            }

        }

    }
    
    selectModalityString() {
        var selectStr = '<select>';

        var sectionHeadings = Object.keys(modality_labels_by_bids_data_type).sort();

        $.each(sectionHeadings, function(key, dataType) {
            selectStr += '<option value="' + dataType + '" class="dataTypeHeading" disabled>' + dataType + "</option>";
            var modalities = modality_labels_by_bids_data_type[dataType].split(" ");
            modalities.sort()

            $.each(modalities, function(midx, modality) {

                var desc = scan_types_descs[modality] || modality;
                selectStr += '<option value="' + modality + '">' + desc + "</option>";

            })


        })
        $.each(scan_types, function(key, value) {
            selectStr += '<option value="' + value[0] + '">' + value[1] + "</option>";
        });
        selectStr += "</select>";

        return selectStr;
    }
    
    displaySeriesDescriptions(series_descriptions) {

        /*
            var selectStr = '<select><option value=""></option><option value="anat" disabled>anat</option>';

            $.each(scan_types, function(key, value) {
                selectStr += '<option value="' + value[0] + '">' + value[1] + "</option>";
            });
            selectStr += "</select>";
        
            */
        var selectStr = this.selectModalityString();

        var tbody = $('#series_descriptions tbody');

        $.each(series_descriptions, function(i, d) {

            var row = $("<tr><td>" + d.desc + "</td><td>" + selectStr + '</td><td><input type="text" class="custom_tags"></input></td></tr>');

            if (d.modality) {
                row.find('select').val(d.modality);
            }

            tbody.append(row);
        });

    }
    
    
    getUserSeriesDescriptions() {
        var selects = $("#series_descriptions select");

        if (selects.length == 0) {
            return false;
        }

        var series_list = []

        selects.each(function(i, elem) {
            var $e = $(elem);
            var val = $e.val();
            var series = $($e.parent().siblings()[0]).text();
            var custom_tags = $($e.parent().siblings()[1]).children('input.custom_tags').val();
            series_list.push([series, val, custom_tags]);
        });

        var data = {
            "study_dir": $('#loaded_study_dir').text(),
            "SeriesDescriptions": series_list
        }

        return data;

    }
}
