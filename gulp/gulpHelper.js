const { GulpError } = require('./GulpError');
const plumber = require('gulp-plumber');
const chalk = require('chalk');
const _ = require('lodash');

function returnNotImplemented() {
    throw new GulpError('This function is not yet implemented!');
}

function registerTask(context, names, taskFunction) {
    names.map(name => context.gulp.task(name, taskFunction));
}

function addErrorHandlingToGulpSrc(context) {
    const gulpSrcCopy = context.gulp.src;
    context.gulp.src = function(...args) {
        return gulpSrcCopy.apply(context.gulp, args)
            .pipe(plumber(error => {
                context.logger(_formatErrorMessage(error));
                this.emit('end');
            }));
    };
}

const finishedTaskHandler = (stream, callback) => {
    stream.on('error', (...args) => callback)
    stream.on('end', (...args) => callback)
    stream.on('finish', (...args) => callback);
};

function _formatErrorMessage(error, title = 'Error') {
    const erroredPlugin = _.get(error, 'plugin', false);
    let outputString = '';

    outputString += `${chalk.bgRed.white(title)} `;

    if (erroredPlugin) {
        outputString += `${chalk.blue('[PLUGIN: ' + erroredPlugin + '] ')}`;
    }

    outputString += error.message;

    return outputString;
}

module.exports = {
    returnNotImplemented,
    registerTask,
    addErrorHandlingToGulpSrc,
    finishedTaskHandler
};
