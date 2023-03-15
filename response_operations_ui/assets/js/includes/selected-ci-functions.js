window.onload = function () {
    const ciCheckBoxes = document.querySelectorAll("input[type=checkbox]");
    const selectButton = document.getElementById('select-or-unselect-ci');
    
    selectButton.onclick = function (ev) {
        if (selectButton.innerText === "Unselect all") {
            ciSelection(false, ciCheckBoxes, ev)
        } else {
            ciSelection(true, ciCheckBoxes, ev)
        }
    };
    
    [].forEach.call(ciCheckBoxes, function (ci) {
        ci.addEventListener("change", function () {
            ciTextUpdates()
        });
    });
}

function ciSelection (selected, ciCheckBoxes, ev) {
    let i;
    for (i = 0; i < ciCheckBoxes.length; i++) {
        ciCheckBoxes[i].checked = selected;
        ev.preventDefault();
    }
    ciTextUpdates()
}

function ciTextUpdates() {
    const totalCIAvail = document.querySelectorAll("input[type=checkbox]").length;
    let totalCIChecked = document.querySelectorAll("input[type=checkbox]:checked").length;

    document.getElementById("ci-checked-count").innerHTML = totalCIChecked + " selected out of " + totalCIAvail + " available";

    if (totalCIAvail > totalCIChecked) {
        document.getElementById('selection-text').innerText = "Select all";
    } else {
        document.getElementById('selection-text').innerText = "Unselect all";
    }
}
