from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# 1) What a Todo looks like (input from the user)
class TodoIn(BaseModel):
    title: str
    done: bool = False  # default = not done yet
    notes: Optional[str] = None

# 2) What we send back (includes an id)
class TodoOut(TodoIn):
    id: int

# 3) Super simple storage (just for learning)
TODOS: List[TodoOut] = []
_next_id = 1  # simple counter for ids


def _get_next_id() -> int:
    global _next_id
    val = _next_id
    _next_id += 1
    return val


# HEALTH CHECK / ROOT
@app.get("/")
def read_root():
    return {"message": "Todo API is running. Go to /docs to test."}


# LIST all todos
@app.get("/todos", response_model=List[TodoOut])
def list_todos():
    return TODOS


# ADD a new todo
@app.post("/todos", response_model=TodoOut, status_code=201)
def add_todo(todo: TodoIn):
    new_todo = TodoOut(id=_get_next_id(), **todo.model_fields_set and todo.model_dump() or todo.dict())
    TODOS.append(new_todo)
    return new_todo


# GET one todo by id
@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int):
    for t in TODOS:
        if t.id == todo_id:
            return t
    raise HTTPException(status_code=404, detail="Todo not found")


# EDIT/REPLACE a todo (PUT = send the full object)
@app.put("/todos/{todo_id}", response_model=TodoOut)
def replace_todo(todo_id: int, todo: TodoIn):
    for i, t in enumerate(TODOS):
        if t.id == todo_id:
            updated = TodoOut(id=todo_id, **(todo.model_dump() if hasattr(todo, "model_dump") else todo.dict()))
            TODOS[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")


# PARTIAL UPDATE (PATCH = send only what changed)
class TodoPatch(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    notes: Optional[str] = None

@app.patch("/todos/{todo_id}", response_model=TodoOut)
def patch_todo(todo_id: int, changes: TodoPatch):
    for t in TODOS:
        if t.id == todo_id:
            data = (t.model_dump() if hasattr(t, "model_dump") else t.dict())
            patch = (changes.model_dump(exclude_unset=True)
                     if hasattr(changes, "model_dump")
                     else changes.dict(exclude_unset=True))
            data.update(patch)
            updated = TodoOut(**data)
            # replace in list
            for i, x in enumerate(TODOS):
                if x.id == todo_id:
                    TODOS[i] = updated
                    break
            return updated
    raise HTTPException(status_code=404, detail="Todo not found")


# DELETE a todo
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for i, t in enumerate(TODOS):
        if t.id == todo_id:
            TODOS.pop(i)
            return
    raise HTTPException(status_code=404, detail="Todo not found")
