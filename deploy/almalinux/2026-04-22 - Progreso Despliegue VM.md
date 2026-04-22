# 🗒️ Progreso de Despliegue — 22 de Abril, 2026

## 🔐 Credenciales del Servidor (Simulación)
> [!warning] Seguridad
> Estas credenciales son solo para el entorno de simulación local.

| Usuario | Password | Rol |
| :--- | :--- | :--- |
| `admin` | `AlmaLinux` | Administrador inicial (Sudoer) |
| `deployer` | `AlmaLinux` | Usuario de despliegue (Simulación CEDIA) |

## 🌐 Información de Red
- **IP Local (NAT):** `192.168.42.128`
- **Hostname:** `dashboard-server.local`

## ✅ Hitos Alcanzados Hoy
1. **Fase 0:** Creación de repositorio en GitHub `SimulacionDespliegue` y rama `feature/despliegue-almalinux`.
2. **Fase 1:** Instalación exitosa de AlmaLinux 9.7 (Minimal) en VMware Workstation.
3. **Fase 1:** Actualización de sistema (`dnf update`) e instalación de herramientas base (`vim`, `wget`, `git`, `selinux utils`).
4. **Fase 2:** Configuración de **SSH Key Authentication** exitosa (Windows -> VM sin contraseña).
5. **Fase 3:** Instalación del **Stack LAMP** (Apache 2.4, MySQL 8.0, PHP 8.1) completada exitosamente.
6. **Fase 4:** Moodle LTS configurado exitosamente. Directorio `/moodle` accesible y Apache reiniciado sin errores de sintaxis.

## 🏁 Estado al cierre del 22 de abril
- **Infraestructura:** VM con AlmaLinux 9.7 (NAT) operativa en `192.168.42.128`.
- **Software:** Stack LAMP (Apache 2.4, MySQL 8.0, PHP 8.1) verificado.
- **Acceso:** SSH Key configurada para `deployer`.
- **Próximo Paso:** Finalizar instalación web de Moodle e iniciar el despliegue del Dashboard Streamlit.
