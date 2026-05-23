from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, admin, guardian, routes, reports

app = FastAPI(title="Recoleccta API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(guardian.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API de Recoleccta en funcionamiento"}

