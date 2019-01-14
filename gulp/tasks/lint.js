const { registerTask } = require('../gulpHelper');

module.exports = (context) => {
    registerTask(context, ['lint'], context.gulp.series(['csslint', 'jslint']));
};

