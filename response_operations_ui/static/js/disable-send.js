(function(window) {
    const createMessageForm = document.getElementById('create-message-form');
    const buttonSendMessage = document.getElementById('btn-send-message');

    if (createMessageForm && buttonSendMessage) {
        createMessageForm.addEventListener('submit', function(event) {
            buttonSendMessage.attributes.disabled = 'disabled';
        });
    }
}(window));

