const { registerTask } = require('../gulpHelper');
const prettier = require('gulp-prettier');
const { join } = require('path');
const { get } = require('lodash');

function taskFunction() {
    const PROJECT_ROOT = get(this, 'config.PROJECT_ROOT');
    const jsPath = join(PROJECT_ROOT, 'assets', 'js');
    const jsPathGlob = join(jsPath, '**/*.js');

    return this.gulp.src(jsPathGlob)
        .pipe(prettier())
        .pipe(this.gulp.dest(jsPath, { overwrite: true }));
}

module.exports = (context) => {
    registerTask(context, ['fixjs', 'jsfix'], taskFunction.bind(context));
};
