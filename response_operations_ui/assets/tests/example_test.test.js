/*

    A highly commented example of the JS testing framework, not to be run.
    Note that the containing 'context' is using 'skip' to avoid these tests being run

*/

// External libraries
const _ = require('lodash');

/**
 * Chai.js is an assertion library that provides us with ways to assert what the outcome
 * of a test should be
 *
 * assert provides traditional assert style statements, similar to those in many languages
 * should provides a plain english interface that allows you to form english-like sentences
 * to explain the test
 * expect is also an english style assertion API, that allows you to write sentence-like
 * assertions beginning with 'expect', rather than 'should'
 *
 * NB: All assertion types take an error message as a final argument, which will be shown if the test fails
 *
 * See below for examples of each
 */
const { assert, expect } = require('chai');
require('chai').should();

const { isEven, alwaysReturnsTwo, multiplyByThree, asynchronousFunctionCallback, asynchronousFunctionPromise, asynchronousFunctionPromiseRejects } = require('./example_test_functions') // We include our own function here, for test

/**
 * Tests are written in sections, using 'context', 'describe', and 'it'
 *
 * describe - typically describes a particular aspect of testing, often an actual function - 'multiplyByTwo'
 * it - denotes the block that will contain actual assertions
 *
 * NB: All of these can be embedded within each other to organise tests: a describe block can contain other
 * describe blocks, it blocks etc. In test runners, this leads to very organised output
 */
context(' Our example tests', () => {
    /**
     * This tests will use classic asserts as examples of this
     *
     * The assert API has many functions to test different types of criteria
     * https://www.chaijs.com/api/assert/
     */
    describe('#isEven', () => {
        it('should throw an error if not passed a number', () => {
            // Assert that the function throws an error when passed a non number (a specific error if you want)
            assert.throws(isEven.bind(null, 'not a number'), TypeError, 'Expected an integer input');
        });

        it('should throw and error if passed a non-integer number', () => {
            // Assert that the function throws an error when passed an non-integer number
            assert.throws(isEven.bind(null, 'not a number'), TypeError, 'Expected an integer input');
        });

        it('should return true for an even number', () => {
            assert.isTrue(isEven(2), `isEven didn't return true for an even number`);
        });

        it('should return true for an odd number', () => {
            assert.isFalse(isEven(3), `isEven didn't return false for an of odd number`);
        });
    });

    /**
     * Tests using should asserts now - a plain-english style assertion
     */
    describe('#alwaysReturnsTwo', () => {
        it('should return a number', () => {
            alwaysReturnsTwo().should.be.a('number');
        });

        it('should not return a string', () => {
            alwaysReturnsTwo().should.not.be.a('string');
        });

        it('should return 2', () => {
            alwaysReturnsTwo().should.equal(2);
        });
    });

    /**
     * Tests using expect API
     */
    describe('#multiplyByThree', () => {
        it('should return input multiplied by three', () => {
            [0, 3, 3.141].forEach(n => expect(multiplyByThree(n)).to.equal(n*3));
        });
    });

    /**
     * Asynchronous function testing examples:
     *
     * Testing a callback function:
     */
    describe('#asynchronousFunctionCallback', (done) => {
        // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
        asynchronousFunctionCallback(callback => {
            // assertions would go here
            done();
        });
    });

    /**
     * Testing a promise function:
     */
    describe('#asynchronousFunctionPromise', (done) => {
        // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
        asynchronousFunctionPromise()
            .then(() => {
                // assertions would go here
                done();
            });
    });

    /**
     * Testing a promise function:
     */
    describe('#asynchronousFunctionPromiseRejects', (done) => {
        // We've used the 'done' argument in this function, and the test will wait until it is called, or it times out.
        asynchronousFunctionPromiseRejects()
            .catch(() => {
                // assertions would go here
                done();
            });
    });
});
