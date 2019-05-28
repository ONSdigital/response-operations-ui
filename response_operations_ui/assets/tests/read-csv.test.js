require('../../static/js/read-csv');

describe('CSV Reader tests', () => {
    describe('Private functions', () => {
        describe('#getOutputTemplate', () => {
            let panel;
            beforeAll(() => {
                panelContainer = document.createElement('div');
                panelContainer.innerHTML = window.readCSV.__private__.getOutputTemplate(45, 900);

                panel = panelContainer.querySelector('div');
            });

            it('should render an info panel', () => {
                expect(panel.className.indexOf('panel--info')).not.toBe(-1);
            });

            it('should include a header', () => {
                expect(panel.querySelectorAll('.panel__header').length).toBe(1);
            });

            it('should include a body', () => {
                expect(panel.querySelectorAll('.panel__body').length).toBe(1);
            });

            it('should include the business count in the body', () => {
                const textInBody = panel.querySelector('#sample-preview-businesses').textContent;
                expect(textInBody).toBe('Number of businesses: 45');
            });

            it('should include the CI count in the body', () => {
                const textInBody = panel.querySelector('#sample-preview-ci').textContent;
                expect(textInBody).toBe('Collection instruments: 900');
            });
        });

        describe('#renderUI', () => {
            let samplePreview;
            let buttonCheckSampleContents;
            let buttonLoadSample;
            let buttonCancelLoadSample;

            let originalGetOutputTemplate;

            beforeAll(() => {
                // Setup DOM Elements
                samplePreview = document.createElement('div');
                buttonCheckSampleContents = document.createElement('button');
                buttonLoadSample = document.createElement('button');
                buttonCancelLoadSample = document.createElement('button');

                samplePreview.id = 'sample-preview';
                buttonCheckSampleContents.id = 'btn-check-sample-contents';
                buttonLoadSample.id = 'btn-load-sample';
                buttonCancelLoadSample.id = 'btn-cancel-load-sample';

                [
                    samplePreview,
                    buttonCheckSampleContents,
                    buttonLoadSample,
                    buttonCancelLoadSample
                ].forEach(el => document.body.appendChild(el));

                // Patch getOutputTemplate
                originalGetOutputTemplate = window.readCSV.__private__.getOutputTemplate;
                window.readCSV.__private__.getOutputTemplate = jest.fn();
                window.readCSV.__private__.getOutputTemplate.mockReturnValue('TEST OUTPUT');
            });

            beforeEach(() => {
                buttonCancelLoadSample.style.display = '';
                buttonLoadSample.style.display = '';
                buttonCheckSampleContents.style.display = '';

                window.readCSV.__private__.getOutputTemplate.mockClear();
            });

            afterAll(() => {
                window.readCSV.__private__.getOutputTemplate = originalGetOutputTemplate;
            });

            it('should call the getOutputTemplate renderer only once', () => {
                window.readCSV.__private__.renderUI(1, 2);
                expect(window.readCSV.__private__.getOutputTemplate.mock.calls.length).toBe(1);
            });

            it('should pass the business and collection instrument counts to the getOutputTemplate renderer', () => {
                window.readCSV.__private__.renderUI(1, 2);
                expect(window.readCSV.__private__.getOutputTemplate.mock.calls[0]).toEqual([1, 2]);
            });

            it('should set the content of the sample preview to the value returned by template renderer', () => {
                window.readCSV.__private__.renderUI(1, 2);
                expect(samplePreview.innerHTML).toBe('TEST OUTPUT');
            });

            it('should hide the check sample contents button', () => {
                expect(buttonCheckSampleContents.style.display).not.toBe('none');
                window.readCSV.__private__.renderUI(1, 2);
                expect(buttonCheckSampleContents.style.display).toBe('none');
            });

            it('should show the load sample button', () => {
                expect(buttonLoadSample.style.display).not.toBe('inline-block');
                window.readCSV.__private__.renderUI(1, 2);
                expect(buttonLoadSample.style.display).toBe('inline-block');
            });

            it('should show the cancel load sample button', () => {
                expect(buttonCancelLoadSample.style.display).not.toBe('inline-block');
                window.readCSV.__private__.renderUI(1, 2);
                expect(buttonCancelLoadSample.style.display).toBe('inline-block');
            });
        });

        describe('#errorHandler', () => {
            let originalAlertsError;
            beforeAll(() => {
                if (!window.alerts) {
                    window.alerts = {
                        error: () => {}
                    };
                }
                originalAlertsError = window.alerts.error;
                window.alerts.error = jest.fn();
            });

            beforeEach(() => {
                window.alerts.error.mockClear();
            });

            afterAll(() => {
                window.alerts.error = originalAlertsError;
            });

            it('should call alerts.error if the error was a NotReadableError', () => {
                const fakeError = {
                    target: {
                        error: {
                            name: 'NotReadableError'
                        }
                    }
                };

                window.readCSV.__private__.errorHandler(fakeError);

                expect(window.alerts.error.mock.calls.length).toBe(1);
            });

            it('should not call alerts.error if the error was not a NotReadableError', () => {
                const fakeError = {
                    target: {
                        error: {
                            name: 'TotallyDifferentError'
                        }
                    }
                };

                window.readCSV.__private__.errorHandler(fakeError);

                expect(window.alerts.error.mock.calls.length).toBe(0);
            });
        });

        describe('#browserHasFileLoaderCapability', () => {
            let originalFileReader = window.FileReader;
            afterAll(() => {
                window.FileReader = originalFileReader;
            });

            it('should return true if browser has FileReaderAPI', () => {
                window.FileReader = () => {};
                expect(window.readCSV.__private__.browserHasFileLoaderCapability()).toBe(true);
            });

            it('should return false if browser doesn\'t have FileReaderAPI', () => {
                delete window.FileReader;
                expect(window.readCSV.__private__.browserHasFileLoaderCapability()).toBe(false);
            });
        });
    });

    describe('Public Functions', () => {

    });
});
