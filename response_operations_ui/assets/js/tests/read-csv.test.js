const { range } = require('lodash');

require('../includes/read-csv');

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
                buttonLoadSample.id = 'btn-upload-sample';
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
            const originalFileReader = window.FileReader;
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

        describe('#processFile', () => {
            let originalRenderUI = window.readCSV.__private__.renderUI;
            const getFakeEvent = () => {
                return {
                    target: {
                        result: ''
                    }
                };
            };

            beforeAll(() => {
                originalRenderUI = window.readCSV.__private__.renderUI;
                window.readCSV.__private__.renderUI = jest.fn();
            });

            beforeEach(() => {
                window.readCSV.__private__.renderUI.mockClear();
            });

            afterAll(() => {
                window.readCSV.__private__.renderUI = originalRenderUI;
            });

            it('should return the correct CI count for an RU_REF based classifier', () => {
                const event = getFakeEvent();
                range(0, 100).forEach(() => event.target.result += 'line\n');

                window.readCSV.__private__.processFile(event, ['RU_REF']);

                expect(window.readCSV.__private__.renderUI.mock.calls[0][1]).toEqual(100);
            });

            it('should return the correct CI count for a FORM_TYPE based classifier', () => {
                const event = getFakeEvent();
                range(0, 100).forEach(() => event.target.result += 'line\n');

                window.readCSV.__private__.processFile(event, ['FORM_TYPE']);

                expect(window.readCSV.__private__.renderUI.mock.calls[0][1]).toEqual(1);
            });

            it('should return the correct business count for a csv split by newlines', () => {
                const event = getFakeEvent();
                range(0, 100).forEach(() => event.target.result += 'line\n');

                window.readCSV.__private__.processFile(event, ['RU_REF']);

                expect(window.readCSV.__private__.renderUI.mock.calls[0][0]).toEqual(100);
            });

            it('should return the correct business count for a csv split by carriage returns', () => {
                const event = getFakeEvent();
                range(0, 100).forEach(() => event.target.result += 'line\r\n');

                window.readCSV.__private__.processFile(event, ['RU_REF']);

                expect(window.readCSV.__private__.renderUI.mock.calls[0][0]).toEqual(100);
            });
        });
    });

    describe('Public Functions', () => {
        describe('#cancelLoadSample', () => {
            const UNCHANGED = 'UNCHANGED';

            let originalGetElementById;
            let resetMock;
            let focusMock;
            let styleDisplay = UNCHANGED;
            let innerHTML = UNCHANGED;
            beforeAll(() => {
                resetMock = jest.fn();
                focusMock = jest.fn();

                originalGetElementById = document.getElementById;
                document.getElementById = jest.fn();
                document.getElementById.mockReturnValue({
                    innerHTML: innerHTML,
                    reset: resetMock,
                    style: {
                        display: styleDisplay
                    },
                    focus: focusMock
                });
            });

            beforeEach(() => {
                document.getElementById.mockClear();
                resetMock.mockClear();
                focusMock.mockClear();
                styleDisplay = UNCHANGED;
                innerHTML = UNCHANGED;
            });

            afterAll(() => {
                document.getElementById = originalGetElementById;
            });

            it('should clear load sample box', () => {
                document.getElementById('sample-preview').innerHTML = 'SOMETHING';
                window.readCSV.cancelLoadSample();
                expect(document.getElementById('sample-preview').innerHTML).toEqual('');
            });

            it('should reset the form', () => {
                window.readCSV.cancelLoadSample();
                expect(resetMock.mock.calls.length).toEqual(1);
            });

            it('should hide the load sample button', () => {
                window.readCSV.cancelLoadSample();
                expect(document.getElementById('btn-upload-sample').style.display).toEqual('none');
            });

            it('should hide the load cancel button', () => {
                window.readCSV.cancelLoadSample();
                expect(document.getElementById('btn-cancel-load-sample').style.display).toEqual('none');
            });

            it('should focus the file input', () => {
                window.readCSV.cancelLoadSample();
                expect(focusMock.mock.calls.length).toEqual(1);
            });
        });

        describe('#handleFiles', () => {
            let originalbrowserHasFileLoaderCapability;
            let originalAlertsWarn;
            let originalFileReader;
            const readAsTextMock = jest.fn();
            const mfrMockReturn = {
                onload: null,
                onerror: null,
                readAsText: readAsTextMock
            };

            const mockFileReader = jest.fn();
            mockFileReader.mockImplementation(() => mfrMockReturn);

            beforeAll(() => {
                originalbrowserHasFileLoaderCapability = window.readCSV.__private__.browserHasFileLoaderCapability;
                window.readCSV.__private__.browserHasFileLoaderCapability = jest.fn();
                originalAlertsWarn = window.alerts.warn;
                window.alerts.warn = jest.fn();
                originalFileReader = window.FileReader;
                window.FileReader = mockFileReader;
            });

            beforeEach(() => {
                window.readCSV.__private__.browserHasFileLoaderCapability.mockClear();
                window.readCSV.__private__.browserHasFileLoaderCapability.mockReturnValue(true);
                window.alerts.warn.mockClear();

                mockFileReader.mockClear();
                mockFileReader.mockImplementation(() => mfrMockReturn);
                readAsTextMock.mockClear();
            });

            afterAll(() => {
                window.readCSV.__private__.browserHasFileLoaderCapability = originalbrowserHasFileLoaderCapability;
                window.alerts.warn = originalAlertsWarn;
                window.FileReader = originalFileReader;
            });

            describe('Without FileReaderAPI supported', () => {
                it('should fire an alert if FileReader support check fails', () => {
                    window.readCSV.__private__.browserHasFileLoaderCapability.mockReturnValue(false);
                    window.readCSV.handleFiles([], []);

                    expect(window.alerts.warn.mock.calls.length).toEqual(1);
                });
            });

            describe('With FileReader API supported', () => {
                const fileArgs = ['SOMEFILE'];
                beforeEach(() => {
                    window.readCSV.handleFiles(fileArgs, []);
                });

                it('should instantiate a new FileReader ', () => {
                    expect(mockFileReader.mock.calls.length).toEqual(1);
                });

                it('should add an onload listener', () => {
                    expect(typeof mfrMockReturn.onload).toEqual('function');
                });

                it('should add an onerror listerner', () => {
                    expect(typeof mfrMockReturn.onerror).toEqual('function');
                });

                it('should read the file selected', () => {
                    expect(readAsTextMock.mock.calls.length).toEqual(1);
                    expect(readAsTextMock.mock.calls[0]).toEqual(fileArgs);
                });
            });
        });
    });
});
