const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    callback(returnNotImplemented());
}

module.exports = (context) => {
    registerTask(context, ['build'], taskFunction.bind(context));
};
