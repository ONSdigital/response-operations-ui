const _ = require('lodash');
const browserify = require('browserify');
const transform = require('vinyl-transform');
const source = require('vinyl-source-stream');
const buffer = require('vinyl-buffer');
const babel = require('gulp-babel');
const sourcemaps = require('gulp-sourcemaps');
const minify = require('gulp-babel-minify');

const { registerTask } = require('../gulpHelper');

function taskFunction(callback) {
    const gulp = this.gulp;
    const config = this.config;

    const JS_SRC_DIR = _.get(config, 'JS_SRC_DIR');
    const JS_DEST_DIR = _.get(config, 'JS_DEST_DIR');
    const MINIFY_OPTIONS = _.get(config, 'MINIFY_OPTIONS', {});
    const MINIFY_OVERRIDES = _.get(config, 'MINIFY_OVERRIDES', {});
    const BROWSERIFY_OPTIONS = _.get(config, 'BROWSERIFY_OPTIONS', {});
    const BABEL_OPTIONS = _.get(config, 'BABEL_OPTIONS', {});

    const minifyOptionsDefaults = {};
    const minifyOverridesDefaults = {};
    const browserifyOptionsDefaults = {};
    const babelOptionsDefaults = {};

    const minifyOptions = Object.assign({}, minifyOptionsDefaults, MINIFY_OPTIONS);
    const minifyOverrides = Object.assign({}, minifyOverridesDefaults, MINIFY_OVERRIDES);
    const browserifyOptions = Object.assign({}, browserifyOptionsDefaults, BROWSERIFY_OPTIONS);
    const babelOptions = Object.assign({}, babelOptionsDefaults, BABEL_OPTIONS);

    const browserifyVinyl = transform(function(filename) {
        const bundler = browserify(filename, browserifyOptions);
        return bundler.bundle;
    });

    const includedJsGlob = `${JS_SRC_DIR}/*.js`;
    const excludedJsGlob = `!${JS_SRC_DIR}/_*.js`;
    const srcArg = [includedJsGlob, excludedJsGlob];

    return gulp.src(srcArg)
        // .pipe(sourcemaps.init())
        .pipe(browserifyVinyl
        // .pipe(babel(babelOptions))
        .pipe(minify(minifyOptions, minifyOverrides))
        // .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(JS_DEST_DIR));
}

module.exports = (context) => {
    registerTask(context, ['bundlejs', 'bundle'], taskFunction.bind(context));
};
