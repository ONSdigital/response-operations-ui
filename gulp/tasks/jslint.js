const _ = require('lodash');
const gulpEslint = require('gulp-eslint');
const { createWriteStream } = require('fs');
const { join } = require('path');

const { registerTask } = require('../gulpHelper');
const GulpError = require('../GulpError');

function taskFunction(callback) {
    const config = this.config;
    const gulp = this.gulp;

    const JS_SRC_DIR = _.get(config, 'JS_SRC_DIR');
    const IS_DEBUG = _.get(config, 'IS_DEBUG');
    const GULP_ESLINT_SETTINGS = _.get(config, 'GULP_ESLINT_SETTINGS', {});
    const PROJECT_ROOT = _.get(config, 'PROJECT_ROOT');

    if (!JS_SRC_DIR) {
        throw new GulpError('JS_SRC_DIR config setting not found');
    }

    const eslintDefaultSettings = {
        configFile: join(PROJECT_ROOT, '.eslintrc.json')
    };

    const eslintConfig = Object.assign({}, eslintDefaultSettings, GULP_ESLINT_SETTINGS);

    const output = gulp.src([JS_SRC_DIR + '/**/*.js', PROJECT_ROOT + '/gulpfile.js', PROJECT_ROOT + '/gulp/**/*.js'])
        .pipe(gulpEslint(eslintConfig));

    if (IS_DEBUG) {
        callback(output
            .pipe(gulpEslint.failAfterError())
            .pipe(gulpEslint.formatEach('codeframe')));
    }

    const logFile = createWriteStream(join(PROJECT_ROOT, 'eslint.log'));
    output
        .pipe(gulpEslint.failOnError())
        .pipe(gulpEslint.format('unix', logFile))
        .on('error', error => {
            return callback(error);
        });
    callback();
}


module.exports = (context) => {
    registerTask(context, ['jslint', 'eslint'], taskFunction.bind(context));
};
