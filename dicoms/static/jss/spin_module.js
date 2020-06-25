import {Spinner} from "./spin.js"

// Display spinny wheel
var opts = {
    lines: 13, // The number of lines to draw
    length: 38, // The length of each line
    width: 17, // The line thickness
    radius: 45, // The radius of the inner circle
    scale: 1, // Scales overall size of the spinner
    corners: 1, // Corner roundness (0..1)
    color: '#000000', // CSS color or array of colors
    fadeColor: 'transparent', // CSS color or array of colors
    speed: 1, // Rounds per second
    rotate: 0, // The rotation offset
    animation: 'spinner-line-fade-quick', // The CSS animation name for the lines
    direction: 1, // 1: clockwise, -1: counterclockwise
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    className: 'spinner', // The CSS class to assign to the spinner
    top: '50%', // Top position relative to parent
    left: '50%', // Left position relative to parent
    shadow: '0 0 1px transparent', // Box-shadow for the lines
    position: 'absolute' // Element positioning
};
function startSpinner() {
    var msg = document.createElement("h1");
    msg.innerHTML = "Conversion in process...";
    document.getElementById("uploader_div").appendChild(msg);
    var target = document.getElementById("spinning-display");
    new Spinner(opts).spin(target);  
}
document.getElementById("generate_form_button").addEventListener("click", startSpinner)

