require('../../static/js/data-panel');
const { defer } = require('lodash');

// Form submit polyfill
window.HTMLFormElement.prototype.submit = () => {};

describe('Disable send button on submit', () => {
    let container;
    let button;

    beforeEach(() => {
        container = document.createElement('div');
        container.innerHTML = `<form id='create-message-form'><button id='btn-send-message'>Send</button></form>`;

        document.body.appendChild(container);

        const form = document.getElementById('create-message-form');
        button = document.getElementById('btn-send-message');

        button.addEventListener('submit', event => {
            form.dispatchEvent(new Event('submit'));
            event.preventDefault();
        });
    });

    afterEach(() => {
        container.remove();
    });

    test('unclicked button should be enabled', () => {
        expect(button.attributes.disabled).not.toBe('disabled');
    });

    test('clicked button should be disabled after clicking', (done) => {
        button.click();
        defer(() => {
            expect(button.attributes.disabled).toBe('disabled');
            done();
        });
    });

    test('clicking button second time does not fire button click event', (done) => {
        let count = 0;
        const clickHandler = event => {
            if (event.originalEvent.target.attributes.disabled !== 'disabled') {
                count++;
            }
        };

        button.addEventListener('click', clickHandler);

        button.click();
        defer(() => {
            button.click();
            defer(() => {
                expect(count).toBe(1);
                done();
            });
        });
    });
});
