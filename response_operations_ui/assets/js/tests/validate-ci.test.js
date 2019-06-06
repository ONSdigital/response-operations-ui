require('../../static/js/validate-ci');
jest.dontMock('lodash');
const {
    range,
    isArray
} = require('lodash');

const {
    nodeClassesChange,
    arrayLikeToArray
} = validateCI.__private__;

describe('Collection Instrument File Validation', () => {
    describe('#nodeClassesChange', () => {
        let node;

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
        let originalGetElementById;
        let originalNodeClassesChange;
        let originalArrayLikeToArray;

        const getElementByIdMock = (id) => {
            return {
                querySelectorAll: () => ( [{}, {}, {}] )
            };
        };

        beforeAll(() => {
            originalGetElementById = document.getElementById;
            originalNodeClassesChange = validateCI.__private__.nodeClassesChange;
            originalArrayLikeToArray = validateCI.__private__.arrayLikeToArray;

            document.getElementById = jest.fn(getElementByIdMock);
            validateCI.__private__.nodeClassesChange = jest.fn();
            validateCI.__private__.arrayLikeToArray = jest.fn(() => [{}, {}, {}]);
        });

        afterAll(() => {
            document.getElementById = originalGetElementById;
            validateCI.__private__.nodeClassesChange = originalNodeClassesChange;
            validateCI.__private__.arrayLikeToArray = originalArrayLikeToArray;
        });

        afterEach(() => {
            validateCI.__private__.nodeClassesChange.mockReset();
        });

        test('it should show panel if file type is wrong', () => {
            validateCI.checkCI({
                type: 'invalid file type'
            });

            expect(validateCI.__private__.nodeClassesChange.mock.calls.length).toEqual(6);
            expect(validateCI.__private__.nodeClassesChange.mock.calls.map(i => i[2])).toEqual(['add', 'add', 'remove', 'remove', 'remove', 'remove']);
        });

        test('it should hide panel if file type is correct', () => {
            validateCI.checkCI({
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });

            expect(validateCI.__private__.nodeClassesChange.mock.calls.length).toEqual(6);
            expect(validateCI.__private__.nodeClassesChange.mock.calls.map(i => i[2])).toEqual(['remove', 'remove', 'add', 'add', 'add', 'add']);
        });
    });

    describe('#checkSelectedCI', () => {
        let originalCheckCi;
        beforeAll(() => {
            originalCheckCi = validateCI.checkCI;
            validateCI.checkCI = jest.fn(() => {});
        });

        afterAll(() => {
            validateCI.checkCI = originalCheckCi;
        });

        afterEach(() => {
            validateCI.checkCI.mockReset();
        });

        test('it should try to process selected if window supports File API', () => {
            window.FileReader = {};
            validateCI.checkSelectedCI([{
                type: ''
            }]);

            expect(validateCI.checkCI.mock.calls.length).toEqual(1);
        });

        test('it should not try to process selected if window does not support File API', () => {
            window.FileReader = false;
            validateCI.checkSelectedCI({});

            expect(validateCI.checkCI.mock.calls.length).toEqual(0);
        });
    });
});
