module.exports = {

    isEven: (number) => {
        if (!Number.isInteger(number)) {
            throw new TypeError('Expected an integer input');
        }

        return number % 2 === 0;
    },

    alwaysReturnsTwo: () => 2,

    multiplyByThree: i => i*3,

    asynchronousFunctionCallback: (callback) => {
        setTimeout(() => callback(), 10);
    },

    asynchronousFunctionPromise: (callback) => {
        return new Promise((resolve) => {
            setTimeout(() => resolve(), 10);
        });
    },

    asynchronousFunctionPromiseRejects: (callback) => {
        return new Promise((_, reject) => {
            setTimeout(() => reject(), 10);
        });
    }

}