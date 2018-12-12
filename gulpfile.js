
const gulp = require('gulp');
const gulpStyleLint = require('gulp-stylelint');
const gulpAutoPrefixer = require('gulp-autoprefixer');
const gulpSourcemaps = require('gulp-sourcemaps');
const gulpCleanCss = require('gulp-clean-css');
const gulpBabel = require('gulp-babel');
const gulpEsLint = require('gulp-eslint');
const gulpSass = require('gulp-sass');
const gulpMocha = require('gulp-mocha');

const transform = require('vinyl-transform');

const chalk = require('chalk');
const _ = require('lodash');
const path = require('path');

const {returnNotImplemented} = require('./gulp/gulpHelper');
const {GulpError} = require('./gulp/GulpError');

const packageJson = require('./package.json');
const config = _.get(packageJson, 'config.gulp', {});

const PROJECT_ROOT = __dirname;

const SCSS_DIR = _.get(config, 'SCSS_DIR', '').replace('$ROOT', PROJECT_ROOT);
const CSS_DIR = _.get(config, 'CSS_DIR', '').replace('$ROOT', PROJECT_ROOT);
const JS_SRC_DIR = _.get(config, 'JS_SRC_DIR', '').replace('$ROOT', PROJECT_ROOT);
const JS_DEST_DIR = _.get(config, 'JS_DEST_DIR', '').replace('$ROOT', PROJECT_ROOT);

const IS_DEBUG = Boolean(process.env.DEBUG);

gulp.task('default', () => {
    console.log(`
    Usage:
        npm test       ${chalk.blue('Run the tests through the test harness')}
        npm build      ${chalk.blue('Run the frontend build')}
        npm run watch  ${chalk.blue('Run the watcher - actively recompile frontend during development')}
    `);
});

// Main functions
gulp.task('test', returnNotImplemented);

gulp.task('build', returnNotImplemented);

gulp.task('watch', () => {
    gulp.watch(`${SCSS_DIR}/**/*.{css,scss}`, ['csslint', '']);
});

gulp.task('lint', ['jslint', 'csslint']);

// Sub tasks
gulp.task('csslint', () => {
    if (SCSS_DIR === '') {
        throw (new GulpError('SCSS_DIR config setting not found'));
    }

    const styleLintSettings = {
        failAfterError: true,
        debug: IS_DEBUG,
        reporters: [
            {formatter: 'verbose', console: true}
        ]
    };

    console.log(SCSS_DIR);

    return gulp
        .src(`${SCSS_DIR}/**/*.{scss,css}`)
        .pipe(gulpStyleLint(styleLintSettings));
});

gulp.task('jslint', () => {

});

gulp.task('mocha', returnNotImplemented);

gulp.task('bundlejs', returnNotImplemented);

gulp.task('transformjs', returnNotImplemented);

gulp.task('browserify', returnNotImplemented);

gulp.task('scsscompile', () => {
    gulp.src(`${SCSS_DIR}/main.scss`)
        .pipe(gulpSourcemaps.init())
        .pipe(gulpSass())
        .pipe(gulpAutoPrefixer())
        .pipe(gulpCleanCss())
        .pipe(gulpSourcemaps.write(CSS_DIR))
        .dest(CSS_DIR + '/main.css')
});

gulp.task('stylelint', ['csslint']);
