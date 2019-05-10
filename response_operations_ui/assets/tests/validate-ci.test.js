require('../../static/js/validate-ci');
jest.dontMock('lodash');
const { range } = require('lodash');


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
            const fn = nodeClassesChange.bind(null, node, [], 'remove');
            expect(fn).toThrow();
        });

        test('it should remove classes from the classList of the node', () => {
            const nodeClasses = range(0, 10).map(i => `class${i.toString()}`);
            const nodeClassesToRemove = nodeClasses.filter(className => parseInt(className.substr(-1)) % 2 === 0);
            const expectedRemainingClasses = nodeClasses.filter(className => !nodeClassesToRemove.includes(className));

            nodeClasses.forEach(className => node.classList.add(className));

            nodeClassesRemove(node, nodeClassesToRemove, 'remove');

            expect(Object.values(node.classList)).toEqual(expectedRemainingClasses);
        });

        test('it should add classes to the classList of the node', () => {
            const nodeClasses = range(0, 10).map(i => `class${i.toString()}`);
            const nodeClassesToRemove = nodeClasses.filter(className => parseInt(className.substr(-1)) % 2 === 0);
            const expectedRemainingClasses = nodeClasses.filter(className => !nodeClassesToRemove.includes(className));

            nodeClasses.forEach(className => node.classList.add(className));

            nodeClassesRemove(node, nodeClassesToRemove, 'remove');

            expect(Object.values(node.classList)).toEqual(expectedRemainingClasses);
        });
    });
});
