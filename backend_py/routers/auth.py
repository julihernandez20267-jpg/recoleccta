from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from core.deps import get_db, get_current_user
from core.security import verify_password, get_password_hash, create_access_token
from core.email import send_otp_email
from datetime import datetime, timedelta
import models, schemas
import secrets
import json
import base64
import string


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos.")
    
    token = create_access_token(subject=user.id, extra_data={"email": user.email, "role": user.role})
    return {
        "success": True,
        "message": "Inicio de sesión exitoso.",
        "data": {
            "user": schemas.UserOut.model_validate(user),
            "token": token
        }
    }

@router.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    valid_roles = ["guardian", "user"]
    role = user_data.role if user_data.role in valid_roles else "user"
    
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está registrado.")
    
    new_user = models.User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(subject=new_user.id, extra_data={"email": new_user.email, "role": new_user.role})
    return {
        "success": True,
        "message": "Registro exitoso.",
        "data": {
            "user": schemas.UserOut.model_validate(new_user),
            "token": token
        }
    }

@router.post("/login-google")
def login_google(google_data: schemas.UserGoogleLogin, db: Session = Depends(get_db)):
    try:
        parts = google_data.idToken.split('.')
        if len(parts) != 3:
            raise ValueError()
        
        # Pad base64 if needed
        payload_b64 = parts[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
        payload = json.loads(payload_json)
        
        email = payload.get("email")
        if not email:
            raise ValueError("Token no contiene email")
            
    except Exception:
        raise HTTPException(status_code=400, detail="Token JWT inválido.")

    role = google_data.role if google_data.role in ["admin", "guardian", "user"] else "user"
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        random_password = secrets.token_hex(16)
        user = models.User(
            email=email,
            password_hash=get_password_hash(random_password),
            role=role,
            displayName=payload.get("name"),
            photoURL=payload.get("picture")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=user.id, extra_data={"email": user.email, "role": user.role})
    return {
        "success": True,
        "message": "Login con Google exitoso.",
        "data": {
            "user": schemas.UserOut.model_validate(user),
            "token": token
        }
    }

@router.post("/recover-password/request")
def request_recover_password(
    data: schemas.RecoverPassword, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta asociada a ese correo.")
        
    # Generate 6-digit alphanumeric OTP
    alphabet = string.ascii_uppercase + string.digits
    otp_code = "".join(secrets.choice(alphabet) for _ in range(6))
    
    user.otp_code = otp_code
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # Send email in background
    background_tasks.add_task(send_otp_email, user.email, otp_code)
    
    return {
        "success": True,
        "message": "Código de verificación enviado a tu correo."
    }

@router.post("/recover-password/reset")
def reset_password(
    data: schemas.ResetPasswordWithOTP, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    if not user.otp_code or user.otp_code.upper() != data.code.strip().upper():
        raise HTTPException(status_code=400, detail="El código de verificación es incorrecto.")
        
    if not user.otp_expiry or user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El código de verificación ha expirado.")
        
    # Update password and clear OTP fields
    user.password_hash = get_password_hash(data.new_password)
    user.otp_code = None
    user.otp_expiry = None
    db.commit()
    
    return {
        "success": True,
        "message": "Contraseña restablecida correctamente."
    }


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "success": True,
        "message": "Sesión válida.",
        "data": {
            "user": schemas.UserOut.model_validate(current_user),
        }
    }

@router.get("/refresh")
def refresh_token(current_user: models.User = Depends(get_current_user)):
    token = create_access_token(subject=current_user.id, extra_data={"email": current_user.email, "role": current_user.role})
    return {
        "success": True,
        "message": "Token renovado correctamente.",
        "data": {
            "user": schemas.UserOut.model_validate(current_user),
            "token": token
        }
    }

@router.put("/profile")
def update_profile(
    profile_data: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_data.displayName is not None:
        current_user.displayName = profile_data.displayName
    if profile_data.photoURL is not None:
        current_user.photoURL = profile_data.photoURL
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "message": "Perfil actualizado correctamente.",
        "data": {
            "user": schemas.UserOut.model_validate(current_user)
        }
    }

