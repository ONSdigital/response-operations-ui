$(document).ready(function() {
  $("#create-message-form").submit(function() {
    $("#btn-send-message").prop("disabled", true);
  });
});
