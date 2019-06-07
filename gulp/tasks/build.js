const { registerTask } = require('../gulpHelper');

function taskFunction() {
    return context.gulp.series(['lint', 'scss_compile', 'bundlejs']);
}

module.exports = (context) => {
    registerTask(context, ['build'], taskFunction.bind(context));
};
