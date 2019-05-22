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

        describe('#renderUi', () => {
            let samplePreview;
            let buttonCheckSampleContents;
            let buttonLoadSample;
            let buttonCancelLoadSample;

            beforeAll(() => {
                const container = document.createElement('div');

                samplePreview = document.createElement('div');
                buttonCheckSampleContents = document.createElement('button');
                buttonLoadSample = document.createElement('button');
                buttonCancelLoadSample = document.createElement('button');

                samplePreview.id = 'sample-preview';
                buttonCheckSampleContents.id = 'btn-check-sample-contents';
                buttonLoadSample.id = 'btn-load-sample';
                buttonCancelLoadSample.id = 'btn-load-sample';

                [samplePreview, buttonCheckSampleContents, buttonLoadSample, buttonCancelLoadSample].forEach(container.appendChild);
            });
        });
    });

    describe('Public Functions', () => {

    });
});
