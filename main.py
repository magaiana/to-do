from fastapi import FastAPI

# create the app
app = FastAPI()

# define a simple route (like a door you can knock on)
@app.get("/")
def read_root():
    return {"message": "Hello Ntobeko"}
