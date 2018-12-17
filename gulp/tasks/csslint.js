const { registerTask } = require('../gulpHelper');
const gulpStyleLint = require('gulp-stylelint');

function taskFunction(context) {
    const config = context.config;
    const gulp = context.gulp;
    const SCSS_DIR = config['SCSS_DIR'];
    const IS_DEBUG = config['DEBUG'];

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

    return gulp
        .src(`${SCSS_DIR}/**/*.{scss,css}`)
        .pipe(gulpStyleLint(styleLintSettings));
}

module.exports = (context) => {
    registerTask(context, ['csslint', 'stylelint'], taskFunction.bind(context.gulp, context));
};
