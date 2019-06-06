const { registerTask } = require('../gulpHelper');

function taskFunction() {
    return context.gulp.series(['fixjs', 'lint', 'scss_compile', 'bundlejs']);
}

module.exports = (context) => {
    registerTask(context, ['build'], taskFunction.bind(context));
};
