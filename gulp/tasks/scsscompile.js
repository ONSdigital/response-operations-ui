const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['scss', 'scsscompile'], taskFunction.bind(context.gulp, context));
};
