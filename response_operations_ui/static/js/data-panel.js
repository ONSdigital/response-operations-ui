function openPanel(){

    var panelToOpen = qs['s'];

    if( panelToOpen != ''){
      $('#' + panelToOpen + ' .data-panel-header').addClass('active');
      $('#' + panelToOpen + ' .data-panel-body').css( 'display', 'block' );

      // location.href = '#' + panelToOpen;
    }

}

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


function checkForChange(){

    var whatToChange = qs['change'];

    // this is all very inefficient, but for now...

    if( whatToChange == 'contact'){
      $('#contact-changed').removeClass('hidden');

      var fullName = qs['firstName'] + ' ' + qs['lastName'];
      var currentEmail = qs['currentEmail'];
      var newEmail = qs['email'];
      var tel = qs['tel'];

      $('#rName').html( fullName );
      $('#rEmail').html( currentEmail );
      $('#rTel').html( tel );

      if( currentEmail != newEmail ){

        var dt = new Date();


        $('#contact-changed').html('Verification email sent to ' + newEmail );
        $('#rNewEmail').html( 'Verification email sent<br \/>' + newEmail );
        // $('#rNewEmail').html( 'Verification email sent + ' + dt + '<br \/>' + newEmail );
        $('.newEmail').removeClass('hidden');
      }


    }

    if( whatToChange == 'verification-email-sent'){
      $('#verification-email-sent').removeClass('hidden');
    }

    if( whatToChange == 'response-status'){
      $('#response-status-changed').removeClass('hidden');
      $('#074-201801').html('Completed by phone');
    }

}

$(dataPanels);
$(checkForChange);
$(openPanel);
