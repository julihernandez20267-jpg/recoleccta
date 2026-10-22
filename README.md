# Recoleccta - Plataforma de Gestión Ambiental y Reciclaje ♻️

**Recoleccta** es una plataforma móvil y backend diseñada para optimizar y reportar puntos de recolección de basura o contenedores llenos, facilitando el trabajo cooperativo entre los administradores, ciudadanos (usuarios) y personal operativo (guardianes).

---

## 🛠️ Stack Tecnológico

### Frontend (Móvil)
- **Framework:** [Expo](https://expo.dev) / React Native (TypeScript).
- **Enrutamiento:** Expo Router (basado en sistema de archivos).
- **Gestión de Estado:** [Zustand](https://github.com/pmndrs/zustand) (Persistencia de sesión segura y estado de autenticación).
- **Mapas:** `react-native-maps` integrado con el proveedor de Google Maps.
- **Áreas Seguras:** `react-native-safe-area-context` para prevención de recortes en teléfonos modernos.

### Backend (API)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python).
- **OR/M:** SQLAlchemy (Modelos y relaciones relacionales).
- **Base de Datos:** MySQL (Alojado en la nube con Aiven DB).
- **Recuperación OTP:** Envío de correos asíncronos mediante SMTP nativo y plantillas de correo en HTML.

---

## 🚀 Características Principales

1. **Sistema RBAC Relacional:**
   - Control de acceso basado en roles (`admin`, `guardian`, `user`) y permisos específicos almacenados de forma relacional en la base de datos (`roles`, `permissions`, `role_permissions`).
   - Llave foránea directa del rol en la tabla `users` con una propiedad dinámica `@property` para mantener compatibilidad hacia atrás en todo el código.

2. **Gestión de Rutas y Waypoints para Guardianes:**
   - Visualización diferenciada en el mapa operativo: ruta activa en **Verde**, rutas pendientes en cola en **Rojo**. Las rutas completadas desaparecen dinámicamente del mapa.
   - Control interactivo de waypoints (puntos de recolección): botón para avanzar dinámicamente de izquierda a derecha. El punto activo se agranda y resalta en el mapa sin recortes visuales.
   - Botón de término inmediato que finaliza la ruta en curso y activa de inmediato la siguiente asignación pendiente en cola.

3. **Recuperación de Contraseña con OTP Alfanumérico:**
   - Solicitud de código temporal de 6 dígitos enviado por correo electrónico.
   - Validación y actualización de contraseña en caliente con almacenamiento de expiración de token en backend.

4. **Gestión de Foto de Perfil en Base64:**
   - Carga de imágenes desde el carrete en Perfil de Usuario y Perfil de Guardián.
   - Conversión automática a Base64 y almacenamiento optimizado en la base de datos como columna de tipo `MEDIUMTEXT` en MySQL para evitar cualquier límite de tamaño o truncamiento.

5. **Optimización de UX Móvil:**
   - Corrección de área segura en pantallas críticas (como el Login) para evitar superposiciones con los botones físicos o virtuales de navegación del teléfono.
   - Detección de inactividad de sesión mediante un listener de eventos burbuja (`onTouchStart`) que no interfiere ni bloquea el deslizamiento vertical (scroll) del usuario.

---

## 💻 Guía de Instalación y Ejecución

### Requisitos Previos
- Node.js (v18 o superior)
- Python (v3.10 o superior)
- Expo Go instalado en un dispositivo móvil o un simulador móvil configurado.

---

### 1. Servidor Backend (Python)

1. Navega al directorio del backend:
   ```bash
   cd backend_py
   ```
2. Crea e inicia un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```
3. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las variables de entorno en un archivo `.env` dentro de `backend_py/`:
   ```env
   DB_HOST=tu_host_aiven_mysql
   DB_PORT=puerto_mysql
   DB_NAME=defaultdb
   DB_USER=tu_usuario
   DB_PASS=tu_contraseña

   JWT_SECRET=tu_secreto_jwt
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # Configuración de Correo para OTP
   MAIL_USERNAME=tu_correo_smtp@gmail.com
   MAIL_PASSWORD=tu_contraseña_aplicacion_smtp
   MAIL_FROM=tu_correo_remitente@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com
   MAIL_FROM_NAME=Recollecta
   MAIL_STARTTLS=True
   MAIL_SSL_TLS=False
   ```
5. Ejecuta las migraciones y siembra de base de datos inicial:
   ```bash
   python seed.py
   ```
6. Inicia el servidor de desarrollo Uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

---

### 2. Aplicación Móvil (Expo)

1. En la raíz del proyecto, instala las dependencias de Node:
   ```bash
   npm install
   ```
2. Configura la URL de tu backend en un archivo `.env` en la raíz del proyecto:
   ```env
   EXPO_PUBLIC_API_URL=https://tu-api.onrender.com/api
   ```
   Para desarrollo local, usa la IP de tu computador si pruebas desde un dispositivo físico (o `http://10.0.2.2:8001/api` en el emulador de Android). Reinicia Expo después de cambiar esta variable.
3. Inicia el servidor del empaquetador de Expo:
   ```bash
   npx expo start
   ```
4. Abre la consola de Expo, escanea el código QR con la app **Expo Go** en tu dispositivo físico, o presiona `a` para Android o `i` para iOS para abrirlo en tu emulador.

---

### 3. Volver a desplegar el backend en Render

1. En Render, crea un **Web Service** y conéctalo al repositorio `julihernandez20267-jpg/recoleccta` de GitHub.
2. Selecciona **Docker** como entorno y establece `backend_py` como **Root Directory**. Render construirá el servicio con `backend_py/Dockerfile`.
3. Crea una base de datos MySQL nueva en un proveedor que puedas usar y copia su URL de conexión. La aplicación usa MySQL; no reemplaces esta URL por una conexión PostgreSQL.
4. En las variables de entorno del servicio de Render, configura `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASS` con los datos de conexión MySQL; configura `DB_SSL_CA` con el contenido del certificado CA descargado desde Aiven, y `JWT_SECRET` con un secreto nuevo y largo. Genera también un valor secreto para `INITIAL_ADMIN_PASSWORD`; se usará únicamente para crear la cuenta inicial `admin@recoleccta.com`. Agrega las variables `MAIL_*` si quieres habilitar recuperación de contraseña por correo. No publiques credenciales ni certificados en GitHub ni los compartas en mensajes.
5. Cuando Render termine el despliegue, copia la URL pública del Web Service y configúrala en el `.env` de la raíz como `EXPO_PUBLIC_API_URL=https://tu-api.onrender.com/api`. Esa URL se incluye al iniciar Expo o al generar una nueva compilación de la app.
6. Inicializa la base de datos nueva ejecutando `python seed.py` desde `backend_py` con las variables de conexión de esa base. Una base nueva no contiene los usuarios ni reportes guardados en la anterior.

La URL antigua `https://recoleccta-app.onrender.com` puede dejar de responder; la aplicación seguirá usando esa dirección de respaldo hasta que configures `EXPO_PUBLIC_API_URL`.
