const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    return returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['test'], taskFunction.bind(context));
};
