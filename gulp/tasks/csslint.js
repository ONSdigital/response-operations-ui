const { registerTask } = require('../gulpHelper');
const gulpStyleLint = require('gulp-stylelint');
const _ = require('lodash');

function taskFunction(context) {
    const config = context.config;
    const gulp = context.gulp;
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

    gulp
        .src(`${SCSS_DIR}/**/*.{scss,css}`)
        .pipe(gulpStyleLint(styleLintSettings))
        .on('error', error => {
            return callback(error);
        });

    callback();
}

module.exports = (context) => {
    registerTask(context, ['csslint', 'stylelint'], taskFunction.bind(context.gulp, context));
};
