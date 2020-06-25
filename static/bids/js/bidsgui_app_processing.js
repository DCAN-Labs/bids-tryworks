
class ProcessingGUI {
    constructor(app) {
        this.app = app;
    }
    
    initUI() {
        var that = this;
        $("#menu_open_bids").click(function() {
            var ok = confirm("Are you sure you want to open a new BIDS Dataset?  Your unsaved selection choices will be lost.");

            if (ok) {
                that.app.startLaunchScreen(2);
                bidsGui.loadStudies();
            }

        })

        $('#menu_save_selections').click(function() {
            window.bidsGui.processingGui.saveSelections();
        });

        $('#menu_save_selections_as').click(function() {
            window.bidsGui.processingGui.saveSelections(true);

        });
        
        if (window.available_bidsapps) {
            this.available_bidsapps = window.available_bidsapps;
            var data = []
            var $select = $('#bidsapp');
            
            $.each(this.available_bidsapps, function(idx,app) {
                $select.append($("<option></option>")
                    .attr("value", app.name)
                    .text(app.name)); 
            });
            $select.change(function(e){
                var $target = $(e.currentTarget);
                
                var appName = $target.val();
                
                that.displayAppOptions(appName);
                
                that.updateLaunchCommand();
            })
        }
        $("#bids_job_name,#bids_running_machine_working_directory,#bidsapp_options_heading_advanced_card input, #bidsapp_options_heading_advanced_card textarea, #generated_command_template").change(
            this.updateLaunchCommand
        ).keyup(this.updateLaunchCommand);
        
        var path_join = function(p1,p2) {
            var p = p1 + "/" + p2;
            return p.replace(/\/\//g, '/');
        }
        var DATASETPATH_updater = function() {
                var p = path_join($('#bids_running_machine_working_directory').val(),
                    $('#bids_job_name').val());
                
                p = p.replace(/\/\//g, '/')
                var bids_input = path_join(p, "input")
                var bids_output =  path_join(p, "output")
                
                $('#DATASETPATH').text(bids_input);
                $('#OUTPUTPATH').text(bids_output);
                
            };
            $("#bids_running_machine_working_directory, #bids_job_name").change(DATASETPATH_updater).keyup(DATASETPATH_updater);
            
            
            $('#btn_launch_bids').click(function() {that.launchProcessingJob()});
            

    }

    launchProcessingJob() {

        var payload =this.constructSaveData();

        if (payload) {
            this.app.api.launch_processing_job(payload).done(function(data) {console.log(data);});
        }

    }
    
    saveInputsToLocalStorage() {
        
        var flds_to_save = [
            "#bids_job_name",
            "#launch_ssh_user",
            "#launch_ssh_host",
            "#bids_running_machine_working_directory"            
        ];
        
        var saver = this.app.saveInputToLocalStorage;
        
        $.each(flds_to_save, function(idx,item){
            saver(item);
        });
    }
    
    loadInputsFromLocalStorage() {
        var flds_to_save = [
            "#bids_job_name",
            "#launch_ssh_user",
            "#launch_ssh_host",
            "#bids_running_machine_working_directory"            
        ];
        
        var loader = this.app.fillEmptyInputFromLocalStorage;
        
        $.each(flds_to_save, function(idx,item){
            loader(item);
        });
    }
    constructSaveData(save_as_new_name) {
        var default_name = "";
        var name = $('#bids_job_name').val();

        if (!name) {
            if (this.saved_selections && this.saved_selections.name) {
                name = this.saved_selections.name;
            };
        }

        if (save_as_new_name || !name) {
            
            name = $('#bids_job_name').val();
            
            if (!name) {
                name = prompt("Please provide a name for this Processing Configuration", name);
                if (name) {
                    $('#bids_job_name').val(name);
                }
            }

        }
        this.saveInputsToLocalStorage();
        
        if (name) {
            var series = window.activeBidsDataset.getAllSelectedSeries();

            var paths = [];

            for (var i in series) {
                paths.push(series[i].json_path);
            }

            var payload = {
                "name": name,
                "sidecars": paths
            };
            var pwd = $('#ssh_password').val()
            if (pwd) {
                payload["ssh_password"] = this.app.encryptor(pwd);
                
            }
            payload["ssh_user"] = $('#launch_ssh_user').val();
            payload["ssh_host"] = $('#launch_ssh_host').val();
            payload["ssh_working_dir"] = $('#bids_running_machine_working_directory').val();
            payload["generated_command_batch"] = $('#generated_command_batch').val();
            return payload;            
        }
    }

    saveSelections(save_as_new_name) {
        var payload = this.constructSaveData(save_as_new_name);
        if (payload) {
            window.api.saveSelections(payload).done(function(r) {
                //save successful
            });
        }
    }

    renderBIDSDataResponse(data) {

        this.saved_selections = data.saved_selections;

        this.loadBidsSubjects(data.subjects, data.saved_selections);

        this.renderSelectionFilterChoices();
    }

    renderSelectionFilterChoices() {
        var choices = window.activeBidsDataset.getAvailableSelectionFilters();

        var enforcement = 'only select if #<input type="text" class="enforce_count"> match a session (blank will match any)';
        enforcement = ""; //just disabling until that funcionality is missing         
        var btn = '<button class="select_all">Select All</button><button class="deselect_all">Unselect All</button>';

        var rows = $.map(choices, function(a) {
            //todo implement enforcement logic return tablerow_from_array([a,enforcement,btn] ,{"filter":a} );
            enforcement = ""; //just disabling until that funcionality is missing 
            return tablerow_from_array([a, enforcement, btn], {
                "filter": a
            });
        });

        $('#filter_selection tbody').append(rows);

        var filterFactory = function(true_or_false) {
            return function(a, b) {
                var $t = $(a.currentTarget);

                var tr = $t.parents('tr')[0];

                var filter_text = $(tr).data('rowdata').filter;

                if (filter_text) {
                    var result = window.activeBidsDataset.toggleSelectionByMappingRule(filter_text, true_or_false);
                    window.bidsGui.refresh();
                    alert(result.matching + " images matched the condition. " + result.changed + " were changed by this action.");
                }

            }

        }

        $('#filter_selection button.select_all').click(filterFactory(true));
        $('#filter_selection button.deselect_all').click(filterFactory(false));
    }

    loadStudy(path, selection_file_path) {

        var request_data = {
            "dataset_dir": path
        };

        if (selection_file_path && selection_file_path != "New Selection") {
            request_data["selection_file_path"] = selection_file_path;
        }

        var that = this;
        window.bidsGui.api.loadBidsDataset(request_data).done(
            function(data) {
                window.bidsGui.startProcessingMode();
                that.renderBIDSDataResponse(data);
            });
        

        
    }
    
    loadBidsSubjects (data, saved_selections) {
        /* Expects data of the form
    
        {
            subjects:[],
            series_descriptions:[]
        } 
    
        saved_selections is optional   
        */

        var bidsds = new BidsDataset(data);
        window.activeBidsDataset = bidsds;

        if (saved_selections && saved_selections.sidecars) {
            var matching = bidsds.selectBySidecarPath(saved_selections.sidecars);

            var msg = matching.match_count + " image" + (matching.mismatches.length == 1 ? '' : 's') + " selected from saved configuration.";

            if (matching.mismatches && matching.mismatches.length > 0) {
                msg = msg + "<br/>" + matching.mismatches.length + " saved selection" + (matching.mismatches.length > 1 ? 's' : '') + " could not be found in the current dataset."
            }

            window.bidsGui.alert(msg);
        }

        if (saved_selections && saved_selections.name) {
            $('#bids_job_name').val(saved_selections.name);
        }
        var subjects_data = data;

        window.bids_data = data;

        var tbl = $('#bids_session_choice tbody');

        tbl.empty();

        var subj;
        var last_subj_id = ""
        for (subj in subjects_data) {
            var subject = subjects_data[subj];
            for (var datekey in subject.sessions) {

                var display_subjid;
                if (subj == last_subj_id) {
                    display_subjid = "";
                } else {
                    display_subjid = subj;
                }

                var img_count_span = '<span class="session_image_count">0</span>';

                var session_data = subject.sessions[datekey];

                var tr = $(tablerow_from_array([display_subjid, datekey, img_count_span]));

                tr.data('subj_date_path', [subj, datekey, session_data.common_path])
                tbl.append(tr);
            }
        }
        tbl.find('.bids_session_cb').change(function(a, b) {

            }

        )
        $('#bids_session_choice tbody tr').click(function(a, b) {


            var $target = $(a.currentTarget);

            window.bidsGui.loadSeriesDetailBids(...$target.data('subj_date_path'));

            var activeClassName = 'table-primary' // see https://getbootstrap.com/docs/4.0/content/tables/ for more standard options
            $target.siblings().removeClass(activeClassName);
            $target.addClass(activeClassName);


        });
                

        window.bidsGui.updateStatus();
    }
    
    renderAppParams(table_selector, template_string) {
        var $tbody = $(table_selector);
        
        var param_finder = /{{([^}]+)}}/g
        var params = {};

        
        do {
            var m = param_finder.exec(template_string);
            
            if (m) {
                var param_name = m[1];
                if (param_name != "SUBJECTID" && param_name != "DATASETPATH" && param_name != "OUTPUTPATH") {
                    params[m[1]]=true;
                }
            }
        } while (m)
        $.each(params, function(param) {
            $tbody.append('<tr class="extra_param_row"><td class="app_param_name">' + param + '</td><td><input class="app_param_value" type="text></td></tr>"');
        });
        
//        $tbody.find('input').change(this.updateLaunchCommand).keyup(this.updateLaunchCommand);
        
    }
    
    displayAppOptions(appName) {
        this.currentBidsApp = null;
        var bidsapp = this.available_bidsapps[appName];

        var that = this; 
        
        $.each(this.available_bidsapps, function(idx, appObject) {
            if (appObject.name == appName) {
                bidsapp = appObject;
                return false;
            }
        });
        
        if (bidsapp) {
            this.currentBidsApp = bidsapp
            $('#bids_app_prefix').val(bidsapp.prefix);
            
            var docs_url = this.currentBidsApp.docs || "";
            $('#bids_app_docs').attr('href',docs_url).text(bidsapp.name + " Documentation");
            
            $('#docker_image_name').text(bidsapp.image);
            
            $('#docker_args').val(bidsapp.docker_args);
            
            $('#image_args').val(bidsapp.image_args);
            

            var cmd = bidsapp.command || "";
            
            $('#bids_app_params_table tr.extra_param_row').remove();
            
            this.renderAppParams('#bids_app_params_table tbody', bidsapp.docker_args);
            this.renderAppParams('#bids_app_params_table tbody', bidsapp.image_args);
            
            $('#bids_app_params_table tr.extra_param_row').change(this.updateLaunchCommand).keyup(this.updateLaunchCommand);
        }
        
    }
    
    substituteAppLaunchParams(orig_string, values) {
        for (var k in values) {
            var re = new RegExp("{{"+k+"}}", "g");
            orig_string = orig_string.replace(re, values[k]);
        }
        return orig_string;
    }
    
    updateLaunchCommand() {
        
        var new_command_template = "";
        var command_batch = ""
        
        var $param_values = $('#bids_action_panel input');
        
        var values = {}
        $.each($param_values, function(idx, fld) {
            var $fld = $(fld);

            var $row = $($fld.parents('tr')[0]);
            var fldname = $row.find('td.app_param_name').text();
            values[fldname] = $fld.val()

        })
        
        values["DATASETPATH"] = $('#DATASETPATH').text();
        values["OUTPUTPATH"] = $('#OUTPUTPATH').text();
        
        
        var prefix = $('#bids_app_prefix').val();
        
        if (prefix) {
            prefix = prefix + " ";
        }
        var currentApp = bidsGui.processingGui.currentBidsApp;
        
        if (currentApp) {
            
            var docker_args = $('#docker_args').val();
            var image_args = $('#image_args').val(); 
            
            new_command_template = prefix + "docker run " + docker_args + " " + currentApp.image + " " + image_args;
            
            new_command_template = bidsGui.processingGui.substituteAppLaunchParams(new_command_template, values);
        }

        $('#generated_command_template').val(new_command_template);
        
        if (window.activeBidsDataset) {
            var subject_ids = window.activeBidsDataset.getAllSelectedSubjectIds();
        
            for (var i in subject_ids) {
                var s_id = "sub-" + subject_ids[i];
            
                command_batch += new_command_template.replace(/{{SUBJECTID}}/g, s_id) + "\n\n";
            }
        
            $('#generated_command_batch').val(command_batch);
        }
        
    }
    

    getSavedSelections(path) {
        
        bidsGui.api.getSavedSelections(path).done(
            
            function(data) {

                    var $ul = $('#choose_selection_file');
                    $ul.empty()

                    $ul.append('<li><a href="#">New Selection</a></li>');

                    if (data.files) {

                        $.each(data.files, function(idx, path) {
                            $ul.append('<li><a href="#">' + path + '</a></li>');
                        })
                    }

                    $ul.data('path', data.path);

                    $ul.find('li a').click(function(a) {
                        a.preventDefault();
                        var $target = $(a.currentTarget);
                        var selection_file_path = $target.text();
                        var study_dir = $($target.parents('ul')[0]).data('path');
                        if (selection_file_path && study_dir) {
                            window.bidsGui.processingGui.loadStudy(study_dir, selection_file_path)
                        }
                        return false;
                    })
                }
        )
    }
}
