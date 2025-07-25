from app import app
from app.core.config import config

# entry point for the sahayak gateway
if __name__=="__main__":
    import uvicorn
    uvicorn.run(
        app=app,
        host=config.HOST,
        port=config.PORT
    )
    pass