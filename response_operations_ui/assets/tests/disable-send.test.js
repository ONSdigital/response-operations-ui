const getElementByIdMock = id => {
    switch (id) {
    case 'create-message-form':
        return createMessageFormMock;

    case 'btn-send-message':
        return buttonSendMessageMock;
    }
};

const addEventListenerMock = (eventName, callback) => {
    this[`fire${eventName.toTitleCase()}`] = () => {
        const event = new Event(eventName);
        callback(event.fire());
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
        createMessageFormMock.addEventListener.fireSubmit();
        expect(buttonSendMessageMock.attributes.disabled).toBe('disabled');
    });
});
