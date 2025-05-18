let params = new URLSearchParams(window.location.search);
let default_tab = params.get('tab');
if (default_tab == "monthly" || default_tab == "weekly") {
    document.getElementById(default_tab + "btn").click();
} else {
    document.getElementById("alltimebtn").click();
}

function opentab(evt, tab_id) {
    let tabcontent = document.getElementsByClassName('tabcontent');
    for (let i = 0; i < tabcontent.length; i++) {
        let cnt = tabcontent[i];
        cnt.style.display = "none";
    }
    let tabbtns = document.getElementsByClassName('tabbtn');
    for (let i = 0; i < tabbtns.length; i++) {
        let btn = tabbtns[i];
        btn.className = btn.className.replace(" active", "");
    }
    let curr_tab = document.getElementById(tab_id);
    window.history.replaceState(null, null, "?tab=" + curr_tab.id);
    curr_tab.style.display = "block";
    evt.currentTarget.className += " active";
}
