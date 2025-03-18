### Run the App ###

run the app with 
uvicorn main:app --reload --port {port}

swagger ui = http://127.0.0.1:8000/docs

redoc documentation = http://127.0.0.1:8000/redoc

### Database ###

Change postgres to your credential in core/db.py DATABASE_URL

We also have to insert some data to test to postgres