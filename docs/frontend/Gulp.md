# Gulp <!-- omit in TOC -->
## Frontend task-runner / build system <!-- omit in TOC -->

- [Introduction to Gulp](#Introduction-to-Gulp)
- [Tasks](#Tasks)
  - [Tasks running tasks](#Tasks-running-tasks)
  - [Structure of tasks in `response-operations-ui`](#Structure-of-tasks-in-response-operations-ui)
    - [Dissecting the task in our format:](#Dissecting-the-task-in-our-format)
    - [The advantage of our format of task](#The-advantage-of-our-format-of-task)
- [Reading files](#Reading-files)
  - [Examples](#Examples)
  - [Outputs of a `gulp.src`](#Outputs-of-a-gulpsrc)
- [Writing Files](#Writing-Files)
- [Watching files](#Watching-files)
- [Plugins](#Plugins)
  - [Notes on choosing plugins](#Notes-on-choosing-plugins)
  - [Writing plugins](#Writing-plugins)

### Introduction to Gulp
Gulp.js is self-referred to as 'The Streaming Build System', and this is because it uses an approach of creating streams of assets to create
built assets for the frontend (in our case, can also be used for backend, but usually not in a Python environment).

`response-operations-ui` uses Gulp to automate the following frontend-centric tasks:

* Conversion of SASS-syntax CSS to standard CSS
* Conversion of modern Javascript syntax to syntax compatible with older browser (Transpilation)
* Bundling of Javascript modules
* Creation of minified versions of frontend assets like CSS and JS

Gulp does this by creation of tasks, and tasks can be run manually, or by defined triggers.  For instances, Gulp can watch code for changes, and then perform specified tasks, in sequence, or in parallel, with various levels of control over them.

### Tasks
Central to Gulp, are Gulp tasks - the jobs that Gulp does, these are defined using the `gulp.task` function, which takes a name, and a function that will be run as the task.  Typically, tasks will use one or more plugins to perform the task, such as a CSS minifier, a JS processor, and so on.

Tasks use [`gulp.src`]('#reading-files') to read input from a file, or from files, and use `pipe` to stream the output to processors, that adapt it, or create assets from it, and finally pipe the output to another place.  This is similar to using the `|` operator in a Unix/Linux system, to 'pipe' streamed output into another executable that can change it.

When a task has piped the inputs through all the stages it needs to, it will either generate output for the console (Like a test result, or linting output), or will write a new file or files.  Writing files uses the [`gulp.dest`](#writing-outputs) function.

A simple example task is below:

```javascript
const gulpSass = require('gulp-sass');

gulp.task('compile_scss', () => {
    gulp.src(`main.scss`)
        .pipe(gulpSass())
        .pipe(gulp.dest('./css'));
});
```

This task compiles SASS to CSS by using the `gulp-sass` library.  The steps are:

1. Reads the `main.scss` file, which is SCSS-syntax SASS.
2. Pipes the stream of the file into the `gulpSass` function, which reads the input, and outputs normal CSS.
3. Pipes the normal CSS to `gulp.dest` which writes a file into the `./css` directory.

This is how gulp tasks are created, and it's mostly very simple.  It can be complex in some cases, but when using a plugin like `gulp-sass`, the plugin will come with instructions on how to use it.

Tasks can be run by running Gulp, with the task name as an argument:

```
$ gulp compile_scss
```

The above assumes you have gulp installed globally, which you can do by running `npm i -g gulp-cli` (will need to install for each version of Node if you use a version manager), but you can use `npx` to run Gulp within the `response-operations-ui` repo, by prefixing the command with `npx`:

```
$ npx gulp compile_scss
```

You can use either approach, but the `npx` approach is better, because it will run the version of Gulp that is installed in the `node_modules` of the repo, meaning you have no need to globally install any tooling, and won't face any issues with version incompatibility.

Running `npx gulp` is roughly equivalent to running `node node_modules/.bin/gulp`, which is installed in the repo directory after install is run, so you should already have it.

#### Tasks running tasks
On many occasions, you may need to make a task that just runs other tasks.  For example, your build task may run tests, linters, and then asset compilers.  Rather than reuse code, just write tasks that do each of these steps, that can then be reused in other tasks.

A task that runs others can either run them in series of parallel, using `gulp.series` and `gulp.parallel`:

```javascript
gulp.task('build', gulp.series(['lint', 'test', 'compile_scss', 'bundle', 'minify']));
```

This runs the lint, test, compile_scss, bundle, and minify tasks, one after the other.  If any fail, an error will throw, and the series execution will stop.

Doing the same in parallel will run all of the tasks at once:

```javascript
gulp.task('build', gulp.parallel(['lint', 'test', 'compile_scss', 'bundle', 'minify']));
```

In this instance, if any fail, the others will still execute, but the exit code of the gulp task will be non-zero to highlight that something failed.

If you need to, you could have complex combination of parallel and series execution:

```javascript
gulp.task('build', gulp.parallel([
    gulp.series(['css_lint', 'scss_compile']),
    gulp.series(['js_lint', 'jsbundle')
]));
```

The above would start two parallel tasks, each running two tasks in series.  This could be useful for more quickly assembling the different types of assets in your app, say CSS, Javascript, Images, etc.; but it has some downsides:

* Pipelines can become needlessly complex, making finding issues harder
* A non-zero exit code means a series execution failed, but doesn't indicate which
* Whilst you can split things into seperate parallel queues of series tasks, it's harder to then combine the results at the end, say in order to minify all of them at once.  It can be done by wrapping the parallel tasks in a series task set, and then making the final task in the set perform the major final functions, but it looks messy, and isn't easy to understand at a glance.

Generally speaking, I'd recommend avoiding mixing parallel and series operations, unless your separate them out into other values to make the code cleaner, e.g.:

```javascript
const cssPipeline = gulp.series(['css_lint', 'scss_compile']);
const jsPipeline = gulp.series(['js_lint', 'jsbundle']);
const parallelPipeline = gulp.parallel([cssPipeline, jsPipeline]);

const wholePipeline = gulp.series([parallelPipeline, 'minify']); // Where 'minify' is a named task setup elsewhere.
```
This is easier to read, but it does lack the usefulness of piped streams - minify doesn't receive the output of `parallelPipeline`, it would have to be written to find it.

#### Structure of tasks in `response-operations-ui`
Tasks in `response-operations-ui` have a similar structure, but they have been written slightly differently to separate the tasks into their own files, which Gulp loads into memory in advance of trying to run tasks.

A Gulp task in the `response-operations-ui` repo takes this form:

```javascript
const { registerTask } = require('../gulpHelper');

function taskFunction() {
    // Task code goes here
}

module.exports = (context) => {
    registerTask(context, ['array', 'of', 'names'], taskFunction.bind(context));
};
```

Tasks are done this way to split the code into task files, and to allow tasks to have more than one name.

##### Dissecting the task in our format:
The task uses the `registerTask` function from `gulpHelper` (a custom helper written to help us manage multiple tasks well).  We make this available with this line.

```javascript
const { registerTask } = require('../gulpHelper'); // Take the 'regsiterTask' function from the gulpHelper, and call it 'registerTake' in this file.
```
...after which, the `registerTask` function will be available to use within the file.

The task must export a registered task, which looks like this, split into multiple lines for commentary reasons:

```javascript
module.exports = (context) => {  // module.exports is the syntax that lets you specify what a javscript module will export, in this case it's a function
    registerTask(
        context,                        // The context is an object of various functions and settings that can be used in the tasks, for instance context.config contains all the configuration settings for the Gulp system, and context.gulp contains the gulp library itself.
        ['names'],                      // This can be an array, or a string, and it's the name or names of the function.  If you pass many names, one task is created with several aliases that can be used to invoke it.
        taskFunction.bind(context)      // This is the function that will be run as the task.  It can be called anything, but all of ours are known as 'taskFunction', for consistency.  `.bind(context)` sends the context object to the function, where it will be the `this` object within the function.
        )
}
```

The use of a shared `context` object makes the structure of the `taskFunction` slighty different to the original example.  For instance, references to `gulp.src`, `gulp.dest` etc. would now become `this.gulp.src` `this.gulp.dest`.

A quick way to convert from the one style to the other is to make the first line of the `taskFunction` the following:

```javascript
const gulp = this.gulp;
```

...after which, `gulp` will be an available object again, and all the `gulp.*` functions will be available as in previous examples.

To explain this further, here is the example from before in our style of task definition:

```javascript
const gulpSass = require('gulp-sass');
const { registerTask } = require('../gulpHelper');

function taskFunction() {
    const gulp = this.gulp;

    return gulp.src(`main.scss`)
        .pipe(gulpSass())
        .pipe(gulp.dest('./css'));
}

module.exports = (context) => registerTask(context, 'compile_scss', taskFunction.bind(context));
```

Things to note about this are:

1. The `gulp.task` function is not used anymore.  This is because our custom helper deals with it, and loads all tasks into memory before attempting to run any, to make sure all dependencies are met.
2. The name for the task now goes as a parameter into `registerTask`, and can be either a string, or an array of aliases that call the same task
3. The task returns the `gulp.src` function - this helps the task runner know when a task has finished, and whether it was successful.

##### The advantage of our format of task
Our task format might seem more complicated, but it actually simplifies the process of adding a new task.  This is for a number of reasons:

* Adding a new task just involves writing a file like the above into the `gulp/tasks` directory.  Our custom code will load all tasks and will make them available to each other before running anything.  Thus, you only need to write one file, and it will add to the system automatically.
* The order of tasks no longer matters, whereas it could if these were all in one file
* The task has access to the `context` object, which includes
  * Our own instance of `gulp`, which shares information with all other tasks
  * A `config` object which contains any configurable items you may need (these can be set in `package.json`, see example snippet below)
  ```json
  "config": {
        "gulp": {
            "SCSS_DIR": "$ROOT/response_operations_ui/assets/scss",
            "CSS_DIR": "$ROOT/response_operations_ui/static/css",
            "JS_SRC_DIR": "$ROOT/response_operations_ui/assets/js",
            "JS_DEST_DIR": "$ROOT/response_operations_ui/static/js"
        }
    }
    ```
  * A logger for sending output to the console/user.  Use `context.logger.warn`, `context.logger.error`, `context.logger.log` or `context.logger.debug`, to output different loglevel messages in your tasks.


### Reading files
Usually, Gulp tasks will read files to perform whatever task they must do.  This uses the `gulp.src` function which converts file inputs into streams that can be piped through processors and other functions.

`gulp.src` can read specific files, or take wildcard-based inputs to read any files that match various patterns.  It can also take an array of patterns to match differing locations.  These patterns are called 'globs' and they are common in Unix and Linux systems for matching files.

#### Examples

```javascript
gulp.src('this.file')       // Matches only the file named 'this.file' in the current directory (directory is relative to the root of the project)
```

```javascript
gulp.src('*.js')            // Matches every file ending with '.js' in the current directory
```

```javascript
gulp.src('**/*.js')         // Matches every file ending with '.js' in any directory including current directory or a descendent (but not a parent)
```

```javascript
gulp.src(['**/*.js', '**/*.ts'])    // Matches any file in or descending from the current directory that end in '.js' or '.ts'
```

```javascript
gulp.src('!(*.js)')         // Matches files (current directory) that don't end in '.js'
```

Globs have a lot of variations, and you can find more explanation and links [here](https://gulpjs.com/docs/en/getting-started/explaining-globs)

#### Outputs of a `gulp.src`
`gulp.src` outputs a stream (called a [vinyl stream](https://github.com/gulpjs/vinyl)), that can be piped into any number of plugins and functions in a chain:

```javascript
gulp.src('glob')
    .pipe(thing1)
    .pipe(thing2)
    .pipe(thing3)
    .pipe(anOutputThing)
```

The chain above takes the files that match 'glob', pipes them into `thing1` which then outputs something else, and pipes to `thing2`, `thing3` etc.

The `thing*`s may take the input, and change it to something else, or they may just be used to assess it somehow.  A test system will likely not change the output, but rather change the exit code to block the pipeline if it was broken.  A compiler or transpiler will take the input and change it - passing the changed version down to the next.

This can be confusing as a concept, but when thought of as a 'pipeline' in the build system sense, it makes more sense.  Each stage is like a stage in a system like Jenkins, or another CI system.  Gulp could be used as a CI system, but it's usually not, because CI systems like Travis, Jenkins and Circle have many more features, and provide a server to deploy from, where Gulp does not.  Gulp is best used as a tool run by the developer and the CI, to run certain tasks.

### Writing Files

If your task outputs to a file, you pipe the output to `gulp.dest` and pass this arguments to specify where the file should write to:

```javascript
gulp.src('glob')
    .pipe(aPlugin)
    .pipe(gulp.dest('a file location'))
```

The above follows these steps:

1. Read all the files that match 'glob'.  This could be something like `*.css` or `*.js`.
2. Convert those files to a stream, and pipe it to `aPlugin` function - this could be a minifier, a compiler etc.
3. `aPlugin` takes the input and makes whatever changes it needs, and outputs a stream of the modified data.
4. Stream is piped to `gulp.dest` which writes it to 'a file location', which is typically a directory, but can as specific as a file.

### Watching files

Like `gulp.src`, `gulp.watch` can take a glob to match files, and also takes a function to run upon a change to those files.  This is handy for writing tasks that can run during development, and run tests, linters, and asset compilers.

A watch function takes this form:

```javascript
gulp.watch('glob', functionToCallWhenFilesInGlobChange);
```
Where `functionToCallWhenFilesInGlobChange` is a function that would be called on the file changes, and is typically just a separately defined task.

The example below shows the running of the task we used as example in [the tasks section of this guide](#tasks), written as a watcher.

```javascript
const gulpSass = require('gulp-sass');
const { registerTask } = require('../gulpHelper');

function taskFunction() {
    const gulp = this.gulp;

    gulp.watch('**/*.scss', () => {
        return gulp.src(`main.scss`)
            .pipe(gulpSass())
            .pipe(gulp.dest('./css'));
    })

}

module.exports = (context) => registerTask(context, 'watch_scss', taskFunction.bind(context));
```

Worthy of note, though, is that a watcher would normally run pre-existing tasks, rather than implement them in-function.  This allows better code reuse.  For example, our earlier example, creating the `compile_scss` task could be added to a watcher like this:

```javascript
const { registerTask } = require('../gulpHelper');

module.exports = (context) => registerTask(context, 'watch_scss', context.gulp.watch('**/*.scss', 'scss_compile'));
```

You can pass either a task function or a string name of a task to `gulp.watch`.  If you need to run several tasks, to you run them in parallel or series, see [Tasks running tasks](#tasks-running-tasks)

### Plugins
One of the central facets of Gulp is the ability to add plugins to achieve the tasks you want to acheive.  Out of the box, Gulp can [read files to a stream](#Reading-files), [pipe them to other functions, and write them to outputs](#Writing-Files) - it doesn't have any built-in processors to achieve the build changes you might need.

If you want, you can write custom functions that manipulate Gulp streams coming through, or you can use plugins, of which there are thousands.  Our system, at time of writing uses:

* [gulp-autoprefixer](https://www.npmjs.com/package/gulp-autoprefixer) - Adds css prefixes for legacy browser support
* [gulp-clean-css](https://www.npmjs.com/package/gulp-clean-css) - 'Cleans up' CSS - a formatter.
* [gulp-eslint](https://www.npmjs.com/package/gulp-eslint) - Allows us to run our ECMAScript linter in gulp tasks
* [gulp-jest](https://www.npmjs.com/package/gulp-jest) - Allows us to run the Jest test framework that we use for unit testing javascript
* [gulp-plumber](https://www.npmjs.com/package/gulp-plumber) - Allows us to pass gulp outputs to functions that _aren't_ gulp plugins.
* [gulp-sass](https://www.npmjs.com/package/gulp-sass) - Allows us to compile SASS/SCSS to CSS
* [gulp-sourcemaps](https://www.npmjs.com/package/gulp-sass) - Allows us to create sourcemaps, to allow debugging of decompiled code, whilst running compiled code.
* [gulp-stylelint](https://www.npmjs.com/package/gulp-stylelint) - Allows us to run Stylelint - a linter for CSS.
* [gulp-util](https://www.npmjs.com/package/gulp-util) - A collection of useful extra utilities for Gulp.

#### Notes on choosing plugins
Because anyone could write and publish a Gulp plugin, and because they are vital to our frontend builds, it is important to choose plugins carefully, considering the popularity and maintenance of them.  Below are useful tips, and these can apply to choosing any external dependency for any project:

* Look at how recently, and how frequently, the library is released.  If it's not been released recently, it may not be under active development, and may be problematic; if it isn't release often, it may take a long time for fixes to occur.
* Look at the repository for the library and see what - and how many - issues are reported.  If there are lots for a relatively young library, or there are many of the same type, you may end up having to maintain the library yourself, and that's a consideration

Finally, when adding libraries, `npm` will give you audit data of known issues, run `npm audit` for very detailed info, and assess problems, act as required.

#### Writing plugins
If you want or need to, you can write your own Gulp plugins.  At it's heart, a gulp plugin is a function that takes a `vinyl` object, and returns another `vinyl` object.  `vinyl` objects are objects that describe a number of files, and you can take the files, change them, and output a new set of files in a new `vinyl` object.

From there, everything is relatively straightforward.

Further reading:

* [Using Gulp Plugins](https://gulpjs.com/docs/en/getting-started/using-plugins)
* [Vinyl](https://gulpjs.com/docs/en/api/vinyl)
