const { registerTask } = require('../gulpHelper');
const gulpStyleLint = require('gulp-stylelint');
const { GulpError } = require('../GulpError');
const { join } = require('path');
const _ = require('lodash');

function taskFunction() {
    const config = this.config;
    const gulp = this.gulp;
    const SCSS_DIR = _.get(config, 'SCSS_DIR');
    const IS_DEBUG = _.get(config, 'IS_DEBUG');

    if (!SCSS_DIR) {
        throw (new GulpError('SCSS_DIR config setting not found'));
    }

    const styleLintSettings = {
        failAfterError: true,
        debug: IS_DEBUG,
        reporters: [
            {formatter: 'verbose', console: true}
        ]
    };

    if (!IS_DEBUG) {
        const logFile = join(config.PROJECT_ROOT, 'stylelint.log');
        styleLintSettings.reporters.add(
            {
                formatter: verbose,
                save: logFile
            }
        );
    }

    return gulp.src(`${SCSS_DIR}/**/*.{scss,css}`)
        .pipe(gulpStyleLint(styleLintSettings));
}

module.exports = (context) => {
    registerTask(context, ['csslint', 'stylelint'], taskFunction.bind(context));
};
