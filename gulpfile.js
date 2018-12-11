const gulp = require('gulp')
const gulpStylelint = require('gulp-stylelint')
const gulpAutoPrefixer = require('gulp-autoprefixer')
const gulpBabel = require('gulp-babel')
const gulpEsLint = require('gulp-eslint')
const gulpSass = require('gulp-sass')
const gulpMocha = require('gulp-mocha')

const chalk = require('chalk')
const _ = require('lodash')
const process = require('process')

const package = require('./package.json')
const config = _.get(package, 'config.gulp', {})

const PROJECT_ROOT = __dirname

const SCSS_DIR =    _.get(config, 'SCSS_DIR', '').replace('$ROOT', PROJECT_ROOT)
const CSS_DIR =     _.get(config, 'CSS_DIR', '').replace('$ROOT', PROJECT_ROOT)
const JS_SRC_DIR =  _.get(config, 'JS_SRC_DIR', '').replace('$ROOT', PROJECT_ROOT)
const JS_DEST_DIR = _.get(config, 'JS_DEST_DIR', '').replace('$ROOT', PROJECT_ROOT)

/**
 * Temporary function to placehold those not yet implemented
 */
function returnNotImplemented() {
    throw GulpError('This function is not yet implemented!')
}
class GulpError extends Error {
    constructor(message, fatal = true) {
        super()
        this.message = message
        this.fatal = fatal
    }
}

try {
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


    gulp.task('test', returnNotImplemented)

    gulp.task('build', returnNotImplemented)

    gulp.task('watch', () => {
        // TODO: Watch task
        // 
        return returnNotImplemented()
    })

    gulp.task('lint', ['jslint', 'csslint'])

    // Sub tasks
    gulp.task('csslint', () => {
        if (SCSS_DIR === ''){
            throw (new GulpError('SCSS_DIR config setting not found'))
        }

        try {
            const styleLintSettings = require('./.stylelintrc')
        } catch (e) {
            throw new GulpError('stylelintrc file missing')
        }

        return gulp
            .src(SCSS_DIR)
            .pipe(gulpStyleLint(styleLintSettings))
    })

    gulp.task('jslint', returnNotImplemented)

    gulp.task('mocha', returnNotImplemented)

    gulp.task('bundlejs', returnNotImplemented)

    gulp.task('transformjs', returnNotImplemented)

    gulp.task('browserify', returnNotImplemented)

    gulp.task('scsscompile', returnNotImplemented)

    gulp.task('stylelint', ['csslint'])

}
catch (error) {
    if (!error instanceof GulpError) {
        throw error // Trace out unexpected errors
    }

    console.log(`${chalk.white.bgRed('ERROR:')} Gulp encountered a build error: ${chalk.white(error.message)}`)

    if (error.fatal) {
        console.log('Stopping')
        process.end(1);
    }
}