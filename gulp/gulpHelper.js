const { GulpError } = require('./GulpError');

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
                context.logger(error.message);
                this.emit('end');
            }));
    };
}

module.exports = {
    returnNotImplemented,
    registerTask
};
