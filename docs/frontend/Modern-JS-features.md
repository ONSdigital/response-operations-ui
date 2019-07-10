# Modern Javascript Features                                            <!-- omit in toc -->
## Allowing frontend development using up to date Javascript features   <!-- omit in toc -->

- [Introduction](#Introduction)
- [Tooling](#Tooling)
  - [Babel](#Babel)
- [ECMAScript modern features](#ECMAScript-modern-features)
  - [Arrow functions](#Arrow-functions)
    - [Passing functions as predicates](#Passing-functions-as-predicates)
    - [Differences between arrow functions and typical functions](#Differences-between-arrow-functions-and-typical-functions)
  - [String interpolation](#String-interpolation)
  - [Classes](#Classes)
  - [`async` and `await`](#async-and-await)
    - [Basic asynchronous functions](#Basic-asynchronous-functions)
    - [Blocking vs non-blocking functions](#Blocking-vs-non-blocking-functions)
    - [Using `async` and `await` to write more concise code](#Using-async-and-await-to-write-more-concise-code)
      - [Asynchronicity libraries (Like async.js)](#Asynchronicity-libraries-Like-asyncjs)
      - [Promises](#Promises)
      - [`async` and `await` syntactic sugar](#async-and-await-syntactic-sugar)
  - [Modules](#Modules)
    - [CommonJS](#CommonJS)
    - [AMD - Asynchronous Module Definition](#AMD---Asynchronous-Module-Definition)
    - [ECMAScript modules](#ECMAScript-modules)

### Introduction
Javscript, correctly known as ECMAScript, has advanced at a fast pace in recent years, adding features like:

* Native promises
* `async`/`await` syntactic sugar to allow synchronous-style asynchronous programming
* Lambda-type, 'arrow functions' similar to delegates in C#, and lambdas in Python or Java
* Native classes - syntactic sugar to write classes rather than prototype objects.
* Modules - to separate out code into manageable chunks.
* `const` and `let` variable declarators to declare at block, rather than global, level

These features allow quicker writing of Javascript, and writing of more understandable and readable code.

### Tooling

Because Javascript has introduced new features at such a fast pace in recent years, the support for new features in both Node and browsers is behind the current specification.  This means that, before we use features, we have to convert them into other code that performs the same task, but that doesn't use the modern syntax where it wouldn't be supported.

#### Webpack
Webpack is a bundling system that allows us to take separate javascript files, and use them as modules to create one overarching javascript application for the front end of the system.

Webpack is run by Gulp using 'build', 'bundle', or 'watch' tasks - the 'watch' task will only run Webpack when the Javascript files are changed

_Javascript files in the `gulp` directory do not bundle, however Gulp does support module use anyway, because it isn't browser-based_

#### Babel
Babel is a language translator for Javascript that can be set up to translate new syntax into old syntax equivalents.  For example, Babel will take a Javascript class, and covert it into a function with prototype:

```javascript
class Animal {
    constructor(name) {
        this.name = name
    }

    greet() {
        console.log(`Hi, ${this.name}`);
    }
}

const myDog = new Animal('dog');

myDog.greet(); //outputs 'Hi, dog'
```

Translated version might be something like this, depending on support requirements:

```javascript
function Animal(name) {
    this.name = name;
}

Animal.prototype.greet = function() {
    console.log('Hi, ' + this.name)
}

var myDog = new Animal('dog');

myDog.greet();
```

You can see that the above has done the following steps:
* Replaced the class with a function - a function called with `new` in Javascript is a constructor.
* Replaced the greet function with a similar function that is a member of `Animal.prototype` - `prototype` is an object used to create new objects.
* Removed the string interpolation in `greet` and replaced it with concatenated strings
* Change the use of `const` to `var`.  Some older browsers don't support `const`.

> **Side note**: The above shows why `this` in Javascript behaves differently than expected.  Although in a class, you expect `this` to refer to an instance of a class, the way that objects are created with constructors is only _emulating_ classes - the functions are actually separate functions, so the reference to `this` which in Javascript refers to the scope the function exists within is not a reference to the class.

Babel will behave differently depending on its settings, which in our repo are passed in the `webpack.config.js` file.  We use `babel/preset-env` to dictate which environments we support, and therefore need translated

### ECMAScript modern features
The use of Webpack and Babel to process our Javascript means we can use modern JS features expained in the following sections.

#### Arrow functions
Many languages have the concept of something similar to arrow functions.  Python, for example, has lambda functions, C# and Java have predicate functions, and PHP and old-style Javascript have 'inline' or 'anonymous' functions.

Arrow functions are handy for a number of things, but they also behave slightly differently to standard functions.  See some examples below

##### Passing functions as predicates
A predicate is a function passed as an argument to be called by the function it's being passed to when something happens.  One common Javascript example is a _callback_, which is passed to be called on completion:

```javascript
function getData(callback) {
    request.get('url/to/data', callback)
}

getData(function (error, data) {
    if (error) throw error;

    populateUIWithData(data);
})
```

The same with an arrow function could be:

```javascript
const getData = callback => request.get('url/to/data', callback);

getData((error, data) => {
    if (error) throw error;
    populateUIWithData(data);
})
```

Equally, arrow functions are useful for array methods:

```javascript
[0,1,2,3,4].map(function (n) { return n*2; }) // returns [0,2,4,6,8]
```

```javascript
[0,1,2,3,4].map(n => n*2); // returns [0,2,4,6,8]
```

##### Differences between arrow functions and typical functions

Firstly, arrow functions have _implicit returns_.  If you create an arrow function, and don't surround the body in prentheses, then whatever the value you put after the arrow is, is returned.  These functions all behave identically:

```javascript

function square(n) {
    return n*n;
}

const square = n => {
    return n*n;
}

const square = n => n*n;
```

Secondly, arrow functions only require brackets around the arguments if there are multiple arguments:

```javascript
const square = n => n*n; // Needs no brackets because there is only one argument

const square = (n) => n*n; // Still works with brackets, if you want to use them

const multiply = (a, b) => a * b; // Needs brackets to make the runtime understand.
```

Thirdly, arrow functions do not feature the 'special' variables that standard functions do:

```javascript
function showArgs() {
    console.log(arguments);
}

showArgs(1,2,3) // logs the arguments to the console
```
vs.
```javascript
const showArgs = () => console.log(arguments);

showArgs(); // Throws a ReferenceError
```

> The reason that special variables don't exist in arrow functions is because of the next difference - arrow functions don't have their own scope in the same way.

Finally, arrow functions inherit the `this` value in play when they are called, rather than encapsulating their own:

```javascript

const arrowFunc = () => console.log(this);

function notArrowFunc() {
    console.log(this);
}

function myFunction() {
    arrowFunc();        // Logs an empty object, the `this` value of `myFunction`

    notArrowFunc();     // Logs the global object in play.  In a browser, this would be `window`
}

myFunction();
```

This behaviour of arrow functions makes them ideal for writing functions within functions that can access the same `this` value.

#### String interpolation
ECMAScript recently introduced template strings, which are a form of string interpolation similar to Python's string interpolation.  See below an example of old string concatenation followed by a template string version.

```javascript
const name = 'Owen';
const age = 36;

console.log('Hi, ' + name + ', you are ' + age + ' years old');
console.log(`Hi, ${name}, you are ${age} years old`);
```

In addition to this, strings defined using the `\`` character, have other useful properties:
* Can be written containing quote marks easily, without escaping `\`I guess that "works"\``
* Can be multiline, which quote delimited strings can't.

#### Classes
Classes are now available in Javascript, as they are in many languages, however there is a key difference in Javascript.  Javascript classes are not a separate entity, or type, but are syntactic sugar for creating a constructor object with a prototype for building it.  This doesn't mean too much when writing the, but understanding the `prototype` object is important to writing Javascript overall.

A class in JS looks like this:
```javascript
class myClass {
    constructor(args) {
        // constructor actions here
    }

    publicFunction() {
        // function that will become part of the constructed instance
    }

    static publicFunction() {
        // a static public function.
    }
}
```

Like in other languages, classes can be extended from others:

```javascript
class Animal {
    // class stuff
}

class Dog extends Animal {
    // Dog class stuff
}
```

Unlike function constructed instances, classes can only directly inherit from one other class, whereas functions can inherit from the prototypes of many others.  Whilst possible, this probably isn't a good idea, as it could allow some ridiculous combinations, that contradict each other, and essentially break.

You could for example, make a custom array using `class` in order to add functions you find handy:

```javascript
class BetterArray extends Array {
    lengthIsEven() {
        return this.length % 2 === 0;
    }
}
```

and that would work fine.

Using prototypal inheritance, you can extend multiple prototypes, and create _monsters_ of objects:

```javascript
function StringArray() {

}

Object.assign(StringArray.prototype, String.prototype, Array.prototype);
```

At this point, you have a String/Array hybrid, with functions for both strings and arrays.  Instantiating it with any value should not work, and any members that have common names will essentially be destroyed.

In short, whilst multiple inheritance can be done, it's _best avoided_!

#### `async` and `await`

Javascript is famous for the fact that it is an _asynchronously_ written language in many cases.  This often leads to confusion, as commands may execute in a different order to that in which they are written - in massive difference to most other languages.

##### Basic asynchronous functions

Below is an example of execution in unexpected order:

```javascript
function asyncFunc1() {
    setTimeout(() => {
        console.log('1');
    }, 10)
}

function asyncFunc2() {
    setTimeout(() => {
        console.log('2');
    }, 5)
}

asyncFunc1();
asyncFunc2();
```

Although the functions are called in order of `asyncFunc1` and then `asyncFunc2`, the output will be:

```
2
1
```

##### Blocking vs non-blocking functions

The functions in the example log in the order they do because javascript functions are _non-blocking_ unless they use a blocking keyword within themselves, like `while`, or `for`.  Non-blocking functions start, and run their code, but don't stop the program from continuing.

The two `asyncFunc*` functions above invoke `setTimeout` which just tells the interpreter to run a function after `n` milliseconds, so these are non-blocking, and the functions will be invoked only a 'tick' apart.

Once invoked, the functions invoke `setTimeout`, and because the `asyncFunc1` is set to wait 10 milliseconds before logging '1', and the `asyncFunc2` is set to wait only 5, `asyncFunc2` logs '2' 5 milliseconds before.

The order of invoking the functions, in this case, makes no difference - they would log in the same order even if you reversed the invocation.  This isn't always true, because asynchronous function are invoked a tick before a following function, so if they asynchronous function had _no delay_ the order they were called in would make a difference - but this will rarely be the case.

> NB: It's important to note, the example we've used is completely predictable, but usually when using asynchronous functions, you are not using timers, but waiting on the actions of unpredictable systems

##### Using `async` and `await` to write more concise code

Because the asynchornicity of code is a _useful_ feature of Javascript, but the code created is not easy to read, many approaches have been used to make it simpler.  Below are some examples:

###### Asynchronicity libraries (Like async.js)
This runs `functionOne`, `functionTwo`, `functionThree` in order, despite their asynchronicity.
```javascript
import async from 'async'

// Functions look somewhat like this:
function functionOne(callback) {
    doAsyncThingOfSomeSort('parameter', (error, data) => callback(error, data));
}

async.series([
    functionOne,
    functionTwo,
    functionThree
], (error, output) => {
    // Handle errors and output here
})
```
> This is a somewhat older styled way of approaching this, but it is clearer, and functions well.

###### Promises
Functions can be written to use Promises, a structure to return from a function immediately, and write code that is very clear, because of its use of plain English function names makes flow clear:

```javascript
function promiseFunction() {
    return new Promise((resolve, reject) => {
        doAsyncThingOfSomeSort('parameter', (error, data) => {
            if (error) return reject(error);

            resolve(data);
        })
    })
}

promiseFunction
    .then(data => {
        // Do stuff with data
    })
    .catch(error => {
        // Do stuff with error
    })
```
Multiple promises can be run and resolved by using `Promise.all`:
```javascript
Promise.all([
    promiseOne,
    promiseTwo,
    promiseThree
])
    .then(data => {
        // do stuff with output
    })
    .catch(error => {
        // do stuff with error
    })
```
Various utility libraries offer more complex control over Promises, to offer features like:
* Series running of promises
* Parallel running with maximum concurrency

###### `async` and `await` syntactic sugar
Promises improved the situation, and were easier to understand and write than embedded callbacks, async.js, etc, but they posed problems to do with handling errors, and sharing variables in scope (How do you know which async function fails in a promises array, for instance?).  The syntax is improved, and more verbose and clear to read, but there's still room for improvement.  This is where `async` and `await` come into play.

The first thing to understand is that `async` is just syntactic sugar.  You can write a function that works the same way, and that would interact with `await` in the same way.

An `async` function:
* Is declared using `async` in front of the function, e.g. `async function functionName(...args) {}`
* Is the same as a function that immediately returns a Promise - it's a wrapper for a Promise.
* Resolves the promise if it returns a value
* Rejects the promise if it throws an error

To illustrate the point, the two below functions equivalent:

```javascript
async function getData() {
    const data = await request.get('url/to/stuff');
    return data;
}
```
```javascript
function getData() {
    return new Promise((resolve, reject) => {
        request.get('url/to/stuff')
            .then(data => resolve(data))
            .catch(error => reject(error));
    });
}
```
But the top function is clearer to read, and is written in a synchronous fashion, whilst still actually being run in an asynchronous way.

When you have to make calls to many asynchronous functions in a row, `await` really comes into it's own:

```javascript
const data = await request.get('url/to/stuff');
await loadDataIntoUI(data);
await showNewPage();
```

#### Modules

Modules are a core feature of many languages. Modularisation allows seperation of scope and code, into organised and reusable chunks.

Many languages have this baked-in, but Javascript was originally intended to be written directly into HTML markup, and after that into singular files.  For a long while, the use of single files was consider close enough to a module system.

Over the years, many attempts were made to create modules, of which the most popular became:

##### CommonJS
```javascript
// Module definition
module.exports = function () {
    // This is the module - this one is a function, but it can be any structure with Javascript.
}
```

```javascript
// Module usage
const module = require('path/to/module');
```

Node.js used a CommonJS styled system for its modules for a long time, but in the very latest version has started to natively support an ECMA standard style

##### AMD - Asynchronous Module Definition
```javascript
// Module definition - AMD modules must be functions.
define('module', () => {
    // This is the module
});
```

```javascript
require(['module'], () => {
    //do stuff with module
})
```

AMD modules incorporate dependency injection - the `require` function receives an array of module names, and a predicate function that runs once the modules are available.

##### ECMAScript modules
The most recent addition, and a style most similar to that of many other languages is ECMA Modules.

```javascript
// Module definitions

const thing = // ... something, a function etc.
const thing2 = // ...another something
const default = // ... Final something

export thing;
export thing2;
export default default;
// Module can now export a default item, or one of several named things
```

```javascript
import { thing } from 'path/to/module';
import { thing2 } from 'path/to/module';
import aDefaultThing from 'path/to/module';
```

You can also use this syntax:

```javascript
from 'path/to/module' import { thing }
```

If several modules you import have clashing names, you can rename the imports as you import them using `as`

```javascript
import namedModule from 'path/to/module';
import namedModule as alternativelyNamedModule from 'path/to/module'
```

The ECMA module syntax is the most recent incarnation of modules, and alongside CommonJS, is one of the most popular.  It has a few features that make it clearer to understand, and can be used in a wider variety of ways that CommonJS.  The latest changes to `response-operations-ui` mean that it's now possible to use CommonJS or ECMAScript module syntax in scripts that we write.  AMD has not been implemented because it's more convoluted, and less useful in the cases we face.
