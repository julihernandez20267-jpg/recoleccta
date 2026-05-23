from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db, require_role
from core.security import get_password_hash
import models, schemas
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def get_users(db: Session = Depends(get_db), admin: models.User = Depends(require_role(["admin"]))):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    user_list = [
        {
            "uid": user.id,
            "email": user.email,
            "role": user.role,
            "displayName": user.displayName,
            "photoURL": user.photoURL,
            "createdAt": user.created_at
        } for user in users
    ]
    return {
        "success": True,
        "message": "Usuarios cargados correctamente.",
        "data": {
            "users": user_list
        }
    }

@router.post("/users")
def update_user_role(data: schemas.UserUpdateRole, db: Session = Depends(get_db), admin: models.User = Depends(require_role(["admin"]))):
    if data.userId <= 0 or data.role not in ['admin', 'guardian', 'user']:
        raise HTTPException(status_code=400, detail="Datos inválidos para actualizar el rol.")
        
    user = db.query(models.User).filter(models.User.id == data.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="No se encontró el usuario.")
        
    user.role = data.role
    db.commit()
    
    return {
        "success": True,
        "message": "Rol actualizado correctamente.",
        "data": {
            "uid": user.id,
            "role": user.role
        }
    }

@router.post("/guardians")
def create_guardian(data: schemas.GuardianCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_role(["admin"]))):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="El email ya está registrado.")
        
    new_user = models.User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        role="guardian",
        displayName=data.displayName
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "message": "Guardián creado exitosamente.",
        "data": {
            "user": schemas.UserOut.model_validate(new_user)
        }
    }

@router.get("/routes")
def get_route_assignments(db: Session = Depends(get_db), admin: models.User = Depends(require_role(["admin"]))):
    assignments = db.query(models.GuardianRouteAssignment).order_by(models.GuardianRouteAssignment.guardian_user_id.asc()).all()
    assign_list = [
        {
            "guardianId": a.guardian_user_id,
            "routeId": a.route_id,
            "updatedAt": a.updated_at
        } for a in assignments
    ]
    return {
        "success": True,
        "message": "Asignaciones cargadas correctamente.",
        "data": {
            "assignments": assign_list
        }
    }

@router.post("/routes")
def assign_route(data: schemas.RouteAssignmentCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_role(["admin"]))):
    if data.guardianId <= 0 or not data.routeId:
        raise HTTPException(status_code=400, detail="Datos inválidos para asignación de ruta.")
        
    guardian = db.query(models.User).join(models.Role).filter(models.User.id == data.guardianId, models.Role.name == 'guardian').first()
    if not guardian:
        raise HTTPException(status_code=404, detail="El usuario no existe o no es guardián.")
        
    # Check if this specific route is already assigned to this guardian
    assignment = db.query(models.GuardianRouteAssignment).filter(
        models.GuardianRouteAssignment.guardian_user_id == data.guardianId,
        models.GuardianRouteAssignment.route_id == data.routeId
    ).first()
    
    if assignment:
        if assignment.status == 'completed':
            assignment.status = 'pending'
            db.commit()
        else:
            return {
                "success": True,
                "message": "La ruta ya se encuentra asignada a este guardián.",
                "data": {
                    "guardianId": data.guardianId,
                    "routeId": data.routeId
                }
            }
    else:
        # Check if the guardian has any active route currently
        has_active = db.query(models.GuardianRouteAssignment).filter(
            models.GuardianRouteAssignment.guardian_user_id == data.guardianId,
            models.GuardianRouteAssignment.status == 'in-progress'
        ).first()
        
        initial_status = 'in-progress' if not has_active else 'pending'
        
        assignment = models.GuardianRouteAssignment(
            guardian_user_id=data.guardianId,
            route_id=data.routeId,
            status=initial_status
        )
        db.add(assignment)
        db.commit()
        
    return {
        "success": True,
        "message": "Ruta asignada correctamente.",
        "data": {
            "guardianId": data.guardianId,
            "routeId": data.routeId
        }
    }


