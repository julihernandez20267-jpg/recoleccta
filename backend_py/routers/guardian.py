from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db, require_role
import models, schemas

router = APIRouter(prefix="/guardian", tags=["guardian"])

@router.get("/route")
def get_guardian_route(guardianId: int, db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "guardian"]))):
    if guardianId <= 0:
        raise HTTPException(status_code=400, detail="guardianId es obligatorio.")
        
    # Validar que el usuario que consulta sea admin o él mismo
    if user.role != "admin" and user.id != guardianId:
        raise HTTPException(status_code=403, detail="No puedes ver la ruta de otro guardián.")
        
    guardian = db.query(models.User).join(models.Role).filter(models.User.id == guardianId, models.Role.name == 'guardian').first()
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardián no encontrado.")
        
    assignments = db.query(models.GuardianRouteAssignment).filter(
        models.GuardianRouteAssignment.guardian_user_id == guardianId,
        models.GuardianRouteAssignment.status != 'completed'
    ).all()
    
    assignments_list = []
    for a in assignments:
        route_obj = db.query(models.Route).filter(models.Route.id == a.route_id).first()
        if route_obj:
            assignments_list.append({
                "routeId": a.route_id,
                "status": a.status,
                "updatedAt": a.updated_at,
                "route": {
                    "id": route_obj.id,
                    "name": route_obj.name,
                    "zone": route_obj.zone,
                    "points": route_obj.points
                }
            })

    active_assignment = next((a for a in assignments_list if a["status"] == "in-progress"), None)

    return {
        "success": True,
        "message": "Asignaciones encontradas." if assignments_list else "Sin asignaciones activas.",
        "data": {
            "guardian": {
                "uid": guardian.id,
                "email": guardian.email,
                "displayName": guardian.displayName
            },
            "assignments": assignments_list,
            "assignment": active_assignment
        }
    }

@router.post("/route/complete")
def complete_guardian_route(
    guardianId: int, 
    routeId: str | None = None,
    db: Session = Depends(get_db), 
    user: models.User = Depends(require_role(["admin", "guardian"]))
):
    if guardianId <= 0:
        raise HTTPException(status_code=400, detail="guardianId es obligatorio.")
        
    if user.role != "admin" and user.id != guardianId:
        raise HTTPException(status_code=403, detail="No puedes completar la ruta de otro guardián.")
        
    if routeId:
        assignment = db.query(models.GuardianRouteAssignment).filter(
            models.GuardianRouteAssignment.guardian_user_id == guardianId,
            models.GuardianRouteAssignment.route_id == routeId
        ).first()
    else:
        assignment = db.query(models.GuardianRouteAssignment).filter(
            models.GuardianRouteAssignment.guardian_user_id == guardianId,
            models.GuardianRouteAssignment.status == 'in-progress'
        ).first()
        
    if not assignment:
        raise HTTPException(status_code=404, detail="No tienes ninguna ruta asignada activa actualmente.")
        
    db.delete(assignment)
    db.commit()
    
    # Activate the next pending route assignment if any exists
    next_pending = db.query(models.GuardianRouteAssignment).filter(
        models.GuardianRouteAssignment.guardian_user_id == guardianId,
        models.GuardianRouteAssignment.status == 'pending'
    ).order_by(models.GuardianRouteAssignment.updated_at.asc()).first()
    
    if next_pending:
        next_pending.status = 'in-progress'
        db.commit()
    
    return {
        "success": True,
        "message": "Ruta completada y asignación liberada exitosamente."
    }



