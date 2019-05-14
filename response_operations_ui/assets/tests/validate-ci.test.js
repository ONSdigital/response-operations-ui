require('../../static/js/validate-ci');
jest.dontMock('lodash');
const { range, isArray } = require('lodash');

describe('Collection Instrument File Validation', () => {
    describe('#nodeClassesRemove', () => {
        let node;
        const nodeClassesChange = window.__private__.nodeClassesChange;

        beforeEach(() => {
            node = document.createElement('div');
        });

        afterEach(() => {
            node = undefined;
        });

        test('it should throw an error if not passed a real node', () => {
            const fn = nodeClassesChange.bind(null, 'this isnt a dom node', [], 'remove');
            expect(fn).toThrow();
        });

        test('it should throw an error if not passed an array of classes', () => {
            const fn = nodeClassesChange.bind(null, node, 'this isnt an array', 'remove');
            expect(fn).toThrow();
        });

        test('it should throw an error if not passed a valid action', () => {
            const fn = nodeClassesChange.bind(null, node, [], 'cheese');
            expect(fn).toThrow();
        });

        test('it should accept a string in place of an array and still remove it', () => {
            node.classList.add('testClass');
            node.classList.add('testClass2');
            nodeClassesChange(node, 'testClass2', 'remove');

            expect(node.className.indexOf('testClass')).not.toBe(-1);
            expect(node.className.indexOf('testClass2')).toBe(-1);
        });

        test('it should remove classes from the classList of the node', () => {
            const nodeClasses = range(0, 10).map(i => `class${i.toString()}`);
            const nodeClassesToRemove = nodeClasses.filter(className => parseInt(className.substr(-1)) % 2 === 0);
            const expectedRemainingClasses = nodeClasses.filter(className => !nodeClassesToRemove.includes(className));

            nodeClasses.forEach(className => node.classList.add(className));

            nodeClassesChange(node, nodeClassesToRemove, 'remove');

            expect(Object.values(node.classList)).toEqual(expectedRemainingClasses);
        });

        test('it should add classes to the classList of the node', () => {
            const nodeClasses = range(0, 10).map(i => `class${i.toString()}`);
            const nodeClassesToRemove = nodeClasses.filter(className => parseInt(className.substr(-1)) % 2 === 0);
            const expectedRemainingClasses = nodeClasses.filter(className => !nodeClassesToRemove.includes(className));

            nodeClasses.forEach(className => node.classList.add(className));

            nodeClassesChange(node, nodeClassesToRemove, 'remove');

            expect(Object.values(node.classList)).toEqual(expectedRemainingClasses);
        });
    });

    describe('#arrayLikeToArray', () => {
        const arrayLikeToArray = window.__private__.arrayLikeToArray;

        test('it should throw an error if not passed an array like type', () => {
            const fn = arrayLikeToArray.bind(null, 12);

            expect(fn).toThrow();
        });

        test('it should return an array if passed an array like type', () => {
            const arrayLike = new Set();

            range(0, 5).forEach(i => arrayLike.add(i));

            expect(isArray(arrayLike)).toBe(false);
            expect(isArray(arrayLikeToArray(arrayLike))).toBe(true);
        });
    });

    describe('#checkCI', () => {

    });

    describe('#checkSelectedCI', () => {
        let originalCheckCi;
        beforeAll(() => {
            originalCheckCi = window.checkCI;
            window.checkCI = jest.fn();
        });

        afterAll(() => {
            window.checkCI = originalCheckCi;
        });

        afterEach(() => {
            window.checkCI.reset();
        });

        test('it should try to process selected if window supports File API', () => {
            window.FileReader = {};
            checkSelectedCI({});

            expect(checkCI.calls.length).toEqual(1);
        });

        test('it should not try to process selected if window does not support File API', () => {
            delete window.FileReader;
            checkSelectedCI({});

            expect(checkCI.calls.length).toEqual(1);
        });
    });
});
