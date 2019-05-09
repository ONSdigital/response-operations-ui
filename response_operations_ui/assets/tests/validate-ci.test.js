require('../../static/js/alert-library');
const { range } = require('lodash');


describe('Collection Instrument File Validation', () => {
    describe('#nodeClassesRemove', () => {
        let node;
        const nodeClassesRemove = window.nodeClassesRemove;

        beforeEach(() => {
            node = document.createElement('div');
        });

        afterEach(() => {
            node = undefined;
        });

        test('it should throw an error if not passed a real node', () => {
            const fn = nodeClassesRemove.bind(null, 'this isnt a dom node', []);
            expect(fn).toThrow();
        });

        test('it should throw an error if not passed an array of classes', () => {
            const fn = nodeClassesRemove.bind(null, node, 'this isnt an array');
            expect(fn).toThrow();
        });

        test('it should remove classes from the classList of the node', () => {
            const nodeClasses = range(0, 10).map(i => `class${i.toString()}`);
            const nodeClassesToRemove = nodeClasses.filter(className => parseInt(className.substr(-1)) % 2 === 0);
            const expectedRemainingClasses = nodeClasses.filter(className => !nodeClassesToRemove.includes(className));

            nodeClasses.forEach(className => node.classList.add(className));

            nodeClassesRemove(node, nodeClassesToRemove);

            expect(node.classList).toEqual(expectedRemainingClasses);
        });

        test(`it should leave prexisting classes in the classList that aren't specified to remove`, () => {});
    });
});
