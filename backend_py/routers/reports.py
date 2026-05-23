from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db, get_current_user, require_role
import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return {
        "success": True,
        "message": "Reportes cargados correctamente.",
        "data": {
            "reports": [schemas.ReportOut.model_validate(r) for r in reports]
        }
    }

@router.post("")
def create_report(
    data: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # If reporter_name is not provided, use user email/displayName
    reporter = data.reporter_name or current_user.displayName or current_user.email.split('@')[0]
    
    new_report = models.Report(
        address=data.address,
        neighborhood=data.neighborhood,
        type=data.type,
        latitude=data.latitude,
        longitude=data.longitude,
        observations=data.observations,
        reporter_name=reporter,
        has_evidence=data.has_evidence,
        status="pending"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return {
        "success": True,
        "message": "Reporte registrado correctamente.",
        "data": {
            "report": schemas.ReportOut.model_validate(new_report)
        }
    }

@router.put("/{report_id}/status")
def update_report_status(
    report_id: int,
    data: schemas.ReportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "guardian"]))
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
        
    valid_statuses = ["pending", "in-progress", "completed"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Estado de reporte inválido.")
        
    report.status = data.status
    if data.status == "in-progress":
        report.assigned_guardian_id = current_user.id
    elif data.status == "completed":
        report.assigned_guardian_id = current_user.id
    else:
        report.assigned_guardian_id = None
        
    db.commit()
    db.refresh(report)
    
    return {
        "success": True,
        "message": f"Estado de reporte actualizado a {data.status}.",
        "data": {
            "report": schemas.ReportOut.model_validate(report)
        }
    }
