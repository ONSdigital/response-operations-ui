
const gulp = require('gulp');
const gutil = require('gulp-util');
// const gulpStyleLint = require('gulp-stylelint');
// const gulpAutoPrefixer = require('gulp-autoprefixer');
// const gulpSourcemaps = require('gulp-sourcemaps');
// const gulpCleanCss = require('gulp-clean-css');
// const gulpBabel = require('gulp-babel');
// const gulpEsLint = require('gulp-eslint');
// const gulpSass = require('gulp-sass');
// const gulpMocha = require('gulp-mocha');

// const transform = require('vinyl-transform');

const chalk = require('chalk');
const _ = require('lodash');
const { join } = require('path');
const { readdirSync } = require('fs');

const { GulpError } = require('./gulp/GulpError');
const { addErrorHandlingToGulpSrc } = require('./gulp/gulpHelper');

const packageJson = require('./package.json');
const config = _.get(packageJson, 'config.gulp', {});

const PROJECT_ROOT = __dirname;
const CONSTANTS = {
    SCSS_DIR:        _.get(config, 'SCSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    CSS_DIR:         _.get(config, 'CSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_SRC_DIR:      _.get(config, 'JS_SRC_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_DEST_DIR:     _.get(config, 'JS_DEST_DIR', '').replace('$ROOT', PROJECT_ROOT),
    TASKS_DIR:       join(PROJECT_ROOT, 'gulp', 'tasks'),
    IS_DEBUG:        Boolean(process.env.DEBUG),
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

context.logger(`Added ${tasksAdded} tasks`);

gulp.task('default', () => {
    console.log(`
    Usage:
        gulp                 ${chalk.blue('Display this message')}
        gulp [taskname]      ${chalk.blue('Run the named gulp task')}

    Available tasks: ${Object.keys(context.gulp.tasks).join(', ')}
    `);
});

// Main functions
// gulp.task('test', returnNotImplemented);

// gulp.task('build', returnNotImplemented);

// gulp.task('watch', () => {
//     gulp.watch(`${SCSS_DIR}/**/*.{css,scss}`, ['csslint', 'scsscompile']);
// });

// gulp.task('lint', ['jslint', 'csslint']);

// // Sub tasks
// gulp.task('csslint', () => {
//     if (SCSS_DIR === '') {
//         throw (new GulpError('SCSS_DIR config setting not found'));
//     }

//     const styleLintSettings = {
//         failAfterError: true,
//         debug: IS_DEBUG,
//         reporters: [
//             {formatter: 'verbose', console: true}
//         ]
//     };

//     console.log(SCSS_DIR);

//     return gulp
//         .src(`${SCSS_DIR}/**/*.{scss,css}`)
//         .pipe(gulpStyleLint(styleLintSettings));
// });

// gulp.task('jslint', () => {

// });

// gulp.task('mocha', returnNotImplemented);

// gulp.task('bundlejs', returnNotImplemented);

// gulp.task('scsscompile', () => {
//     gulp.src(`${SCSS_DIR}/main.scss`)
//         .pipe(gulpSourcemaps.init())
//         .pipe(gulpSass())
//         .pipe(gulpAutoPrefixer())
//         .pipe(gulpCleanCss())
//         .pipe(gulpSourcemaps.write(CSS_DIR))
//         .dest(CSS_DIR + '/main.css');
// });
