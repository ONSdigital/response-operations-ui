/*

    A highly commented example of the JS testing framework, not to be run.
    Note that the containing 'describe' is using 'skip' to avoid these tests being run

*/

// include the functions we want to test:
const {
    isEven,
    alwaysReturnsTwo,
    multiplyByThree,
    asynchronousFunctionCallback,
    asynchronousFunctionPromise,
    asynchronousFunctionPromiseRejects,
    timerFunctionThatTakesALongTime,
    makingAMockeryOfFunctions
} = require('./example_test_functions'); // We include our own function here, for test

let { getValueA, getValueB }  = require('./example_test_functions'); // These included using let so they can be mocked.

/**
 * 'describe' blocks allow you to section off tests into separate parts - this is then reflected in the output from test runners, and from the jest command line tool
 *
 * You can put describe blocks within describe blocks, to nest a 'tree' of tests, for organisation
 *
 * Conventionally, when tests refer to a single function, you should put those tests in a describe block in the form 'describe('#functionName')'
 */
describe(' Our example tests', () => {
    /**
     * These tests are testing basic pure functions, and this is how the ideal test looks.
     *
     * The functions themselves are sectioned into a 'describe' block, and this contains a number of 'test' blocks.
     * The test block can contain multiple expectations, but it's best to minimise the number of expectations per
     * block, so that when a test fails, it's clear which part of the expectation failed.
     *
     * E.g. If the test that fails is called "function should return a string", it's clear that if it fails, it didn't
     * return a string. If it's called "function should return correct output", and has multiple expectations, we don't
     * know immediately which failed.
     *
     * NB: Opinion is divided on this idea, and some people prefer multiple expectations.
     */
    describe('Simple functional testing', () => {
        describe('#isEven', () => {
            test('should throw an error if not passed a number', () => {
                // Assert that the function throws an error when passed a non number (a specific error if you want)
                expect(isEven.bind(null, 'not a number')).toThrow();
            });

            test('should throw and error if passed a non-integer number', () => {
                // Assert that the function throws an error when passed an non-integer number
                expect(isEven.bind(null, 'not a number')).toThrow();
            });

            test('should return true for an even number', () => {
                expect(isEven(2)).toBe(true);
            });

            test('should return true for an odd number', () => {
                expect(isEven(3)).toBe(false);
            });
        });

        describe('#alwaysReturnsTwo', () => {
            test('should return a number', () => {
                expect(typeof alwaysReturnsTwo()).toBe('number');
            });

            test('should not return a string', () => {
                expect(alwaysReturnsTwo()).not.toBe('string');
            });

            test('should return 2', () => {
                expect(alwaysReturnsTwo()).toBe(2);
            });
        });

        describe('#multiplyByThree', () => {
            test('should return input multiplied by three', () => {
                [0, 3, 3.141].forEach(n => expect(multiplyByThree(n)).toBe(n*3));
            });
        });
    });

    /**
     * Asynchronous function testing examples:
     *
     * Famously, many functions in Javascript are asynchronous, and there are many types of asynchronous function completion:
     *
     *  - Callback-based functions: Passed a function when invoked, and call it when finished.
     *  - Promise-based functions: Return a 'Promise' object when invoked, and then call 'then' or 'catch' functions when it finishes, 'then' called on success, 'catch' called on failure
     *  - Native async functions: Largely not supported in browsers, these are syntactic sugar for promises that allow them to be written in a synchronous style.
     */
    describe('Testing various asynchronous functions', () => {
        /**
         * Testing a callback based function:
         */
        describe('#asynchronousFunctionCallback', () => {
            // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
            test('should callback', (done) => {
                asynchronousFunctionCallback(callback => {
                    expect(true);
                    done();
                });
            });
        });

        /**
         * Testing a promise function:
         */
        describe('#asynchronousFunctionPromise', () => {
            // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
            test('should resolve a promise', done => {
                asynchronousFunctionPromise()
                    .then(() => {
                        expect(true);
                        done();
                    });
            });
        });

        /**
         * Testing a promise function:
         */
        describe('#asynchronousFunctionPromiseRejects', () => {
            // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
            test('should reject a promise', () => {
                asynchronousFunctionPromiseRejects()
                    .catch(() => {
                        expect(true);
                        done();
                    });
            });
        });
    });

    /**
     * Mocking in Jest testing framework
     *
     * When testing functions that call other functions, you should mock the output of those functions, so that you are testing only the function under test (the unit)
     * Jest has multiple mock styles and assistants for this:
     */
    describe('Testing using mocks', () => {
        /**
         * Mocking timers
         *
         * Sometimes, functions have timers in them for applications like regularly updating output etc.  These needlessly slow down the testing.
         * See example below for a function that times for 30 minutes, but can be tested immediately.
         */
        describe('#timerFunctionThatTakesALongTime', () => {
            beforeAll(() => {
                jest.useFakeTimers();
            });

            test(`should callback 'done'`, () => {
                const callback = jest.fn();
                timerFunctionThatTakesALongTime(callback);
                expect(callback).not.toBeCalled();
                jest.runAllTimers();
                expect(callback).toBeCalledWith('done');
            });
        });
    });
});
