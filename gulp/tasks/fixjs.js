const { registerTask } = require('../gulpHelper');
const prettier = require('gulp-prettier');
const { join } = require('path');
const { get } = require('lodash');

function taskFunction() {
    const PROJECT_ROOT = get(this, 'config.PROJECT_ROOT');
    const jsPath = join(PROJECT_ROOT, 'assets', '**/*.js');

    return this.gulp.src(jsPath)
        .pipe(prettier())
        .pipe(this.gulp.dest());
}

module.exports = (context) => {
    registerTask(context, ['fixjs', 'jsfix'], taskFunction.bind(context));
};
