//options per the BIDS spec bids_specs1.0.2 pdf
//https://github.com/cbedetti/Dcm2Bids

//from Bids Spec version 1.1.1, section 8.3.2
var scan_types = [
    ["T1w", "T1 weighted"],
    ["T2w", "T2 weighted"],
    ["T1rho", "T1 Rho map"],
    ["T1map", "T1 map"],
    ["T2map", "T2 map"],
    ["T2star", "T2*"],
    ["FLAIR", "FLAIR"],
    ["FLASH", "FLASH"],
    ["PD", "Proton density"],
    ["PDmap", "Proton density map"],
    ["PDT2", "Combined PD/T2"],
    ["inplaneT1", "Inplane T1"],
    ["inplaneT2", "Inplane T2"],
    ["angio", "Angiography"]

];

var scan_types_descs = {
    "T1w": "T1 weighted",
    "T2w": "T2 weighted",
    "T1rho": "T1 Rho map",
    "T1map": "T1 map",
    "T2map": "T2 map",
    "T2star": "T2*",
    "FLAIR": "FLAIR",
    "FLASH": "FLASH",
    "PD": "Proton density",
    "PDmap": "Proton density map",
    "PDT2": "Combined PD/T2",
    "inplaneT1": "Inplane T1",
    "inplaneT2": "Inplane T2",
    "angio": "Angiography"
};
/*
#todo make sure these labels are grabbed from the spec correctly, some are unclear in the appendedx doc, 
#   check:    under fmap is it "magnitudefieldmap" or are "magniture and fieldmap" separate
#               under func is it sbrefevents or sbref and events as separate ones
#                   if events, it is confusing because beh also has events
#                   beh events, stimphysio or stim and physio as separeate ones 
#                   meg last column could be anything 
*/

var modality_labels_by_bids_data_type = {
    "anat": "T1w T2w T1rho T1map T2map T2star FLAIR FLASH PD PDmap PDT2 inplaneT1 inplaneT2 angio defacemask",
    "func": "bold sbref events physio stim",
    "dwi": "dwi bvec bval",
    "fmap": "phasediff phase1 phase2 magnitude1 magnitude2 magnitude fieldmap epi",
    "beh": "events stim physio",
    "meg": "meg channels photo coordsystemheadsshape"
}



var checkIfRowNeedsCustomTags = function($tr) {
    var modality = $tr.descendants('select').val()

}


var tablerow_from_array = function(array_of_values, data_to_store_at_tr_level) {

    var tr = '<tr><td>' + array_of_values.join("</td><td>") + '</td></tr>';

    if (data_to_store_at_tr_level) {
        var tr = $(tr);
        tr.data('rowdata', data_to_store_at_tr_level);
    }
    return tr;
}

var subjectsToTreeView = function(subjects) {
    //convert the subjects key of the search results to the data structure required for bootstrap treeview and 
    //render it is #session_tree

    var nodes = [];
    for (var subj in subjects) {
        var subject = subjects[subj];

        var node = {
            "text": subj,
            "nodes": [],
            "selectable": true,
            icon: "glyphicon glyphicon-stop"
        };

        for (var datekey in subject) {
            var date_data = subject[datekey];
            node.nodes.push({
                "text": datekey,
                "selectable": true,
                icon: "glyphicon glyphicon-stop",
                "subject_id": subj,
                "date": datekey
            });
        }

        nodes.push(node);
    }

    $("#session_tree").treeview({
        data: nodes,
        onNodeSelected: onSessionTreeRowClick
    });

}



var onChangeBidsSeriesSelection = function(e) {
    var series_id_obj = $(e.currentTarget).bidsSeriesId();
    window.laste = e;
    window.activeBidsDataset.toggleSelection(series_id_obj, $(e.currentTarget).is(':checked'));
    window.bidsGui.updateStatus();
}

var onSessionTreeRowClick = function(event, data) {

    var date = data.date

    if (date) {
        var subject_id = data.subject_id;
        if (subject_id) {

            window.bidsGui.convertGui.loadSeriesDetail(subject_id, date);
        }
    }
}
var onStudyClick = function(event, data) {

    var path = data.fullpath;
    window.bidsGui.processingGui.getSavedSelections(path);
}

var onStudyClickPopup = function(event, data) {

    path = data.fullpath;

    $('#convert_target_dir').val(path);

    window.bidsGui.convertGui.updateStatus();

}

var ajaxErrorHandler = function(r) {
    window.bidsGui.displayAjaxError(r);
}
