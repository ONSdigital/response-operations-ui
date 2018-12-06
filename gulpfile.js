import 'gulp'
import 'chalk'

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

gulp.task('test', [])

gulp.task('build')

gulp.task('watch')

// Tasks used by other tasks