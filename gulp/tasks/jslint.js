const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['jslint', 'eslint'], taskFunction.bind(context.gulp, context));
};
