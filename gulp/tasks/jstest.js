const { registerTask } = require('../gulpHelper');
const { exec } = require('child_process');
const { join } = require('path');

function taskFunction(callback) {
    const jestConf = join(this.config.PROJECT_ROOT, 'jest.config.js');

    try {
        exec('npx jest --config ' + jestConf, (error, _, stderr) => {
            console.log(stderr);
            callback(error);
        });
    } catch (error) {
        console.error(error);
        callback(error);
    }
}

module.exports = (context) => {
    registerTask(context, ['jstest'], taskFunction.bind(context));
};
