const better_url = location.origin;
const TARGETURL = better_url + "/api/ProgressIndicator/";

function extractProgress(progress){
    console.log(progress)
}


function getProgress() {
    $.ajax({
        type: "GET",
        url: TARGETURL,
        header: "Access-Control-Allow-Origin",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(jsonData),
        success: function(response) {
            console.log("Success")
            console.log(data)
        },
        error: function(xhr, desc, err) {
            console.log("Error: GET failed." + err)
        }
    })
    if (fail === false){
        reloadAfterFileUpload()
    }
}


function postProgress(jsonData){
    $.ajax({
        type: "POST",
        url: TARGETURL,
        header: "Access-Control-Allow-Origin",
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify(jsonData),
        success: function(response) {
            console.log("POST Success")
        },
        error: function(xhr, desc, err) {
            console.log("Error: POST failed." + err)
        }
    })
    if (fail === false){
        reloadAfterFileUpload()
    }
}

while (true) {
    setTimeout(function() {
        getProgress();
    }, 1000);
    
}