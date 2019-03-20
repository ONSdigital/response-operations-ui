const { registerTask } = require('../gulpHelper');
const { GulpError } = require('../GulpError');
const mocha = require('gulp-spawn-mocha');
const _ = require('lodash');

function taskFunction() {
    const config = this.config;
    const gulp = this.gulp;

    const TESTS_DIR = _.get(config, 'TESTS_DIR');

    if (!TESTS_DIR) {
        throw (new GulpError('TESTS_DIR config setting found.'));
    }

    const TESTS_SPLAT = `${TESTS_DIR}/**/*.test.js`;

    return gulp.src(TESTS_SPLAT)
        .pipe(mocha({
            bin: `${config.PROJECT_ROOT}/node_modules/mocha/bin/mocha`
        }));
}

module.exports = (context) => {
    registerTask(context, ['test'], taskFunction.bind(context));
};
