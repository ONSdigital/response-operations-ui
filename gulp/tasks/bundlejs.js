const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction(callback) {
    return returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['bundlejs', 'bundle'], taskFunction.bind(context));
};
