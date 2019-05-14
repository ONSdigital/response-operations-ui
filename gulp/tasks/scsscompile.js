const { registerTask } = require('../gulpHelper');
const GulpError = require('../GulpError');
const gulpSass = require('gulp-sass');
const gulpAutoPrefixer = require('gulp-autoprefixer');
const gulpCleanCss = require('gulp-clean-css');
const gulpSourcemaps = require('gulp-sourcemaps');
const dartSass = require('sass');
const Fiber = require('fibers');

// Forces gulp-sass to use installed node sass instead of dependency
gulpSass.compiler = dartSass;

function taskFunction() {
    const gulp = this.gulp;
    const SCSS_DIR = this.config['SCSS_DIR'];
    const CSS_DIR = this.config['CSS_DIR'];

    if (!SCSS_DIR) {
        throw new GulpError('SCSS_DIR config setting not set.');
    }

    if (!CSS_DIR) {
        throw new GulpError('CSS_DIR config setting not set.');
    }

    return gulp.src(`${SCSS_DIR}/main.scss`)
        .pipe(gulpSourcemaps.init())
        .pipe(
            gulpSass({
                fiber: Fiber
            }).on('error', gulpSass.logError)
        )
        .pipe(gulpAutoPrefixer())
        .pipe(gulpCleanCss())
        .pipe(gulpSourcemaps.write('.'))
        .pipe(gulp.dest(CSS_DIR));
}

module.exports = (context) => {
    registerTask(context, ['scss', 'scsscompile', 'scss_compile'], taskFunction.bind(context));
};
