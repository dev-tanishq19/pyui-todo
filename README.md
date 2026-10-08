# pyui – a tiny UI framework in Python (+ To-Do demo)

No dependencies. Python 3.9+.

    python todo_app.py        # open http://localhost:8000

## How it works
1. **Components** – functions that return a tree of `Element`s with props (`div(h1("Hi"), class_="card")`).
2. **Renderer** – walks the tree and produces HTML (text is escaped, so no HTML injection).
3. **State** – `state.set(...)` changes data and notifies the app.
4. **Events** – `on_click` / `on_submit` handlers are registered during render; the HTML posts to `/_event/<id>`,
   the server runs the handler, state changes, the app re-renders, the browser reloads `/`.
5. **Demo** – `todo_app.py` (add, complete, delete, filter, clear done) uses only `pyui`.

## Limits (by design)
Single shared in-memory state, full-page re-render, no JS.

## Deploy (Render/Railway/etc.)
Start command: `python todo_app.py` (reads `PORT` from the environment).
