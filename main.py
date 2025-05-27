from fastapi import FastAPI
#comment to test
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}