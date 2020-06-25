class BidsGui {
    constructor() {
        this.processingGui = new ProcessingGUI(this);
        this.convertGui = new ConvertGui(this);
        this.api = new BidsAPI(ajaxErrorHandler);
        window.api = this.api;
    }
    
    login(e) {
        e.preventDefault();
        var p = $('#passcode').val();
        if (!p) {
            alert("Enter the passcode");
            return;
        }
        
        this.generateEncryptor(p)
        
        var encryptedPasscode = this.encryptor(p);
        
        var that = this;
        this.api.login(encryptedPasscode).done(function() {
            $("#login").remove();
            that.alert("Login successful");
        }
        );        
    }


    generateEncryptor(key) { 
        this.encryptor = function encrypt(msg) {
        var encrypted_msg = CryptoJS.AES.encrypt(msg, key); 
        return encrypted_msg.toString();
        } 
    }
        
        
    alert(msg, danger) {

        var serverity_class = danger ? "alert-danger" : "alert-warning"
            /* post a warning at the top of the screen (under the header) */
        
        var dismiss_btn = '  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'

        $('#top_nav').after('<div class="alert ' + serverity_class + '" role="alert">' + msg + dismiss_btn + '</div>');

    }

    displayAjaxError(d) {
        
        var t = d.responseText;
        
        var lines = t.split("\n");
        
        var display;
        if (lines.length>2) {
            display = lines[0] + "\n" + lines[1];
            console.log(t);
        } else {
            display = t
        }
        this.alert('Problem with the request. <p>' + display + '</p>', true);
    }
    updateStatus() {
        var count = window.activeBidsDataset.getAllSelectedSeries().length;
        $('#bids_status_series_selected').text(count);

        var countsBySession = window.activeBidsDataset.getSelectedCountsBySession();

        $('#bids_session_choice tbody tr').each(function(idx, row) {
            var $row = $(row)
            var data = $row.data();

            var ids = data.subj_date_path;
            var selected_count = countsBySession[ids[0]][ids[1]];

            $row.find("span.session_image_count").text(selected_count)

        })
    }

    updateSubtitle(t) {
        $('#sub_title').text(t);
    }
    startConvertMode() {

        this.updateSubtitle("DICOM Conversion");
        $('#launchpanel').hide();
        $('#bids_dataset_panel').hide();
        $('#study_detail').show();
        this.mode = "dicom"
    }

    startProcessingMode() {
        this.updateSubtitle("Processing Mode");
        $("#select_study").hide();
        $("#launchpanel").hide();
        $('#study_detail').hide();
        $('#bids_dataset_panel').show();
        this.mode = "bids"
    }

    startLaunchScreen(selectTabNumber) {
        $('#study_detail').hide();
        $('#bids_dataset_panel').hide();
        $("#launchpanel").show();
        $("#select_study").show();
        if (selectTabNumber) {
            $('#launcher_tabs li:nth-child(' + selectTabNumber + ') a').tab('show');
        }
    }

    loadStudiesCallback(a) {

        $('#studies').treeview({
            data: a,
            onNodeSelected: onStudyClick
        });

        $('#popup_studies').treeview({
            data: a,
            onNodeSelected: onStudyClickPopup
        });
    }

    loadStudies() {
        this.api.loadStudies().done(this.loadStudiesCallback);
    }

    initUI() {
        
        this.processingGui.initUI();
        this.convertGui.initUI();
        
        var that = this;

        this.loadStudies();

        $('#login_form').submit(function(e){that.login(e);return false;});
        
        var bidsapps = ["Fair Lab Pipeline","app2","app1"];
        var groups = ["d","e","f"];
        var roisets = ["g","h","i"];
        var epireps = ["j","k","l"];
        
        $('#check_all').click(function(e) {
            $('#session_choice input[type="checkbox"]').prop("checked", true);
            that.convertGui.updateStatus();
        })

        $('#uncheck_all').click(function(e) {
            $('#session_choice input[type="checkbox"]').prop("checked", false);
            that.convertGui.updateStatus();

        })

        $('#search').submit(function(e) {
            e.preventDefault();

            var frm = $('#search');

            var subject_ids = frm.find("textarea[name='subject_ids']").val();
            if (subject_ids.length>0) {
                var data = {
                    "subject_ids": subject_ids
                };
            }
            
            window.api.search_dicoms_by_subject_ids(subject_ids).done(
                function(data){
                    that.convertGui.loadSubjectSearchResults(data)
                });
        });

        $.fn.bidsSeriesId = function(target) {
            var data = this.parents('tr').first().data().rowdata;
            return {
                "subject_id": data.subject_id,
                "session_date": data.session_date,
                "SeriesNumber": data.SeriesNumber,
                "SeriesDescription": data.SeriesDescription
            }
        }

        $('[data-toggle="tooltip"]').tooltip();

        /*
        if (window.localStorage) {
            var last_search = window.localStorage.getItem("last_search_subject_ids");
            if (last_search) {
                var $fld = $('#new_subject_ids');
                if (!$fld.text()) {
                    $fld.text(last_search);
                }
            }
        }
        */
        this.processingGui.loadInputsFromLocalStorage();
        
        this.processingGui.updateLaunchCommand();
    }

    fillEmptyInputFromLocalStorage(dom_id) {
        if (window.localStorage) {
            var val = window.localStorage.getItem(dom_id);
            
            var $input = $(dom_id)
            if (val && !$input.val()) {
                $input.val(val);
            }
        }        
    }
    
    saveInputToLocalStorage(dom_id) {
        if (window.localStorage) {
            window.localStorage.setItem(dom_id, $(dom_id).val());
        }
    }

    refresh() {
        /*
        refresh UI state to display current data state based on the last rendering action that had occurred
        */
        var a = this.lastRenderAction;
        if (a) {
            if (a.mode == this.mode) {
                if (a.action == "loadSeriesDetailBids") {
                    this.loadSeriesDetailBids(a.subject_id, a.date)
                }
            }
        }
        this.updateStatus();
    }
    loadSeriesDetailBids(subject_id, date) {

        var that = this;

        this.lastRenderAction = {
            "mode": this.mode,
            "action": "loadSeriesDetailBids",
            "subject_id": subject_id,
            "date": date
        }

        var tbody = $('#bids_series_table tbody').empty();

        var session_data = window.activeBidsDataset.getSeries(subject_id, date);

        if (session_data) {
            var sorted_series_in_session = [];

            for (var series_key in session_data) {
                sorted_series_in_session.push(session_data[series_key]);
            }

            var justFileName = function(path) {
                var parts = path.split("/");
                return parts[parts.length-1];
                
            }
            sorted_series_in_session.sort(function(a, b) {
                
                var a_file = justFileName(a.json_path);
                var b_file = justFileName(b.json_path)
                if (a_file > b_file) {
                     return 1;
                 } else if (a_file < b_file) {
                     return -1;
                 }
                 return 0;
            });

            var chkbox_off = '<input class="series_select_cb" type="checkbox">';
            var chkbox_on = '<input class="series_select_cb" type="checkbox" checked>';
            var btns = '<a href="#" class="preview_sidecar button">Sidecar</a><a  href="#" class="preview_image">Image</a>';
            for (var idx in sorted_series_in_session) {
                var series = sorted_series_in_session[idx];

                //series.sort(function(a,b) { parseInt(b.series)-parseInt(a.series)});

                var sidecar_path_parts = series.json_path.split("/")
                var sidecar_name = sidecar_path_parts[sidecar_path_parts.length - 1];
                var chkbox;

                if (series.selected) {
                    chkbox = chkbox_on;
                } else {
                    chkbox = chkbox_off;
                }
                var data = [chkbox, sidecar_name, series.shape, btns]
                    /*
            
                eries
                {SeriesDescription: "ABCD-fMRI-FM-AP_SIEMENS_original_(baseline_year_1_arm_1)",
                 SeriesNumber: 21, ProtocolName: "ABCD_fMRI_DistortionMap_AP"
                , json_path: "/studies/BIDSDIREXAMPLE/sub-NDARINV3F6NJ6WW/ses-20…b-NDARINV3F6NJ6WW_ses-20170312_run-02_phase2.json"}
    */

                //store in each row enough info to map it uniquely to the underlying data. 
                var dataToStash = Object.assign({
                    "subject_id": subject_id,
                    "session_date": date
                }, series)
                tbody.append(tablerow_from_array(data, dataToStash));
            }

            tbody.find('.series_select_cb').change(onChangeBidsSeriesSelection);

            tbody.find('.preview_sidecar').click(function(e) {
                e.preventDefault();
                var $t = $(e.currentTarget);
                var $tr = $($t.parents('tr')[0]);

                var data = $tr.data('rowdata');
                if (data && data.json_path) {
                    that.previewSidecar(data.json_path);
                }
                return false;
            })

        }
    }

    previewSidecar(json_path) {
        api.getSidecarPreview(json_path).done(function(data) {

            var $modal = $('#sidecar_preview_modal');
            $modal.find('span.previewing_sidecar_path').text(json_path);
            $modal.find('textarea').text(data);
            $modal.modal();

            var $table = $modal.find('table.sidecar_table tbody');

            $table.empty();

            var values = JSON.parse(data);

            var sorted_keys = Object.keys(values).sort();

            var rowForKeyValue = function(key, value) {
                return '<tr><th scope="row">' + key + ':<td><span class="preview_value">' + value + '</span><a href="#" class="edit_preview_value">Edit</a></td></tr>';
            }

            $.each(sorted_keys, function(i, k) {
                $table.append(rowForKeyValue(k, values[k]));
            });

            var enterEditValueMode = function($t) {
                /*create the input box and cancel/save buttons and logic to 
                save value change if and only if user hits save after the value edit.
                */
                var $td = $($t.parent());
                var $i = $('<input type="text" class="edit_preview_newvalue">');
                var $b = $('<button class="save_preview_newvalue">Save</btn>');
                var $bc = $('<button class="cancel_preview_newvalue">Cancel</btn>');
                var $curValue = $td.find('span.preview_value');
                var curValue = $curValue.text();

                $i.val(curValue);

                $td.append($i)
                $td.append($b)
                $td.append($bc)

                var removeAll = function() {
                    $i.remove();
                    $b.remove()
                    $bc.remove();
                }
                $bc.click(function() {
                    removeAll();
                })

                $b.click(function(e) {
                    //save
                    $curValue.text($i.val());
                    var key = $($td.siblings()[0]).text();
                    key = key.substring(0, key.length - 1);
                    window.api.postSidecarUpdate(json_path, key, $i.val())
                    removeAll();
                })

            }
            var onClickEdit = function(e) {
                var $t = $(e.currentTarget);

                enterEditValueMode($t);
            }
            $table.find('a.edit_preview_value').click(onClickEdit)

            $("#add_preview_key").off("click").click(function() {
                var new_key = prompt("What is the name of the new key to add to the sidecar json?")
                if (new_key) {
                    var $new_row = $(rowForKeyValue(new_key, ""));

                    $table.append($new_row);

                    var $t = $($new_row.find('a.edit_preview_value')[0]);
                    enterEditValueMode($t);
                    $new_row.find("input.edit_preview_newvalue").focus();
                    $new_row.find('a.edit_preview_value').click(onClickEdit);
                }
            });

        });
    }
}
