const { registerTask } = require('../gulpHelper');
const jest = require('gulp-jest').default;
const _ = require('lodash');
const { join } = require('path');

function taskFunction() {
    const config = this.config;
    const jestConf = require(join(config.PROJECT_ROOT, 'package.json')).jest;
    const testMatchGlobs = jestConf.testMatch.map(match => `${config.PROJECT_ROOT}/${match}`);

    return this.gulp.src(testMatchGlobs).pipe(jest(jestConf));
}

module.exports = (context) => {
    registerTask(context, ['test'], taskFunction.bind(context));
};
