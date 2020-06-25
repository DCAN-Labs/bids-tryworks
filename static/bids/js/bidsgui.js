var launcher = function() {
    window.bidsGui = new BidsGui();
    window.bidsGui.initUI();

}

$(document).ready(launcher);
