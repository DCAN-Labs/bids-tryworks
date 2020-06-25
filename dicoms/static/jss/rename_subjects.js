// Loading axio's from CDN
var axiosScript = document.createElement('script')
axiosScript.setAttribute('src', 'https://unpkg.com/axios/dist/axios.min.js')
document.head.appendChild(axiosScript)

const better_url = location.origin;
const TARGETURL = better_url + "/api/SubjectsAKA";



function post(jsonData){
    var fail = true
    console.log("Target url ", TARGETURL)
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
            success_response = response;
            fail = false
        },
        error: function(xhr, desc, err) {
            console.log("Error: POST failed." + err)
            fail = true
        }
    })
    if (fail === false){
        console.log('')
    }
}


function renameSelectedSubjects() {
    $("#search_selection :selected").each(function() {
      addRenameInputForSubjectSession(this);
    })
}

function addRenameInputForSubjectSession(subjectSession) {

  // Get subject session's ID and text content
  var subSesID = "rename-" +  subjectSession.id; // subSesID + "-" + sub_ses_txt
  console.log("subjectSession ", subjectSession.innerText.split(' '))
  console.log("subjectSession.innerText " + subjectSession.innerText)
  console.log("HTML SPLIT ON SPACES" + subjectSession.innerText.split(' '))
  var subSesText = subjectSession.innerText.split(' ')
  if (!$("#" + subSesID).length) {

    // Label for row to rename subject session
    var subSesLabel = document.createElement("p");
    subSesLabel.id = subSesID;
    subSesLabel.innerHTML = ("Rename subject "
                             + subSesText[1] + " to: ");

    // Textarea to enter new name
    var newSubSesInput = document.createElement("textarea");
    newSubSesInput.id = subSesID + "-textarea"
    newSubSesInput.value = subSesText[1];
    newSubSesInput.columns = "60";
    newSubSesInput.rows = "1";

    // Cancel button
    var cancelButton = document.createElement("button");
    cancelButton.innerHTML = "Cancel"
    cancelButton.addEventListener("click", function() {
      removeThis(subSesID);
    });

    // Accept button
    var acceptButton = document.createElement("button");
    acceptButton.innerHTML = "Accept";
    acceptButton.addEventListener("click", function() {
      changeName(subjectSession.id);
      removeThis(subSesID);
    })

    // Add new elements to DOM
    var renameDiv = document.getElementById("rename-div");
    console.log(renameDiv);
    subSesLabel.appendChild(newSubSesInput);
    subSesLabel.appendChild(cancelButton);
    subSesLabel.appendChild(acceptButton);
    renameDiv.appendChild(subSesLabel);
  }

  function removeThis(elID) {
    $("#" + elID).remove();
  }

  function changeName(subSesID) {
    var newName = $.trim($("#rename-" + subSesID + "-textarea").val());
    var newText = subjectSession.innerText.split(' ')
    newText[1] = newName
    console.log('newText', newText)
    var newStr = newText.join(' ')
    $("#" + subSesID).html(newStr);

    post({'SubjectID': newText[0],
          'SubjectAKA': newText[1]})
  }
}

function populateDetails(sessionPK) {
  function sesLabel(detail) { 
    return "#session_" + detail + "_label";
  }
  $("#series_table tbody").empty();
  var session = session_series[sessionPK];
  var acquisitionTime;
  var toAdd;
  if (session["Series"].length > 0) {
    for (var i = 0; i < session["Series"].length; i++) {
      acquisitionTime = session["Series"][i]["AcquisitionTime"];
      toAdd = "<tr><td>" + [
          session["Series"][i]["SeriesNumber"],
          session["Series"][i]["SeriesDescription"],
          acquisitionTime === null ? "N/A" : String.valueOf(acquisitionTime),
        ].join("</td><td>") + "</td></tr>";
      $("#series_table tbody").append(toAdd);
    };
  } else {
    $("#series_table tbody").append("No session series data");
  }
  $(sesLabel("path")).html(session["Path"]);
  $(sesLabel("date")).html(session["Date"]);
  $(sesLabel("study")).html()
  $(sesLabel("subject")).html(session["SubjectAKA"] ? session["SubjectAKA"] : session["SubjectID"]);
}