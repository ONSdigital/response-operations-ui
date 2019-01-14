
const gulp = require('gulp');
const gutil = require('gulp-util');

const chalk = require('chalk');
const _ = require('lodash');
const { join } = require('path');
const { readdirSync } = require('fs');

const { GulpError } = require('./gulp/GulpError');
const { addErrorHandlingToGulpSrc, registerTask } = require('./gulp/gulpHelper');

const packageJson = require('./package.json');
const config = _.get(packageJson, 'config.gulp', {});

const PROJECT_ROOT = __dirname;
const CONSTANTS = {
    SCSS_DIR:        _.get(config, 'SCSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    CSS_DIR:         _.get(config, 'CSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_SRC_DIR:      _.get(config, 'JS_SRC_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_DEST_DIR:     _.get(config, 'JS_DEST_DIR', '').replace('$ROOT', PROJECT_ROOT),
    TASKS_DIR:       join(PROJECT_ROOT, 'gulp', 'tasks'),
    IS_DEBUG:        !Boolean(process.env.node_env === 'production'),
    PROJECT_ROOT
};

const context = {
    config: CONSTANTS,
    gulp,
    GulpError,
    logger: gutil.log
};

context.logger('Loading Gulp Tasks');

addErrorHandlingToGulpSrc(context);

let tasksAdded = 0;
const initialiseTask = fileName => {
    const taskInitialiser = require(fileName);
    taskInitialiser(context);
    tasksAdded++;
};

const taskFiles = readdirSync(CONSTANTS.TASKS_DIR)
    .filter(fileName => fileName.endsWith('.js'))
    .map(fileName => join(CONSTANTS.TASKS_DIR, fileName));

if (taskFiles.length === 0) {
    throw new GulpError('No tasks found');
}

taskFiles.map(initialiseTask);

registerTask(context, ['build'], context.gulp.series(['csslint', 'scss_compile']));

context.logger(`Added ${tasksAdded} tasks`);

gulp.task('default', (callback) => {
    console.log(`
    Usage:
        gulp                 ${chalk.blue('Display this message')}
        gulp [taskname]      ${chalk.blue('Run the named gulp task')}

    Available tasks: ${Object.keys(context.gulp._registry._tasks).join(', ')}
    `);

    callback();
});
