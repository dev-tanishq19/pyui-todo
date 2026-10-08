"""Demo: a to-do list built ONLY with pyui."""
from pyui import (App, State, Raw, div, span, p, h1, h2, ul, li, button, form,
                  input_, style)

CSS = """
:root{--bg1:#6366f1;--bg2:#ec4899;--card:#ffffff;--text:#1f2937;--muted:#9ca3af;
      --line:#f1f1f4;--accent:#6366f1;--soft:#eef2ff;--danger:#ef4444;--input:#f6f7fb}
@media (prefers-color-scheme:dark){
 :root{--card:#1e1f2b;--text:#f3f4f6;--muted:#7c8195;--line:#2b2d3c;--soft:#2a2c45;--input:#262838}}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;padding:2.5rem 1rem;color:var(--text);
     font-family:'Segoe UI',system-ui,-apple-system,Roboto,sans-serif;
     background:linear-gradient(135deg,var(--bg1),var(--bg2)) fixed}
.card{max-width:520px;margin:auto;background:var(--card);padding:1.8rem;border-radius:22px;
      box-shadow:0 25px 60px rgba(0,0,0,.25)}
.head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:.4rem}
h1{margin:0;font-size:1.8rem;letter-spacing:-.5px}
.sub{color:var(--muted);font-size:.9rem;margin:.2rem 0 0}
.pct{font-weight:700;color:var(--accent);font-size:1.1rem}
.progress{height:8px;background:var(--soft);border-radius:99px;overflow:hidden;margin:1rem 0 1.4rem}
.progress div{height:100%;background:linear-gradient(90deg,var(--bg1),var(--bg2));
              border-radius:99px;transition:width .4s}
form.inline{display:inline;margin:0}
.add{display:flex;gap:.6rem;margin-bottom:1.2rem}
.add input{flex:1;padding:.85rem 1rem;border:2px solid transparent;border-radius:14px;
           background:var(--input);color:var(--text);font-size:1rem;outline:none;transition:.2s}
.add input:focus{border-color:var(--accent);background:var(--card)}
button{font:inherit;cursor:pointer;border:0;transition:transform .15s,background .2s,opacity .2s}
button:hover{transform:translateY(-1px)}
.add button{padding:0 1.3rem;border-radius:14px;color:#fff;font-weight:600;
            background:linear-gradient(135deg,var(--bg1),var(--bg2))}
ul{list-style:none;padding:0;margin:0}
li{display:flex;align-items:center;gap:.8rem;padding:.75rem .4rem;border-bottom:1px solid var(--line)}
li .text{flex:1;font-size:1.02rem}
li.done .text{text-decoration:line-through;color:var(--muted)}
.check{width:26px;height:26px;border-radius:50%;border:2px solid var(--muted);
       background:transparent;color:#fff;font-size:.8rem;display:grid;place-items:center;padding:0}
.check.on{background:var(--accent);border-color:var(--accent)}
.del{background:transparent;color:var(--muted);font-size:1.3rem;line-height:1;padding:.2rem .5rem;
     border-radius:8px;opacity:.5}
li:hover .del{opacity:1;color:var(--danger)}
.empty{text-align:center;padding:2rem 0;color:var(--muted)}
.empty .big{font-size:2.6rem}
.bar{display:flex;gap:.4rem;margin-top:1.3rem;align-items:center;flex-wrap:wrap}
.pill{padding:.4rem .9rem;border-radius:99px;background:var(--soft);color:var(--accent);
      font-size:.85rem;font-weight:600}
.pill.active{background:var(--accent);color:#fff}
.clear{margin-left:auto;background:transparent;color:var(--muted);font-size:.85rem;padding:.4rem .5rem}
.clear:hover{color:var(--danger)}
"""

EMPTY = {"all": ("📝", "Nothing here yet. Add your first task!"),
         "active": ("🎉", "All caught up!"),
         "done": ("🕳️", "No completed tasks yet.")}

state = State(todos=[], next_id=1, filter="all")


# ---- event handlers: change state -> UI re-renders automatically ----
def add_todo(fields):
    text = fields.get("text", "").strip()
    if text:
        state.set(todos=state["todos"] + [{"id": state["next_id"], "text": text, "done": False}],
                  next_id=state["next_id"] + 1)

def toggle(todo_id):
    state.set(todos=[{**t, "done": not t["done"]} if t["id"] == todo_id else t
                     for t in state["todos"]])

def delete(todo_id):
    state.set(todos=[t for t in state["todos"] if t["id"] != todo_id])

def set_filter(name):
    state.set(filter=name)

def clear_done():
    state.set(todos=[t for t in state["todos"] if not t["done"]])


# ---- components: plain functions that return Elements ----
def TodoItem(t):
    return li(
        button("✓" if t["done"] else "", class_="check on" if t["done"] else "check",
               on_click=lambda: toggle(t["id"])),
        span(t["text"], class_="text"),
        button("×", class_="del", on_click=lambda: delete(t["id"])),
        class_="done" if t["done"] else "",
    )

def FilterButton(name, current):
    return button(name.capitalize(), class_="pill active" if name == current else "pill",
                  on_click=lambda: set_filter(name))

def Header(total, done):
    pct = round(100 * done / total) if total else 0
    return div(
        div(div(h1("My Tasks"), p(f"{done} of {total} completed", class_="sub")),
            span(f"{pct}%", class_="pct"), class_="head"),
        div(div(style=f"width:{pct}%"), class_="progress"),
    )

def EmptyState(current):
    icon, msg = EMPTY[current]
    return div(div(icon, class_="big"), p(msg), class_="empty")

def view(s):
    todos, current = s["todos"], s["filter"]
    shown = [t for t in todos if current == "all" or (current == "done") == t["done"]]
    done = sum(t["done"] for t in todos)
    return div(
        style(Raw(CSS)),
        div(
            Header(len(todos), done),
            form(input_(name="text", placeholder="Add a new task…", autocomplete="off", autofocus=True),
                 button("Add"), class_="add", on_submit=add_todo),
            ul([TodoItem(t) for t in shown]) if shown else EmptyState(current),
            div(
                [FilterButton(n, current) for n in ("all", "active", "done")],
                button("Clear completed", class_="clear", on_click=clear_done),
                class_="bar",
            ),
            class_="card",
        ),
    )


if __name__ == "__main__":
    App(view, state, title="pyui To-Do").run()
