from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db, require_role
import models, schemas

router = APIRouter(prefix="/routes", tags=["routes"])

@router.get("")
def get_routes(db: Session = Depends(get_db)):
    routes = db.query(models.Route).order_by(models.Route.created_at.desc()).all()
    return {
        "success": True,
        "message": "Rutas cargadas correctamente.",
        "data": {
            "routes": [schemas.RouteOut.model_validate(r) for r in routes]
        }
    }

@router.post("")
def create_route(
    data: schemas.RouteCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_role(["admin"]))
):

    existing = db.query(models.Route).filter(models.Route.id == data.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="La ruta ya existe.")
        
    new_route = models.Route(
        id=data.id,
        name=data.name,
        zone=data.zone,
        points=data.points
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    return {
        "success": True,
        "message": "Ruta creada correctamente.",
        "data": {
            "route": schemas.RouteOut.model_validate(new_route)
        }
    }
