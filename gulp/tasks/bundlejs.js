const { registerTask } = require('../gulpHelper');
const webpack = require('webpack-stream');
const { join } = require('path');
const { get } = require('lodash');

function taskFunction() {
    const JS_SRC_DIR = get(this, 'config.JS_SRC_DIR');
    const JS_DEST_DIR = get(this, 'config.JS_DEST_DIR');

    if (!JS_SRC_DIR) {
        throw (new GulpError('JS_SRC_DIR config setting not found'));
    }

    if (!JS_DEST_DIR) {
        throw (new GulpError('JS_DEST_DIR config setting not found'));
    }

    return this.gulp.src(join(JS_SRC_DIR, '*.js'))
        .pipe(webpack())
        .pipe(this.gulp.dest(join(JS_DEST_DIR)));
}

module.exports = (context) => {
    registerTask(context, ['bundlejs', 'bundle'], taskFunction.bind(context));
};
