document.getElementById("default").click()

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

    document.getElementById(tab_id).style.display = "block"
    evt.currentTarget.className += " active"
}
