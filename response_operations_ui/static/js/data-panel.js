function initDataPanels() {
    var acc = document.getElementsByClassName("data-panel-header");
    for (var i = 0; i < acc.length; i++) {
        // Introduce button and hide data panel content if js running

        var initPanel = acc[i].nextElementSibling;
        initPanel.style.display = "none";

        // Add event listener to toggle displaying the data panel
        acc[i].addEventListener("click", function() {
            var panel = this.nextElementSibling;
            this.classList.toggle("active");
            if (panel.style.display === "block") {
                panel.style.display = "none";
            } else {
                panel.style.display = "block";
            }
        });

    }
}


function openPanel(){
  var panelToOpen = window.location.hash;
  if( panelToOpen !== ""){
     $( panelToOpen + " .data-panel-header").addClass("active");
     $( panelToOpen + " .data-panel-body").css( "display", "block" );
   }
}