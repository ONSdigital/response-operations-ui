const { series } = require('gulp');
const _ = require('lodash');

function taskFunction(context, callback) {
    const { config } = context;
    const gulp = context.gulp;

    const PROJECT_ROOT = _.get(config, 'PROJECT_ROOT');
    const CSS_DIR = _.get(config, 'CSS_DIR');
    const SCSS_DIR = _.get(config, 'SCSS_DIR');
    const JS_SRC_DIR = _.get(config, 'JS_SRC_DIR');
    const JS_DEST_DIR = _.get(config, 'JS_DEST_DIR');

    if (!CSS_DIR) {
        throw (new GulpError('CSS_DIR config setting not found'));
    }

    if (!SCSS_DIR) {
        throw (new GulpError('SCSS_DIR config setting not found'));
    }

    if (!JS_SRC_DIR) {
        throw (new GulpError('JS_SRC_DIR config setting not found'));
    }

    if (!JS_DEST_DIR) {
        throw (new GulpError('JS_DEST_DIR config setting not found'));
    }

    gulp.watch(SCSS_DIR + '**/*.{css, scss}', series('csslint', 'scsscompile', () => callback()));
    gulp.watch([JS_SRC_DIR + '/**/*.js', PROJECT_ROOT + '/gulpfile.js', PROJECT_ROOT + '/gulp/**/*.js'], series('jslint', () => callback()));
}

module.exports = (context) => {
    context.gulp.task('watch', taskFunction.bind(context.gulp, context));
};
