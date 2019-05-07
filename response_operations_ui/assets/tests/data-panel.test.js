require('../../static/js/data-panel');

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
    </div>`;

    const defer = fn => setTimeout(fn, 0);

    beforeAll(() => {
        jest.useRealTimers();
    });

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
            dataPanelHeader.click();
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
            dataPanelBody.click();
            defer(() => {
                expect(dataPanelBody.style.display).toBe('block');
            });
        });

        test('Clicking panel contents twice hides panel contents', (done) => {
            dataPanelBody.click();
            defer(() => {
                dataPanelBody.click();
                expect(dataPanelBody.style.display).toBe('block');
                defer(() => {
                    expect(dataPanelBody.style.display).toBe('none');
                });
            });
        });
    });
});
