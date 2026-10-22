import os

from database import SessionLocal, engine
import models
from core.security import get_password_hash
from sqlalchemy import text

def run_migrations(db):
    print("Ejecutando migraciones de base de datos...")
    
    # 1. Crear nuevas tablas (roles, permissions, role_permissions) si no existen
    models.Base.metadata.create_all(bind=engine)
    
    # 2. Agregar columnas a 'users' si no existen
    # Columna role_id
    try:
        db.execute(text("SELECT role_id FROM users LIMIT 1"))
    except Exception:
        print("Añadiendo columna role_id a tabla users...")
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN role_id INT NULL"))
            db.execute(text("ALTER TABLE users ADD CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error al añadir role_id: {e}")

    # Columna otp_code
    try:
        db.execute(text("SELECT otp_code FROM users LIMIT 1"))
    except Exception:
        print("Añadiendo columna otp_code a tabla users...")
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN otp_code VARCHAR(6) NULL"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error al añadir otp_code: {e}")

    # Columna otp_expiry
    try:
        db.execute(text("SELECT otp_expiry FROM users LIMIT 1"))
    except Exception:
        print("Añadiendo columna otp_expiry a tabla users...")
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN otp_expiry TIMESTAMP NULL"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error al añadir otp_expiry: {e}")

    # Modificar tipo de photoURL a MEDIUMTEXT
    try:
        print("Modificando columna photoURL a MEDIUMTEXT...")
        db.execute(text("ALTER TABLE users MODIFY COLUMN photoURL MEDIUMTEXT NULL"))
        db.commit()
        print("Columna photoURL modificada a MEDIUMTEXT correctamente.")
    except Exception as e:
        db.rollback()
        print(f"Nota/Aviso al modificar photoURL: {e}")

    # 3. Migrar roles de la columna vieja (role string) a la nueva (role_id)
    try:
        print("Migrando roles de string a FK...")
        db.execute(text("UPDATE users SET role_id = 1 WHERE role = 'admin' AND role_id IS NULL"))
        db.execute(text("UPDATE users SET role_id = 2 WHERE role = 'guardian' AND role_id IS NULL"))
        db.execute(text("UPDATE users SET role_id = 3 WHERE role = 'user' AND role_id IS NULL"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Nota: La columna role vieja no existe o ya fue migrada: {e}")

    # 4. Modificar 'guardian_route_assignments'
    # Remover índice único resolviendo dependencias de FK
    try:
        # Buscar el nombre de la restricción de llave foránea
        res_fk = db.execute(text("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'guardian_route_assignments' 
              AND COLUMN_NAME = 'guardian_user_id'
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """)).fetchall()
        
        for fk_row in res_fk:
            fk_name = fk_row[0]
            print(f"Eliminando FK temporalmente: {fk_name}...")
            try:
                db.execute(text(f"ALTER TABLE guardian_route_assignments DROP FOREIGN KEY {fk_name}"))
                db.commit()
            except Exception as e_fk:
                db.rollback()
                print(f"Error al eliminar FK: {e_fk}")
                
        # Ahora remover el índice único
        res_idx = db.execute(text("""
            SELECT INDEX_NAME 
            FROM information_schema.statistics 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'guardian_route_assignments' 
              AND COLUMN_NAME = 'guardian_user_id' 
              AND NON_UNIQUE = 0
        """)).fetchall()
        
        for row in res_idx:
            idx_name = row[0]
            if idx_name != 'PRIMARY':
                print(f"Eliminando índice único {idx_name} en guardian_route_assignments...")
                try:
                    db.execute(text(f"ALTER TABLE guardian_route_assignments DROP INDEX {idx_name}"))
                    db.commit()
                except Exception as ex:
                    db.rollback()
                    print(f"Error al eliminar índice único: {ex}")
                    
        # Recrear la llave foránea sin la restricción única
        for fk_row in res_fk:
            fk_name = fk_row[0]
            print(f"Recreando FK sin restricción única: {fk_name}...")
            try:
                db.execute(text(f"ALTER TABLE guardian_route_assignments ADD CONSTRAINT {fk_name} FOREIGN KEY (guardian_user_id) REFERENCES users(id) ON DELETE CASCADE"))
                db.commit()
            except Exception as e_re:
                db.rollback()
                print(f"Error al recrear FK: {e_re}")
                
    except Exception as e:
        print(f"Error buscando FKs o índices: {e}")


    # Columna status
    try:
        db.execute(text("SELECT status FROM guardian_route_assignments LIMIT 1"))
    except Exception:
        print("Añadiendo columna status a tabla guardian_route_assignments...")
        try:
            db.execute(text("ALTER TABLE guardian_route_assignments ADD COLUMN status ENUM('pending', 'in-progress', 'completed') NOT NULL DEFAULT 'pending'"))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error al añadir columna status: {e}")

def seed_db():
    db = SessionLocal()
    try:
        run_migrations(db)
        
        # 1. Seed Roles
        print("Sembrando roles...")

        roles_to_seed = [
            {"id": 1, "name": "admin"},
            {"id": 2, "name": "guardian"},
            {"id": 3, "name": "user"}
        ]
        for r in roles_to_seed:
            existing_role = db.query(models.Role).filter(models.Role.id == r["id"]).first()
            if not existing_role:
                new_role = models.Role(id=r["id"], name=r["name"])
                db.add(new_role)
        db.commit()

        # 2. Seed Permissions
        print("Sembrando permisos...")
        permissions_to_seed = [
            {"id": 1, "name": "create_route", "description": "Crear rutas de recolección"},
            {"id": 2, "name": "assign_route", "description": "Asignar rutas a guardianes"},
            {"id": 3, "name": "update_report_status", "description": "Actualizar estado de reportes"},
            {"id": 4, "name": "edit_profile", "description": "Editar datos de perfil"}
        ]
        for p in permissions_to_seed:
            existing_permission = db.query(models.Permission).filter(models.Permission.id == p["id"]).first()
            if not existing_permission:
                new_permission = models.Permission(id=p["id"], name=p["name"], description=p["description"])
                db.add(new_permission)
        db.commit()

        # 3. Seed Role-Permissions
        print("Sembrando mapeo rol-permiso...")
        # admin gets all: 1, 2, 3, 4
        # guardian gets: 3, 4
        # user gets: 4
        role_permissions_to_seed = [
            # Admin (role_id=1)
            {"role_id": 1, "permission_id": 1},
            {"role_id": 1, "permission_id": 2},
            {"role_id": 1, "permission_id": 3},
            {"role_id": 1, "permission_id": 4},
            # Guardian (role_id=2)
            {"role_id": 2, "permission_id": 3},
            {"role_id": 2, "permission_id": 4},
            # User (role_id=3)
            {"role_id": 3, "permission_id": 4},
        ]
        for rp in role_permissions_to_seed:
            existing_mapping = db.query(models.RolePermission).filter(
                models.RolePermission.role_id == rp["role_id"],
                models.RolePermission.permission_id == rp["permission_id"]
            ).first()
            if not existing_mapping:
                new_mapping = models.RolePermission(role_id=rp["role_id"], permission_id=rp["permission_id"])
                db.add(new_mapping)
        db.commit()
        
        # 4. Seed Admin User
        admin_email = "admin@recoleccta.com"
        admin = db.query(models.User).filter(models.User.email == admin_email).first()
        
        if not admin:
            admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
            if not admin_password:
                raise RuntimeError(
                    "Set INITIAL_ADMIN_PASSWORD before creating the initial admin user."
                )
            print(f"Creando usuario admin: {admin_email}")
            admin_user = models.User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                role_id=1, # Admin
                displayName="Administrador"
            )
            db.add(admin_user)
            db.commit()
            print("Usuario admin creado exitosamente.")
        else:
            print("El usuario admin ya existe. Actualizando rol a admin (id=1)...")
            admin.role_id = 1
            db.commit()
            
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
