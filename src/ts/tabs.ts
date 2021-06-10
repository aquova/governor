let hash = window.location.hash.substr(1)
if (hash == "monthly" || hash == "alltime") {
    document.getElementById(hash + "btn").click()
} else {
    document.getElementById("default").click()
}

function opentab(evt, tab_id) {
    let tabcontent = document.getElementsByClassName('tabcontent')
    for (let i = 0; i < tabcontent.length; i++) {
        let cnt = tabcontent[i] as HTMLElement
        cnt.style.display = "none"
    }

    let tabbtns = document.getElementsByClassName('tabbtn')
    for (let i = 0; i < tabbtns.length; i++) {
        let btn = tabbtns[i] as HTMLElement
        btn.className = btn.className.replace(" active", "")
    }

    let curr_tab = document.getElementById(tab_id)
    window.location.hash = curr_tab.id
    curr_tab.style.display = "block"
    evt.currentTarget.className += " active"
}
