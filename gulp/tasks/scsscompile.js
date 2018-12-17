const { registerTask } = require('../gulpHelper');
const GulpError = require('../GulpError');
const gulpSass = require('gulp-sass');
const gulpAutoPrefixer = require('gulp-autoprefixer');
const gulpCleanCss = require('gulp-clean-css');
const gulpSourcemaps = require('gulp-sourcemaps');

function taskFunction(callback) {
    const gulp = this.gulp;
    const SCSS_DIR = this.config['SCSS_DIR'];
    const CSS_DIR = this.config['CSS_DIR'];

    if (!SCSS_DIR) {
        throw new GulpError('SCSS_DIR config setting not set.');
    }

    if (!CSS_DIR) {
        throw new GulpError('CSS_DIR config setting not set.');
    }

    gulp.src(`${SCSS_DIR}/main.scss`)
        .pipe(gulpSourcemaps.init())
        .pipe(gulpSass())
        .pipe(gulpAutoPrefixer())
        .pipe(gulpCleanCss())
        .pipe(gulpSourcemaps.write('.'))
        .pipe(gulp.dest(CSS_DIR))
        .on('error', error => {
            return callback(error);
        });

    callback();
}

module.exports = (context) => {
    registerTask(context, ['scss', 'scsscompile'], taskFunction.bind(context));
};
