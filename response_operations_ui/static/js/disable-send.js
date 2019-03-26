(function(window) {
    document.getElementById('create-message-form').addEventListener('submit', function(event) {
        document.getElementById('btn-send-message').attributes.disabled = 'disabled';
    });
}(window));

