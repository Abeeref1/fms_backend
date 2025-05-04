from src.main import app

if __name__ == "__main__":
    # Only used if you run "python wsgi.py" locally
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
