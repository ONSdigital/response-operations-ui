function dataPanels(){

  var acc = document.getElementsByClassName("data-panel-header");
  var i;

  for (i = 0; i < acc.length; i++) {

    // Introduce button if js running, so we can focus on each accordion heading
    var panelTitle = acc[i].innerHTML;
    acc[i].innerHTML = '<button class="data-panel-header__title">' + panelTitle + '<\/button>';

    acc[i].addEventListener("click", function() {
      /* Toggle between adding and removing the "active" class,
      to highlight the button that controls the panel */
      this.classList.toggle("active");

      /* Toggle between hiding and showing the active panel */
      var panel = this.nextElementSibling;
      if (panel.style.display === "block") {
        panel.style.display = "none";
      } else {
        panel.style.display = "block";
      }
    });
  }

}
