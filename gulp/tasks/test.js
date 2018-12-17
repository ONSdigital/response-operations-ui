const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['test'], taskFunction.bind(context.gulp, context));
};
