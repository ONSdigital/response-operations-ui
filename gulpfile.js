
const gulp = require('gulp');
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
const { readdir } = require('fs');
const { promisify } = require('util');

const { GulpError } = require('./gulp/GulpError');

const packageJson = require('./package.json');
const config = _.get(packageJson, 'config.gulp', {});

const PROJECT_ROOT = __dirname;
const CONFIG = {
    SCSS_DIR:        _.get(config, 'SCSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    CSS_DIR:         _.get(config, 'CSS_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_SRC_DIR:      _.get(config, 'JS_SRC_DIR', '').replace('$ROOT', PROJECT_ROOT),
    JS_DEST_DIR:     _.get(config, 'JS_DEST_DIR', '').replace('$ROOT', PROJECT_ROOT),
    TASKS_DIR:       join(PROJECT_ROOT, 'gulp', 'tasks'),
    IS_DEBUG:        Boolean(process.env.DEBUG),
};

console.log('Loading Gulp Tasks');

const readDirAsync = promisify(readdir);
const initialiseTask = fileName => {
    const Task = require(fileName);

    console.log(Task);
    const task = new Task();
    console.log(task);
    const taskRunner = task.run.bind(Task, CONFIG);
    console.log(`Trying to register tasks ${task.names.join('/')}`);
    task.names.forEach(name => gulp.task(name, taskRunner));
    console.log(`Registered Gulp Task ${names.join('/')}`);
};

readDirAsync(CONFIG.TASKS_DIR)
    .then(files => {
        const jsFiles = files.filter(fileName => fileName.endsWith('.js'));
        if (jsFiles.length === 0) {
            throw new GulpError('No Gulp tasks found');
        }

        jsFiles
            .map(fileName => join(CONFIG.TASKS_DIR, fileName))
            .map(initialiseTask);
    })
    .catch(error => {
        throw error; // Only serves to avoid throwing a process.uncaughtException
    });

gulp.task('default', () => {
    console.log(`
    Usage:
        npm test       ${chalk.blue('Run the tests through the test harness')}
        npm build      ${chalk.blue('Run the frontend build')}
        npm run watch  ${chalk.blue('Run the watcher - actively recompile frontend during development')}
    `);
});

process.on('UnhandledPromiseRejectionWarning', function (...args) {
    console.log(args);
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
