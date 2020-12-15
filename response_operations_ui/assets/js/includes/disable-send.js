(function(window) {
    const createMessageForm = document.getElementById('create-message-form');
    const buttonSendMessage = document.getElementById('btn-send-message');

    if (createMessageForm && buttonSendMessage) {
        createMessageForm.addEventListener('submit', function(event) {
            buttonSendMessage.attributes.disabled = 'disabled';
        });
    }
}(window));

(function(window) {
    const loadSampleForm = document.getElementById('form-load-sample');
    const buttonLoadSample = document.getElementById('btn-load-sample');

    if (loadSampleForm && buttonLoadSample) {
        loadSampleForm.addEventListener('submit', function(event) {
            buttonLoadSample.attributes.disabled = 'disabled';
        });
    }
}(window));