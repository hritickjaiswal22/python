# `python3 -m venv .venv` — the `node_modules` of Python

## The problem it solves

In Node, every project has its own `node_modules/`. If project A needs `axios@1.0` and project B needs `axios@2.0`, they don't conflict — each has its own folder.

Python **doesn't work that way by default**. `pip install requests` installs into one global location (`/usr/lib/python3.12/site-packages` or similar). So:

- Project A installs `requests==2.0`
- Project B installs `requests==3.0`
- Project A now breaks 💥

This is "dependency hell." A **virtual environment** fixes it — a self-contained folder per project with its own Python + its own packages. Exactly like `node_modules/`, but it also isolates the Python interpreter itself.

---

## Decoding the command

```
python3   -m   venv   .venv
   │       │     │       │
   │       │     │       └─ name of the folder to create (you choose)
   │       │     └───────── the built-in module to run: "venv"
   │       └─────────────── "run a module as a script"
   └─────────────────────── which python to use (3.12.3 in your case)
```

`python3 -m venv .venv` = "Hey python3, run the `venv` module, and make the environment in a folder called `.venv`."

The name `.venv` is just a **convention**. The leading dot hides it (like `.git`, `.env`). You could call it `myenv`, `env`, whatever. Everyone uses `.venv`.

### What `-m` means

It's Python's "run this module" flag. `python3 -m venv` runs the `venv` module. Same pattern for other tools:

- `python3 -m pip install requests` (run pip)
- `python3 -m http.server` (start a web server)
- `python3 -m json.tool file.json` (format JSON)

You'll see `-m` everywhere. It means "don't run a `.py` file, run this installed/builtin module."

---

## What just got created

```
.venv/
├── bin/              # scripts: python, pip, activate
├── lib/
│   └── python3.12/
│       └── site-packages/   # ← packages you pip install go HERE
└── pyvenv.cfg        # metadata
```

That `site-packages/` is your `node_modules/`. When activated, `pip install X` puts X **there**, not globally.

---

## Activation

Creating the venv doesn't use it — you have to **activate** it:

```bash
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows
```

After activation, your shell prompt changes:

```
(.venv) $
```

Now `python` and `pip` point to the venv versions. Test it:

```bash
which python     # → /path/to/project/.venv/bin/python
which pip        # → /path/to/project/.venv/bin/pip
pip install requests
```

`requests` now lives inside `.venv/lib/.../site-packages/`. Global Python is untouched.

**Deactivate** with:

```bash
deactivate
```

---

## The npm ↔ venv cheat sheet

| Node                             | Python                                   |
| -------------------------------- | ---------------------------------------- |
| `node_modules/`                  | `.venv/`                                 |
| `npm install`                    | `pip install`                            |
| `package.json`                   | `requirements.txt` (or `pyproject.toml`) |
| `package-lock.json`              | `requirements.txt` with pinned versions  |
| `.gitignore` has `node_modules/` | `.gitignore` has `.venv/`                |
| `nvm use 20`                     | activate venv                            |
| `npm run dev`                    | `python main.py`                         |

Install deps from a file:

```bash
pip freeze > requirements.txt     # save current deps
pip install -r requirements.txt   # install from file (like npm install)
```

---

## Rules of thumb

1. **One venv per project.** Always.
2. **Never commit `.venv/`.** Add to `.gitignore`. Others recreate it.
3. **Always commit `requirements.txt`** (or `pyproject.toml`).
4. **Never `pip install` without an active venv.** If you do, you pollute global Python and will regret it.
5. **Recreate anytime** — `.venv/` is disposable:
   ```bash
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Your exact next commands

```bash
mkdir py-api-practice && cd py-api-practice
python3 -m venv .venv              # create the isolated env
source .venv/bin/activate          # step into it
echo ".venv/" > .gitignore         # don't commit it
pip install requests               # now installs locally
python -c "import requests; print(requests.__version__)"
```

# Types in python

**Python has type hints, but they are NOT validated at runtime.**

Just like TypeScript, Python's built-in type hints are **erased at runtime**. They are purely for developers, IDEs (like VS Code), and static type checkers (like `mypy` or `pyright`). They do not magically validate the API response shape.

To get actual **runtime validation** (like Zod or io-ts in the JS world), you need a third-party library. The industry standard for this in Python is **Pydantic**.

Here is how you go from your current script to a fully typed, validated API client.

### Step 1: Basic Type Hints (The "TypeScript" way)

You can annotate your variables without installing anything. It won't validate anything, but it gives you autocomplete in VS Code.

```python
import requests
from typing import Any

res: requests.Response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
print(res.status_code)
print(res.headers["content-type"])

# We tell Python this is a dictionary. It won't check if it's true.
data: dict[str, Any] = res.json()
print(data["title"]) # VS Code will autocomplete "title" if it's typed as dict
```

This is exactly like writing `const data: any = await res.json()` in TS. It's a lie until you validate it.

---

### Step 2: Runtime Validation with Pydantic (The "Zod" way)

Pydantic is the Python equivalent of Zod. You define a class (like an interface), and it will actually **parse and validate** the incoming data at runtime. If the API returns a string where a number should be, Pydantic throws an error.

First, install it in your `.venv`:

```bash
pip install pydantic
```

Now, refactor your code:

```python
import requests
from pydantic import BaseModel, ValidationError

# 1. Define the expected shape (like a TS interface)
class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

# 2. Make the request
res = requests.get("https://jsonplaceholder.typicode.com/posts/1")
raw_data = res.json()

# 3. Validate and parse the data!
try:
    post = Post.model_validate(raw_data)  # <-- This does the actual validation
    print(f"Success! Title: {post.title}")
    print(f"Body: {post.body}")

    # Note: `post` is now an object, not a dictionary!
    # You use dot notation (post.title) instead of bracket notation (raw_data["title"])

except ValidationError as e:
    print("API returned the wrong shape!")
    print(e.json())

```

### The Key Differences (TS vs. Python)

| Feature                  | TypeScript                      | Python (Built-in) | Python (Pydantic)                |
| :----------------------- | :------------------------------ | :---------------- | :------------------------------- |
| **Syntax**               | `interface Post { id: number }` | `dict[str, Any]`  | `class Post(BaseModel): id: int` |
| **Runtime Validation?**  | ❌ No (erased)                  | ❌ No (erased)    | ✅ **Yes**                       |
| **Throws on bad data?**  | N/A                             | ❌ No             | ✅ **Yes** (`ValidationError`)   |
| **Output object**        | Plain JS object                 | `dict`            | **Class instance** (`post.id`)   |
| **Ecosystem Equivalent** | Zod / io-ts                     | None              | **Pydantic**                     |

### Why this matters for API calling

In TypeScript, you use Zod to validate `fetch` responses because TypeScript can't.
In Python, you use Pydantic to validate `requests` responses because Python's built-in hints can't.

If you look at almost any modern Python backend (FastAPI) or SDK (OpenAI, Anthropic), they are built entirely on Pydantic models. It is the de facto standard for data validation in Python.

### Your next move:

1. Run `pip install pydantic`
2. Add the `Post` class to your `api.py`
3. Try changing the URL to `/posts/1` but intentionally break the model (e.g., change `id: int` to `id: str`) to see the `ValidationError` in action. That's the magic of runtime validation!

# Core Differences in Approach: Dynamic Typing, Functional Programming, and OOP

Both JavaScript and Python are dynamically typed, meaning that variables do not need to be declared with a specific type and can hold different types of data at runtime. But the two languages implement this dynamic typing in slightly different ways, **and they each approach functional programming and object-oriented programming (OOP) differently**.

**Dynamic Typing**: Both languages allow flexibility in declaring variables without specifying types, making them highly flexible. But Python’s strict indentation requirements and clear error messages provide a more structured approach to dynamic typing.

JavaScript, on the other hand, has a looser syntax, which sometimes leads to quirks, such as type coercion, that can result in unexpected behavior (for example, 0 == '' evaluates to true).

**Functional Programming**: Both languages support functional programming techniques, but JavaScript leans heavily on it. Functions are first-class citizens in JavaScript, allowing developers to pass functions as arguments, return them from other functions, and store them in variables. Higher-order functions, such as map, reduce, and filter, are commonly used in JavaScript to process arrays and data collections.

Python also supports functional programming, and it includes a lambda feature for anonymous functions as well as map, filter, and reduce functions. But functional programming is **less central in Python, which encourages readability and simplicity over deeply functional constructs**.

**Object-Oriented Programming (OOP)**: JavaScript’s OOP model is prototype-based, meaning that objects can inherit directly from other objects without the need for classes. Since ES6, JavaScript has also included support for class syntax, making it easier for developers coming from class-based languages to work with objects.

**Python, on the other hand, uses a class-based model that is more in line with traditional OOP languages like Java and C++. Classes, inheritance, and polymorphism in Python are straightforward, making it an excellent choice for developers who prefer a clear and well-structured approach to OOP**.

#### Common Use Cases for JavaScript:

- Frontend Web Development

- Full-Stack Web Development

- Real-Time Applications

- Mobile App Development

#### Common Use Cases for Python:

- Data Science and Analysis

- Machine Learning and Artificial Intelligence

- Automation and Scripting

- Backend Web Development

- Scientific Computing and Research

# Syntax and Language Features

Comparison of Syntax Simplicity and Readability

One of Python’s main selling points is its clear, readable syntax. Often described as “executable pseudocode,” Python emphasizes simplicity, aiming for code that’s easy to write and, perhaps more importantly, easy to read.

Unlike JavaScript, which uses braces ({}) to define code blocks, Python uses indentation to enforce structure, which naturally encourages clean, organized code.
Example: Hello World and Simple Loops

In both languages, the "Hello, World!" example highlights the difference in syntax:

Python:

```
print("Hello, World!")
```

JavaScript:

```
console.log("Hello, World!");
```

Python’s built-in print function makes printing straightforward without additional syntax. In JavaScript, console.log performs the same task but requires a more explicit object-method format.

Now, consider a simple loop that prints numbers from 0 to 4:

Python:

```
for i in range(5):
    print(i)
```

JavaScript:

```
for (let i = 0; i < 5; i++) {
    console.log(i);
}
```

The difference here is striking. Python’s for loop with range() is compact and highly readable, while JavaScript’s loop uses a more complex syntax with initialization, condition, and increment clauses. This is a minor but illustrative example of Python’s design philosophy: code should be intuitive and easy to follow.

### Type Checking and Conversion

Python’s type-checking system is more consistent, while JavaScript sometimes has quirky behavior due to type coercion, where values of different types are implicitly converted for comparison. For example:

JavaScript:

```
console.log(0 == "");  // true due to type coercion
console.log(0 === ""); // false due to strict equality
```

Python:

```
print(0 == "")  # Raises a TypeError: 'int' and 'str' cannot be compared
```

Python does not allow implicit type coercion, reducing potential bugs related to unexpected type behavior. If type conversion is needed, Python requires explicit casting.
Working with Primitive Data Types

JavaScript and Python share some primitive types but also have unique types and handling:

- Numbers: Both JavaScript and Python have number types, but Python distinguishes between int and float for integers and decimal numbers. JavaScript has only a single Number type for all numeric values (including NaN for “not-a-number”).

- Strings: Both languages treat strings as sequences of characters, allowing methods like concatenation, splitting, and indexing. In Python, strings are immutable, meaning once created, they cannot be modified directly.

- Booleans: Both languages have true and false values. But JavaScript’s type coercion can lead to unexpected results in conditions, which Python avoids with explicit boolean handling.

- Null and Undefined: JavaScript distinguishes between null (an intentional absence of value) and undefined (an uninitialized variable). Python uses None as a single, consistent representation of “no value.”

# Async in Python

```
import httpx
import asyncio
from pydantic import BaseModel, ValidationError

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

async def main():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://jsonplaceholder.typicode.com/posts/1")
        post = Post.model_validate(res.json())
        print(post)

asyncio.run(main())
```

## First, the plain `with` statement

Python has a thing called a **context manager**. If you've seen this pattern before:

```python
with open("file.txt") as f:
    data = f.read()
# file is automatically closed here, even if an error happened
```

That's the same as writing:

```python
f = open("file.txt")
try:
    data = f.read()
finally:
    f.close()
```

The `with` block guarantees **setup** at the start and **cleanup** at the end, no matter what happens inside. In JS terms, it's like a built-in `try/finally` shorthand.

## Now the `async` version

`async with` is exactly the same idea, except the setup and/or cleanup require `await`.

So:

```python
async with httpx.AsyncClient() as client:
    res = await client.get(...)
```

is roughly equivalent to:

```python
client = httpx.AsyncClient()
await client.__aenter__()      # "setup"
try:
    res = await client.get(...)
finally:
    await client.__aexit__(None, None, None)   # "cleanup"
```

The `__aenter__` / `__aexit__` methods are just Python's dunder hooks for the async context manager protocol.

## What is `httpx.AsyncClient()` actually doing?

It creates an HTTP client object. Why not just `await httpx.get(...)` like you'd do in JS with `fetch`?

Because `AsyncClient` maintains:

- a **connection pool** (reuses TCP connections instead of opening a new one each request)
- default headers, auth, timeouts, base URLs, etc.
- things that need explicit teardown — you have to `await client.aclose()` when done

That's why it's a context manager: it needs to be **opened** and **closed** cleanly.

`async with httpx.AsyncClient() as client:` = "create a client, give me a reference as `client`, and when the block ends (even on error), close it for me."

## Ok so `async with httpx.AsyncClient() as client` creates an http client object but why is it required anyway ???

The real reason for creating an HTTP client object is that "The difference is Node's undici (behind fetch) has a global connection pool it manages for you. Python doesn't — you create and own the pool explicitly. That's why the async with shows up so much." in node js it is handled for me automatically while in Python it needs to be done explicitly

#### It's a philosophical difference between the two ecosystems

**Node.js / JS:** "Batteries included, hide the complexity."

- `fetch` just works. There's a global dispatcher (undici) managing sockets behind the scenes.
- You never think about connection pooling unless you're optimizing something specific.

**Python:** "Explicit is better than implicit." (This is literally from the Zen of Python — run `import this` in a REPL.)

- The language prefers you to see and control resource lifecycles.
- Sockets, files, DB connections, HTTP clients — all explicitly opened and closed.
- It's more verbose, but you always know what's happening.

#### So the full "why" is three things bundled together

1. **Connection pooling** — reuse sockets (the main perf win)
2. **Shared configuration** — base URL, headers, auth, timeouts, cookies
3. **Explicit lifecycle** — you decide when it opens and closes, which matters in async apps where "when do I clean up?" is critical

All three are solved by the same object, which is why `AsyncClient` shows up everywhere.

## Ok so in JS async and await is handled by promises and single threaded event loop delegation model basically inside an async function after first await the code more or less behaves like chained `then` blocks pushed into microtask queue and does not block main thread so how does that work in python ???

```
My initial understanding for python async & await is

- An async function upon execution does not start executing by itself unlike in JS it returns a "coroutine"
- This co-routine needs to be activated by `asyncio.run(asyncFn())`
- Unlike in JS which has event loop always , python does not when above coroutine is activated an event loop for that async function is also created
- Inside this event loop just like JS in which after first await tasks or callbacks are pushed into queue for python they get pushed to ready queue and after that
- The same architecture as followed by JS involving event loop and single thread is used for execution and completion of that async function

```

## Review of above

Your understanding is **mostly right**, but a few points need sharpening. Let me go through each one.

## ✅ Point 1: "An async function returns a coroutine and doesn't start by itself"

**Correct.** This is the biggest mental shift from JS and you nailed it.

Small addition: the coroutine object is inert until _something_ drives it. `await`, `asyncio.run`, or `asyncio.create_task` are the drivers.

## ⚠️ Point 2: "This coroutine needs to be activated by `asyncio.run(asyncFn())`"

**Half right.** `asyncio.run()` **does** activate it — but it's not the _only_ way, and it's not what happens in FastAPI.

The ways to drive a coroutine:

- `asyncio.run(coro)` → creates a loop, runs the coro until done, closes the loop. **Only callable once, at the top level, and only from sync code.**
- `await coro` → drives it inside another coroutine.
- `asyncio.create_task(coro)` → schedules it on the _currently running_ loop.

In FastAPI/uvicorn, uvicorn calls `asyncio.run(...)` (or equivalent) **once** at startup. After that, every request handler is a coroutine driven by `await` / `create_task` on that same loop. You'll never call `asyncio.run` in your own FastAPI code.

So: `asyncio.run` is one way to _start the whole thing_, not the general mechanism for running every coroutine.

## ❌ Point 3: "When the coroutine is activated, an event loop for that async function is created"

**This is the part to fix.** It's not one loop per coroutine. It's **one loop total**, and _all_ coroutines run on it.

Think of it this way:

```
asyncio.run(main())
    └── creates ONE loop
        └── schedules main() on it
            └── main() awaits sub1()   ← same loop
            └── main() awaits sub2()   ← same loop
            └── create_task(worker())  ← same loop
```

Every coroutine, task, and callback in your program shares that single loop. That's exactly like JS — one event loop, everything on it.

The wording "an event loop for that async function" makes it sound like each coroutine gets its own loop, which would break the whole concurrency model (how would they share state or await each other?).

BUT

```python
asyncio.run(main1())
asyncio.run(main2())
asyncio.run(main3())
```

#### Question Do three `asyncio.run()` calls share one loop?

**No — and this is important.**

Each `asyncio.run()` call:

1. Creates a **brand new** event loop
2. Runs the coroutine on it until it finishes
3. **Closes and destroys** that loop
4. Then the next line runs — which creates _another_ brand new loop

So they don't share anything. They run **sequentially**, one after another, each in its own throwaway loop. The first one must completely finish before `main2` even starts.

### The JS comparison

In JS, the event loop is a **process-level singleton**. There's exactly one, forever, and you can't replace it. So your instinct — "one loop, shared" — is the JS mental model leaking in.

In Python, the event loop is just an **object**. You can create many. `asyncio.run()` is a convenience that does create-use-destroy for you.

### How you'd actually share one loop

Wrap them in a single `asyncio.run()`:

```python
async def main():
    await asyncio.gather(main1(), main2(), main3())   # concurrent, same loop
    # or sequentially:
    # await main1(); await main2(); await main3()

asyncio.run(main())   # ONE loop for all three
```

Now all three run on the same loop. `gather` even runs them concurrently — like `Promise.all([main1(), main2(), main3()])`.

### The rule

> **One `asyncio.run()` = one loop.** Everything inside that `asyncio.run()` shares it. Nothing _outside_ it exists on that loop.

In FastAPI/uvicorn, uvicorn calls `asyncio.run()` once at startup. Every request for the entire life of the server runs on that one loop. That's your "singleton" — it's just created once by the framework, not by the language.

## ✅ Point 4: "After first await, callbacks pushed to ready queue"

**Mostly correct.** Small refinements:

- It's not just "after the _first_ await" — it's after _every_ await. The coroutine pauses and resumes each time it awaits something that isn't immediately ready.
- The queue isn't literally called "ready queue" in user-facing docs, but internally asyncio has exactly that (`loop._ready`). So your intuition is fine.
- There's also a **timer heap** for delayed things (`asyncio.sleep(1)`) and an **I/O selector** for sockets — JS hides these; Python's loop has them as explicit structures.

## ⚠️ Point 5: "Same architecture as JS, single thread, event loop executes it"

**Correct in spirit, with one important caveat:** Python has a **GIL** (Global Interpreter Lock), which means even if you _do_ use threads, only one thread runs Python bytecode at a time. JS is single-threaded by design; Python is single-threaded _for CPU work_ in practice, but it _does_ have threads.

For your async code: you're on the event loop thread, same as JS. But you can also `run_in_executor` to hand blocking work (file I/O, CPU-heavy stuff) to a thread pool — something you don't typically do in JS because you'd use a Worker.

## Corrected version of your summary

> - An `async def` function returns a **coroutine** and does not start on its own (unlike JS).
> - The coroutine must be **driven**: by `await`, by `asyncio.create_task`, or at the top level by `asyncio.run`.
> - `asyncio.run` creates **one event loop** for the _entire program_ (not per coroutine). FastAPI/uvicorn does this once at startup, then reuses that loop for every request.
> - Inside that loop, every `await` that can't complete immediately pauses the coroutine and schedules its continuation on the loop's ready queue — very similar to JS microtasks.
> - The loop also handles timers and I/O readiness (via `epoll`/`kqueue`/`IOCP`) — same underlying design as Node's libuv, just exposed explicitly.
> - Execution is single-threaded on the loop thread, like JS. (Extra nuance: Python has threads + a GIL, but they don't run in parallel for CPU work.)

## One-liner to remember

**JS:** "There is an event loop, and async functions start themselves on it."
**Python:** "There is an event loop _you or a framework start_, and coroutines are inert until _you_ put them on it."
