const { registerTask } = require('../gulpHelper');

module.exports = (context) => {
    registerTask(context, ['test'], context.gulp.series(['csslint', 'jslint', 'jstest']));
};
