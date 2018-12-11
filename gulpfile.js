const gulp = require('gulp')
const chalk = require('chalk')
const _ = require('lodash')

const package = require('./package.json')
const config = _.get(package, 'config.gulp', {})

const PROJECT_ROOT = __dirname

const SCSS_DIR =    _.get(config, 'SCSS_DIR').replace('$ROOT', PROJECT_ROOT)
const CSS_DIR =     _.get(config, 'CSS_DIR').replace('$ROOT', PROJECT_ROOT)
const JS_SRC_DIR =  _.get(config, 'JS_SRC_DIR').replace('$ROOT', PROJECT_ROOT)
const JS_DEST_DIR = _.get(config, 'JS_DEST_DIR').replace('$ROOT', PROJECT_ROOT)

// Default task
gulp.task('default', () => {
    console.log(`
    Usage:
        npm test       ${chalk.blue('Run the tests through the test harness')}
        npm build      ${chalk.blue('Run the frontend build')}
        npm run watch  ${chalk.blue('Run the watcher - actively recompile frontend during development')}
    `);
})

// Main functions

function returnNotImplemented() {
    console.warn('function not implemented')
}

gulp.task('test', returnNotImplemented)

gulp.task('build', returnNotImplemented)

gulp.task('watch', returnNotImplemented)

gulp.task('lint', returnNotImplemented)

// Sub tasks

gulp.task('_csslint', () => {

})

gulp.task('_jslint', returnNotImplemented)

gulp.task('_bundlejs', returnNotImplemented)

gulp.task('_scsscompile', returnNotImplemented)

gulp.task('_stylelint', returnNotImplemented)