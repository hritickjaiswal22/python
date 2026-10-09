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
