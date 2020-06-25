const better_url = location.origin;
const TARGETURL = better_url + "/api/";



function on_load() {
    // Set event listeners to retrieve file information after upload
    document.getElementById('input-file').addEventListener('change', getFile);
    document.getElementById('upload_config_pk').addEventListener('change', flipBooleans);
}


function flipBooleans() {    
    console.log($("#upload_config_pk").val())
    if ($("#upload_config_pk").val() === null) {
        $("#use_uploaded_boolean").val("False");
    } else {
        $("#use_uploaded_boolean").val("True");
    }
}


function postTextToDB() {
    var fail = true
    textToPost = document.getElementById('content-target').value;
    fileName = document.getElementById('input-file').value;
    if (textToPost === "") {
        setStatusTo("Please enter text or upload a file before clicking POST.")
    } else {
        console.log("Text to post: " + textToPost);
        var jsonData = {"data": textToPost, "filename": fileName};
        $.ajax({
            type: "POST",
            url: TARGETURL,
            header: "Access-Control-Allow-Origin",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify(jsonData),
            success: function(response) {
                console.log(JSON.stringify(jsonData));
                console.log("POST successful. Response:" + response);
                setStatusTo("POST successful.")
                success_response = response;
                fail = false
                let identifier = getUploadedConfigPk(response);
                $("#upload_config_pk").val(identifier);

                $(".boolean").val(identifier);
                hideConversionSelectorAndBuilder();
            },
            error: function(xhr, desc, err) {
                console.log("Error: POST failed." + err)
                setStatusTo("Error: POST failed." + err)
                fail = true
            }
        })
        if (fail === false){
            reloadAfterFileUpload()
        }
    }
}

function hideConversionSelectorAndBuilder(){
    /* Hides the conversion builder and previously used
    conversion selection html if user uploads a dcm2bids json
    */
    $(".select_conversion_file").hide()
    $(".build_conversion_file").hide()
    $(".make_new_checkbox").hide()
}

function getUploadedConfigPk(response_object){
    let result;
    $.each(response_object, function(index, value) {
        if (index == "uploaded_config_pk") {
            result = value;
        }
    })
    return result;
    /*var pk = response_object.upload_config_pk;
    console.log(Object.keys(response_object))
    console.log(response_object.constructor.name)
    let x = JSON.parse(JSON.stringify(response_object))
    console.log(x)
    let y = JSON.stringify(x.upload_config_pk)
    console.log(y)
    var = jsonObj = Ext.decode(response_object)
    $("#upload_config_pk").val(pk)
    return response_object
    */
}

function setStatusTo(msg) {
    document.getElementById("status").innerHTML = msg;
}


function getFile(event) {
    const input = event.target;
    if ('files' in input && input.files.length > 0) {
        placeFileContent(
            document.getElementById('content-target'),
            input.files[0]
        );
    }
}

function placeFileContent(target, file) {
    readFileContent(file).then(content => {
        target.value = content;
    }).catch(error => console.log(error));
}

function readFileContent(file) {
    const reader = new FileReader();
    return new Promise((resolve, reject) => {
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file);
    })
}

function reloadAfterFileUpload() {
    location.reload()
}