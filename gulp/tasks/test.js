const { returnNotImplemented, registerTask } = require('../gulpHelper');

function taskFunction() {
    returnNotImplemented();
}

module.exports = (context) => {
    registerTask(context, ['build'], taskFunction);
};
