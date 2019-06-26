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
        setTimeout(() => callback(), 1);
    },

    asynchronousFunctionPromise: () => {
        return new Promise((resolve) => {
            setTimeout(() => resolve(), 1);
        });
    },

    asynchronousFunctionPromiseRejects: () => {
        return new Promise((_, reject) => {
            setTimeout(() => reject(), 1);
        });
    },

    timerFunctionThatTakesALongTime: (callback) => {
        const ONE_MINUTE = 60000;
        setTimeout(() => {
            callback('done');
        }, ONE_MINUTE * 30);
    }
};

