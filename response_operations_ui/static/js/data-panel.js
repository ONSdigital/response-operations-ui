function initDataPanels() {
    var acc = document.getElementsByClassName("data-panel-header");
    for (var i = 0; i < acc.length; i++) {
        // Introduce button if js running, so we can focus on each accordion heading
        var panelTitle = acc[i].innerHTML;
        acc[i].innerHTML = "<button class='data-panel-header__title'>" + panelTitle + "<\/button>";
        var panel = acc[i].nextElementSibling;
        panel.style.display = "none";
        // Add event listener to toggle displaying the data panel
        acc[i].addEventListener("click", function() {
            this.classList.toggle("active");
            if (panel.style.display === "block") {
                panel.style.display = "none";
            } else {
                panel.style.display = "block";
            }
        });
    }
}
