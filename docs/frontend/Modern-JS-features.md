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
  - [Modules](#Modules)

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

Object.assign(StringArray, String, Array);
```

At this point, you have a String/Array hybrid, with functions for both strings and arrays.  Instantiating it with any value will fail, because if it's a string, the array constructor will throw, and if an array, the string constructor will fail.  If it had a value, the array functions would fail if it were a string, and vice versa.

In short, whilst multiple inheritance can be done, it's _best avoided_!

#### `async` and `await`

#### Modules