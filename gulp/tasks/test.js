const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction(callback) {
    callback(returnNotImplemented());
}

module.exports = (context) => {
    registerTask(context, ['test'], taskFunction.bind(context));
};
