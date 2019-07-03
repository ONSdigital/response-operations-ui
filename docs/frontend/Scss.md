# SASS/SCSS to CSS Transpiler                               <!-- omit in toc -->
## Streamlined process for styling Response Operations UI   <!-- omit in toc -->

- [Introduction](#Introduction)

### Introduction
The HTML in the frontend of the UI is styled with Cascading Style Sheets (CSS).  Rather than rely on the potentially repetetive syntax of this, we use SCSS, which is compiled to usable CSS by a task in [Gulp](Gulp.md).

SCSS allows us to:

* Use features not available in CSS
* Write more succinct code
* Write hierarchical styles not possible in CSS
* Write plain CSS if we want - _All valid CSS is valid SCSS. So if you don't know it, it's not a problem_
* Make use of several additional features to reuse code: SCSS has mixins, functions, and variables, whilst CSS generally doesn't have the same

### SCSS Primer
The easiest way to explain SCSS is to note how it's different from CSS:

A basic CSS 'rule' looks like this:

```CSS
.selector {
    property: value;
}
```

This shows us several things:

* A CSS rule is defined by a selector.  The above example shows us a selector that would apply to elements with the class `selector`, but other selectors are available, such as `#id` for selecting an element with id `id`, or `a` for selecting HTML anchor tags (`<a>`).
* The rule is encapsulated by parentheses, which contain a list of key-value pairs.
* The key-value pairs each specify a styling 'property' and 'value' for that, for example 'width: 10px' defines the element as 10 pixels wide.

CSS is flat, so if you define two items, one defined as a child of another, you must write two rules like this:

```CSS
.parent {
    property: value;
}

.parent .child {
    property: value;
}
```

Which can lead to long lists of repetetive styles.

#### SCSS hierarchical syntax
In SCSS, you can declare rules within rules, which makes the code less repetitive.  See the example below:

```scss
.parent {
    property: value;

    .child {
        other-property: value;
    }
}
```

This is succinct, and would compile down to CSS like this:

```css
.parent {
    property: value;
}
.parent .child {
    other-property: value;
}
```

You can embed as many rules within rules as you like, but bear in mind that a CSS rule shouldn't be too specific - it should be as specific as it needs to be.  This isn't documentation on CSS itself, so if you want to read more about CSS Specifity, [this article](https://css-tricks.com/specifics-on-css-specificity/) is a good place to start.

#### SCSS rule extending syntax
The examples shown in [SCSS hierarchical syntax](#SCSS-hierarchical-syntax) show a simple example of how SCSS can create rules made up multiple selectors in a row, simply by declaring new rules within the current rule, but there are cases in which this isn't enough.

How, for example, could we define an anchor tag that has different states like `:visited`, `:active` etc.  If we wrote this in SCSS as embedded rules, it would generate the state selectors as children:

```scss
a {
    text-decoration: none;
    :hover {
        text-decoration: underline;
    }
}
```

...seems like it may work, but actually generates this CSS:

```css
a {
    text-decoration: none;
}

a :hover {
    text-decoration: underline;
}
```

...which isn't what we needed at all, because we need to create `a:hover` as a selector.  Selectors that modify the parent selector use the `&` character to declare rules that extend the current rule:

```scss
a {
    text-decoration: none;

    &:hover {
        text-decoration: underline;
    }
}
```
...gives us exactly what we wanted:

```css
a {
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
```

#### SCSS Mixins
Mixins in SCSS are small chunks of reusable code that can be added to styling rules.  When you have patterns that you use often, you can create a mixin, and include it in your rules.  Mixins accept parameters, much like functions, and they form CSS info themselves.

#### Simple example

**Mixin:**
```scss
@mixin reset() {
    margin: 0;
    padding: 0;
}
```

**Use:**
```scss
.element {
    width: 100px;
    height: 100px;

    @include reset();
}
```

**Resulting CSS:**
```css
.element {
    width: 100px;
    height: 100px;
    margin: 0;
    padding: 0;
}
```

#### Advanced example (mixin with parameters)

**Mixin:**
```scss
@fade-to-black($color) {
    background: linear-gradient(to-bottom, $color, black);
}
```

**Use:**
```scss
.element {
    @include fade-to-black(red);
}
```

**Resulting CSS:**
```css
.element {
    background: linear-gradient(to-bottom, red, black);
}
```

### Variables
A recent addition to CSS also, SCSS supports variables that you can use to represent virtually anything you need to.  These are useful for reuse of values that you can then change only once.

Variables are set using this syntax:
```scss
$variable-name: "value" // doesn\'t have to be a string
```

Common uses include setting font sizes, colours, and image locations:

```scss
background-image: $background-img-url;
```

```scss
color: $global-text-colour
```

```scss
font-size: $font-size-xl;
```