require('../../static/js/data-panel');
const { clickElement } = require('./test-utils');

describe('Data panel tests', () => {
    let dataPanelContainer;
    let dataPanelHeader;
    const dataPanelMarkup = `
    <div class="data-panel" id="survey">
        <h3 class="data-panel-header">
            <button class='data-panel-header__title'></button>
        </h3>

        <div class="data-panel-body">
            <p>Some content</p>
        </div>
    </div>
    `;

    beforeEach(() => {
        dataPanelContainer = document.createElement('div');
        dataPanelContainer.id = 'dataPanelContainer';
        dataPanelContainer.innerHTML = dataPanelMarkup;
        document.body.append(dataPanelContainer);

        dataPanelHeader = document.querySelector('.data-panel-header');
        dataPanelBody = document.querySelector('.data-panel-body');
    });

    afterEach(() => {
        dataPanelContainer.remove();
    });

    describe('Behaviour without panels initialised', () => {
        test('Contents of panels is visible', () => {
            expect(dataPanelBody.style.display).toBe('');
        });

        test('Content visible after clicking panel toggle', () => {
            clickElement(dataPanelHeader);
            expect(dataPanelBody.style.display).toBe('');
        });
    });

    describe('Behaviour with panels initialised', () => {
        beforeEach(() => {
            initDataPanels();
        });

        test('Panels initialise with content hidden', () => {
            expect(dataPanelBody.style.display).toBe('none');
        });

        test('Clicking panel toggle first time shows panel contents', () => {
            clickElement(dataPanelHeader);
            expect(dataPanelBody.style.display).toBe('block');
        });

        test('Clicking panel contents twice hides panel contents', () => {
            clickElement(dataPanelHeader);
            clickElement(dataPanelHeader);
            expect(dataPanelBody.style.display).toBe('none');
        });
    });
});
