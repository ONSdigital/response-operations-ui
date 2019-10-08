# Bundling with Webpack and Babel      <!-- omit in toc -->

## Achieving modularised and modernised Javascript/ECMAScript by using bundlers and transpilers <!-- omit in toc -->

- [What is a bundler](#What-is-a-bundler)
  - [Time to first byte - TTFB](#Time-to-first-byte---TTFB)
  - [This is where bundlers come in](#This-is-where-bundlers-come-in)
- [What is a transpiler](#What-is-a-transpiler)
- [Webpack](#Webpack)
- [Babel](#Babel)
- [Our own use of Webpack and Babel](#Our-own-use-of-Webpack-and-Babel)

### What is a bundler
In frontend Javascript, browsers offer no system to include Javascript in various modules, and create a single file from it to load in the production site.  Whilst we could put in something like this:

```html
<script src="path/to/module1"></script>
<script src="path/to/module2"></script>
<script src="path/to/module3"></script>
<script src="path/to/module4"></script>
```

this is not a good idea for several reasons:

- We are loading the scripts into the DOM in order, but we aren't addressing how they interact.  If `module1` executes immediately, and makes reference to `module4` before it has loaded, an error will be thrown that is needlessly complex to deal with.
- We have to think very carefully about the dependencies of each part of our code, and whether its dependencies are available.  We can fix this with dependency injection systems like `require.js`, but it's better overall to just have a simpler system
- If we load 4 files instead of 4, we may load the _exact_ same amount of code, but we won't load it as fast due to TTFB, see below.

#### Time to first byte - TTFB

When a webpage loads an asset, it makes an HTTP/HTTPS request to the server for the asset, and this involves several steps:

- A DNS lookup of the server
- A request to the server
- Negotiation of a connection (SYN, SYN-ACK, ACK in TCP.  More steps added for TLS)
- First response from the server
- Resource sent from the server
- End of receipt from the server

Of those, only the last two are the same for identical data.  The DNS, request, negotiation etc, whilst they may be sped up by caching of DNS after the first request, will be repeated for each separate request.  After the connection negotiation, the delay until the data starts arriving is the TTFB (Time To First Byte), and multiple requests will always add extra time through this.

Because of this, loading extra scripts means a certain amount of extra time to load.  For example, the ONS homepage, loaded from my home today, loads 27 assets, the first of which is the HTML page markup.  Each load _after_ first byte takes no more than 100ms (generally more like 40ms), so the load time from the server is negligible, but the DNS lookup, negotiations, and TTFB take much longer.

Connections happen sequentially, up to whatever limit the server can either manage/has configured, but the loading of all assets took 5.5 seconds, of which around 60% was waiting for new connections.

In short, the more that can be loaded in one request (technically, it's everything, but this target is not realistic), the better for load times, so we try to minimise how many separate scripts and assets we load separately.

#### This is where bundlers come in

In a typical modern frontend application, you will have several Javascript files, some from external sources, some unique to you application, and several files for CSS - usually written in a [transpiled](#What-is-a-transpiler) language like SCSS or LESS.  Whilst, as seen, these can be loaded separately, it's usually much better to load one file, containing compressed content.

A bundler can achieve this.  It takes the many files needed for the frontend to work, and creates one file of all of them that is as compressed as possible, for quick transfer.

Methods used by bundlers to do this:

- Simple concatenation of files - especially true of CSS
- Use of compression techniques like variable renaming, whitespace removal etc
- Static analysis of files to find opportunities for further optimisation
- Plugins to achieve extra functionality.

With regards to that last point, plugins are used by bundlers to add functionality to their processes.  We use plugins for our bundler [Webpack](#Webpack) to achieve the following extra features:

- Rewriting [Modern Javascript](Modern-JS-features.md) to Javscript that offers the same functions, but is operable with more browsers - this is for ease of development without sacrificing cross-browser functionality
- [Transpiling](#What-is-a-transpiler) SCSS to CSS - this is also for ease of development without sacrificing cross-browser functionality

The bundler outputs a single file, which is a compressed version of the Javascript files in the repo, with transformations to more crossbrowser code, and compressed as far as possible.

### What is a transpiler

Transpilation is similar to compilation, but rather than taking the steps that a compiler takes:

* Static analysis
* Tokenisation
* Reduction down to machine code/byte code
* Writing of binary

...or whatever variant of that a specific compiler does, _transpilation_ is taking a high level language, and rewriting it according to comparatively simple rules to another fairly high level language.

The main difference being that the output of a compiler will either be binary code or bytecode that can be run quickly and simply by a runtime; but the output of a transpiler will still need extensive JIT or JIT-style work to run, or use.

For example, the CSS language variant SCSS is not converted into an optimised style description language, it's just made into standard CSS.

Transpiled languages are used to add features to languages that speed up or otherwise improve development, rather than affect performance at use.  For this reason, they are only suitable for use when the transpiled output is already performant enough, or where changing the transpiled language could achieve the performance improvements needed.

In short, transpiled languages are almost entirely aimed at improving development rather than anything else.  In a sense though, all compilers only take one set of instructions and turn it into another.  Transpilers are notable, however, because they don't turn a language into a lower level language, just a different high level language.

We use transpilers to rewrite SCSS as CSS, and up to date Javascript as older style Javscript - this is covered in details in the document [Modern JS features](Modern-js-features.md).

### Webpack

Webpack is our bundler.  Of the currently popular bundler systems, it is the most popular as most supported.  Others include:

- Rollup.js
- Bundle.js
- Browserify

Webpack, out of the box, takes Javascript written in modules, and bundles it together into a single file for consumption in the frontend.  We've written a Webpack config that introduces a Javascript transpiler tool called [Babel](#Babel) to turn the modern JS we write into older fashioned, better supported Javascript.

Webpack can also do many other things, and has thousands of available plugins, but we currently only use it for JS bundling.  Our SCSS bundling is done by a [Gulp](Gulp.md) task.

### Babel

Babel is a 'translator' or transpiler that takes the Javascript you write, and re-writes it to make avoid using newer, unsupported features.  Use of Babel can allow you to write cutting edge Javascript, and have Babel convert it its into older, widely supported equivalent.

Babel can be setup by use of a `.babelrc` file that makes alterations to it's settings.  Things that can be changed include:

- Which environments Babel is setup to support
- Which Babel plugins are used

Babel previously supported importing modules, but now works inline with other tools to do this.

### Our own use of Webpack and Babel

Our use of Webpack and Babel is implemented through the existing [Gulp](Gulp.md) task runner:

- Webpack runs and imports included modules, and executes Babel to transpile them
- Gulp's `build` task runs webpack via a Gulp plugin
- Gulp's `bundle` task also runs webpack
- Gulp's `watch` task runs webpack only when the Javascript assets need recompiling - so it's useful during development

