window.onload = function() {
    const ciCheckBoxes = document.querySelectorAll("input[type=checkbox]");
    const totalCIAvail =
        document.querySelectorAll("input[type=checkbox]").length;
    let totalCIChecked = 0;
    
    document.getElementById('select-or-unselect-ci').onclick = function () {
        if (document.getElementById('select-or-unselect-ci').innerText === "Unselect all") {
            document.getElementById("ci-checked-count").innerHTML = totalCIAvail + " selected out of " + totalCIAvail + " available";
        } else {
            document.getElementById("ci-checked-count").innerHTML = 0 + " selected out of " + totalCIAvail + " available";
        }
    };
    
    [].forEach.call(ciCheckBoxes, function (ci) {
        ci.addEventListener("change", function () {
            totalCIChecked = document.querySelectorAll("input[type=checkbox]:checked").length;
            document.getElementById("ci-checked-count").innerHTML = totalCIChecked + " selected out of " + totalCIAvail + " available";
        });
    });
};



