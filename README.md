# Python Decorators

A decorator is a function that **takes another function and returns a modified version of it**, adding behavior without changing the original function's code.

Think of it as gift wrapping: the gift (the function) stays the same, but it comes wrapped in something extra.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Your First Decorator](#your-first-decorator)
3. [The `@` Syntax](#the--syntax)
4. [Handling Arguments and Return Values](#handling-arguments-and-return-values)
5. [Preserving Metadata with `functools.wraps`](#preserving-metadata-with-functoolswraps)
6. [Decorators with Arguments](#decorators-with-arguments)
7. [Stacking Multiple Decorators](#stacking-multiple-decorators)
8. [Class-Based Decorators](#class-based-decorators)
9. [Decorating Classes](#decorating-classes)
10. [Decorators That Register Instead of Wrap](#decorators-that-register-instead-of-wrap)
11. [Practical Examples](#practical-examples)
12. [Common Pitfalls](#common-pitfalls)
13. [Built-in and Popular Decorators](#built-in-and-popular-decorators)
14. [Quick Reference](#quick-reference)

---

## Prerequisites

Decorators rely on three Python features.

### 1. Functions are first-class objects

A function can be assigned to a variable, passed as an argument, and returned from another function.

```python
def say_hi():
    print("Hi!")

other = say_hi      # no parentheses: this is the function itself
other()             # Hi!
```

`say_hi` refers to the function. `say_hi()` **calls** it.

### 2. Functions can be defined inside functions

```python
def outer():
    def inner():
        print("inside")
    return inner

f = outer()
f()   # inside
```

### 3. Closures

An inner function can remember variables from the enclosing function, even after the outer function has returned.

```python
def make_greeter(name):
    def greet():
        print(f"Hello, {name}!")
    return greet

greet_ana = make_greeter("Ana")
greet_ana()   # Hello, Ana!
```

---

## Your First Decorator

```python
def my_decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

def say_hi():
    print("Hi!")

say_hi = my_decorator(say_hi)
say_hi()
```

Output:

```
Before
Hi!
After
```

A decorator does three things:

1. **Receives** a function (`func`).
2. **Defines** a new function (`wrapper`) that calls `func` plus does something extra.
3. **Returns** the new function (`return wrapper`, with no parentheses).

---

## The `@` Syntax

The `@` symbol is syntactic sugar. These two forms are identical:

```python
# Manual
def say_hi():
    print("Hi!")
say_hi = my_decorator(say_hi)

# With @
@my_decorator
def say_hi():
    print("Hi!")
```

After decoration, the name `say_hi` points to `wrapper`. The original function still exists, but it is held inside the wrapper as `func`.

```
BEFORE:  say_hi ──► [ original ]

AFTER:   say_hi ──► [ wrapper: extra + original + extra ]
                                         │
                                         └──► [ original ]
```

> **Important:** the decorator runs **once**, at definition time. The wrapper runs **every time** you call the function.

---

## Handling Arguments and Return Values

A realistic decorator must accept any arguments and return the original result.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)   # run the original and keep the result
        print("After")
        return result                    # hand the result back
    return wrapper

@my_decorator
def add(a, b):
    return a + b

print(add(2, 3))   # prints Before, After, then 5
```

- `*args, **kwargs` means "accept anything and forward it."
- `return result` ensures the original value is not lost.

### The two `return` statements

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result       # 1. returns the RESULT of the function
    return wrapper          # 2. returns the wrapper function ITSELF
```

| Missing return | Consequence |
|---|---|
| `return wrapper` (outer) | `add` becomes `None`; calling it raises `TypeError: 'NoneType' object is not callable` |
| `return result` (inner) | The function still runs, but the caller always receives `None` |

Note that `return wrapper` has **no parentheses**. With parentheses (`return wrapper()`), you would execute the wrapper immediately and return its result instead of the function.

---

## Stacking Multiple Decorators

```python
@A
@B
def f():
    ...
```

is equivalent to:

```python
f = A(B(f))
```

**B wraps `f` first, then A wraps the result.** Think of nested boxes with a single gift in the center:

```
[ box A [ box B [ f ] ] ]
```

- **Decoration** happens from the inside out (bottom decorator first).
- **Execution** happens from the outside in (top decorator's code runs first).

```python
def A(func):
    def wrapper(*args, **kwargs):
        print("enter A")
        result = func(*args, **kwargs)
        print("exit A")
        return result
    return wrapper

def B(func):
    def wrapper(*args, **kwargs):
        print("enter B")
        result = func(*args, **kwargs)
        print("exit B")
        return result
    return wrapper

@A
@B
def f():
    print("original")

f()
```

Output:

```
enter A
enter B
original
exit B
exit A
```

The original function runs **exactly once**. Stacking does not run it multiple times; each decorator simply adds its own layer. A function runs more than once only if a decorator explicitly calls it repeatedly (like `retry`).

Order matters: `@A @B` and `@B @A` produce different behavior.

---

## Class-Based Decorators

Any callable can be a decorator. A class with `__call__` works well when you need to keep state.

```python
from functools import update_wrapper

class CountCalls:
    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def greet():
    print("Hello!")

greet()   # Call #1 of greet
greet()   # Call #2 of greet
print(greet.count)   # 2
```

---

## Decorating Classes

Decorators can also receive and modify classes.

```python
def add_repr(cls):
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

print(Point(1, 2))   # Point(x=1, y=2)
```

`@dataclass` is the best-known example of a class decorator.

---

## Decorators That Register Instead of Wrap

A decorator does not have to wrap the function. It can simply record it somewhere and return it unchanged. This is how web frameworks define routes.

```python
class MiniApp:
    def __init__(self):
        self.routes = {}

    def get(self, path):
        def decorator(func):
            self.routes[path] = func   # register
            return func                # return the same function
        return decorator

app = MiniApp()

@app.get("/hello")
def hello():
    return {"message": "Hello!"}

print(app.routes)   # {'/hello': <function hello ...>}
```

Flask (`@app.route`), FastAPI (`@app.get`), and `pytest` (`@pytest.fixture`) all work this way.

---

## Common Pitfalls

1. **Forgetting `return wrapper`.** The decorated name becomes `None`.
2. **Forgetting to return the result inside the wrapper.** The function runs, but its value is lost.
3. **Writing `return wrapper()` instead of `return wrapper`.** You execute the wrapper instead of returning it.
4. **Forgetting `@wraps`.** You lose `__name__`, `__doc__`, and introspection, which breaks debugging and some tools.
5. **Not accepting `*args, **kwargs`.** The decorator then only works for functions with one specific signature.
6. **Confusing definition time with call time.** The decorator body runs once when the function is defined; the wrapper body runs on every call.
7. **Using `@decorator` when it needs arguments.** If the decorator takes arguments, you must write `@decorator()` (with parentheses), even if all arguments have defaults.
8. **Hidden behavior.** Decorators can change what a function does (caching, retries, permission checks). Always read the `@` lines above a function before assuming what it does.

---

## Built-in and Popular Decorators

| Decorator | Purpose |
|---|---|
| `@property` | Turn a method into a read-only attribute |
| `@staticmethod` | Method that does not receive `self` |
| `@classmethod` | Method that receives the class as `cls` |
| `@functools.wraps` | Preserve wrapped function metadata |
| `@functools.lru_cache` | Memoize results |
| `@functools.cache` | Unbounded cache (Python 3.9+) |
| `@functools.cached_property` | Compute an attribute once, then cache it |
| `@functools.singledispatch` | Function overloading by argument type |
| `@dataclasses.dataclass` | Auto-generate `__init__`, `__repr__`, etc. |
| `@contextlib.contextmanager` | Build context managers from generators |
| `@abc.abstractmethod` | Declare abstract methods |
| `@torch.no_grad()` | Disable gradient tracking (PyTorch) |
| `@tf.function` | Compile to a TensorFlow graph |
| `@jax.jit` / `@numba.jit` | JIT compilation |
| `@app.get("/path")` | Register a route (FastAPI/Flask) |
| `@pytest.fixture`, `@pytest.mark.parametrize` | Testing helpers |

---

## Quick Reference

**Minimal template (no arguments):**

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # code before
        result = func(*args, **kwargs)
        # code after
        return result
    return wrapper
```

**Mental model:**

```python
@decorator
def f(): ...

# is exactly
f = decorator(f)
```

