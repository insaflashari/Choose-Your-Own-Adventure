##main.py
# main.py → The entry point of your backend. Starts the 
# server, sets up routes, config, and connects the pieces.

from fastapi import FastAPI #main class for creating FastAPI app
from fastapi.middleware.cors import CORSMiddleware #Middleware to handle Cross-Origin Resource Sharing (lets your frontend running on a different domain or port talk to your backend).

from core.config import settings #Central place for settings (e.g., environment variables like DB connection URL, allowed origins, API prefix).
from routers import story, job  #Two separate files that define related API endpoints for different parts of the game.
from db.database import create_tables #Function that ensures your database tables exist before starting.

create_tables() #Runs before the app is started, makes sure all the models are created in the database

#creates FastAPI application object w metadata
app = FastAPI(
    title="Choose Your Own Adventure Game API", #for API docs
    description="api to generate cool stories", #for API docs
    version="0.1.0", #for API docs
    docs_url="/docs", #where Swagger UI docs are served 
    redoc_url="/redoc" #where redoc docs are served
)

#CORS is Cross Origin Resource Sharing, we enable certain 
# "origins"/urls to interact with our backend
#SECURITY

#Your frontend might be hosted on a different port (e.g., React on http://localhost:3000) 
# from your backend (http://localhost:8000), and browsers block cross-origin requests by default.

##allow someone to send credentials to our backend
##allowed to use any API type methods, like "GET"(retrieving data), "POST"(making data), "PUT"(updating data) 
## which specifiy different operations you want to do on the API, we are allowing all these operations
##headers is like additional info you can send with the request, we are allowing all of the headers

app.add_middleware (
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, #Whitelist of allowed frontend URLs.
    allow_credentials=True, #Allows cookies / authentication headers to be sent.
    allow_methods=["*"], #Allows all HTTP methods (GET, POST, PUT, DELETE…). 
    allow_headers=["*"] #Allows any custom HTTP headers. 
)

#setting up endpoints

#include_router() pulls in the endpoints from story.py and job.py.
#prefix=settings.API_PREFIX → Means your routes will have a common base path (e.g., /api/story instead of just /story).
app.include_router(story.router, prefix = settings.API_PREFIX)

app.include_router(job.router, prefix = settings.API_PREFIX)

##standard python practice: only execute what's inside this if statement if we directly execute this python file
# (if we import from this file it won't run, but if we execute this file it will run)

#if __name__ == "__main__": → Only runs if you start the file directly with python main.py.
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
##univorn is a webserver that allows us to serve our fastapi app, 
# we can't run a fastapi api unelss it has a webserver that it is connected to

#"main:app" → "file_name:FastAPI_app_object".
##host="0.0.0.0" → Accessible from anywhere (useful in Docker or remote servers).
###port=8000 → Runs on port 8000.
####reload=True → Auto-restarts the server on code changes (for development).
    