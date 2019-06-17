const { registerTask } = require('../gulpHelper');

function taskFunction() {
    return context.gulp.series(['lint', 'bundlejs', 'scss_compile']);
}

module.exports = (context) => {
    registerTask(context, ['build'], taskFunction.bind(context));
};
