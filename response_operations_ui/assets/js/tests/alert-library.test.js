require('../includes/alert-library');

describe('Alert library tests', () => {
    describe('Private functions', () => {
        let errorContainer;
        beforeEach(() => {
            errorContainer = document.createElement('div');
            errorContainer.id = 'error-alerts';
            document.body.append(errorContainer);
        });

        afterEach(() => {
            errorContainer.remove();
        });

        describe('_getErrorContainer', () => {
            test('returns an object if element found', () => {
                errorContainer.innerHtml = 'HTML';
                const output = alerts.__private__._getErrorContainer();

                expect(typeof output).toBe('object');
                expect(output.innerHtml).toBe('HTML');
            });

            test('returns null if no element found', () => {
                errorContainer.remove();

                const output = alerts.__private__._getErrorContainer();

                expect(output).toBe(null);
            });
        });

        describe('_clearAlerts', () => {
            test('should remove childnodes of error container', () => {
                const someOtherElement = document.createElement('div');
                errorContainer.appendChild(someOtherElement);

                expect(errorContainer.firstElementChild).toEqual(someOtherElement);

                alerts.__private__._clearAlerts();

                expect(errorContainer.firstElementChild).toBe(null);
            });
        });

        describe('_getPanelTemplateHtml', () => {
            let output;
            let testElement;

            beforeAll(() => {
                output = alerts.__private__._getPanelTemplateHtml('Panel Title', 'Panel content', 'TESTCLASS');
                testElement = document.createElement('div');
                testElement.innerHTML = output;
            });

            it('should return a panel with the passed title', () => {
                const foundTitle = testElement.querySelector('.panel__header > div');
                expect(foundTitle.textContent).toBe('Panel Title');
            });

            it('should return a panel with the passed message', () => {
                const foundBody = testElement.querySelector('.panel__body > div');
                expect(foundBody.textContent).toBe('Panel content');
            });

            it('should return a panel with the passed class', () => {
                const foundClass = testElement.querySelector('.panel');
                expect(foundClass.className.indexOf('panel--TESTCLASS')).toBeGreaterThan(-1);
            });

            it(`should return a panel with the class 'error' if no class is specified`, () => {
                const output = alerts.__private__._getPanelTemplateHtml('Panel Title', 'Panel content');
                const testElement = document.createElement('div');
                testElement.innerHTML = output;
                const foundClass = testElement.querySelector('.panel');

                expect(foundClass.className.indexOf('panel--error')).toBeGreaterThan(-1);
            });
        });

        describe('_getSimplePanelTemplateHtml', () => {
            let output;
            let testElement;

            beforeAll(() => {
                output = alerts.__private__._getSimplePanelTemplateHtml('Panel content', 'TESTCLASS');
                testElement = document.createElement('div');
                testElement.innerHTML = output;
            });

            it('should return a panel with the passed message', () => {
                const foundBody = testElement.querySelector('.panel__body > div');
                expect(foundBody.textContent).toBe('Panel content');
            });

            it('should return a panel with the passed class', () => {
                const foundClass = testElement.querySelector('.panel');
                expect(foundClass.className.indexOf('panel--TESTCLASS')).toBeGreaterThan(-1);
            });

            it(`should return a panel with the class 'error' if no class is specified`, () => {
                const output = alerts.__private__._getSimplePanelTemplateHtml('Panel content');
                const testElement = document.createElement('div');
                testElement.innerHTML = output;
                const foundClass = testElement.querySelector('.panel');
                expect(foundClass.className.indexOf('panel--error')).toBeGreaterThan(-1);
            });
        });
    });
});
