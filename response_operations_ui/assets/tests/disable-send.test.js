const getElementByIdMock = id => {
    switch (id) {
    case 'create-message-form':
        return createMessageFormMock;

    case 'btn-send-message':
        return buttonSendMessageMock;
    }
};

const addEventListenerMock = function(eventName, callback) {
    const titleCaseEventName = eventName.substr(0, 1).toUpperCase() + eventName.substr(1);
    this[`fire${titleCaseEventName}`] = () => {
        const event = new Event(eventName);
        const domEl = document.createElement('div');

        domEl.dispatchEvent(event);
        callback(event);
    };
};

const createMessageFormMock = {
    addEventListener: addEventListenerMock
};

const buttonSendMessageMock = {
    attributes: {
        disabled: undefined
    }
};

document.getElementById = getElementByIdMock;
require('../../static/js/disable-send');

describe('Disable send button on submit', () => {
    test('Button disabled setting is not set before click', () => {
        expect(buttonSendMessageMock.attributes.disabled).toBe(undefined);
    });

    test('it should be disabled after form submits', () => {
        createMessageFormMock.fireSubmit();
        expect(buttonSendMessageMock.attributes.disabled).toBe('disabled');
    });
});