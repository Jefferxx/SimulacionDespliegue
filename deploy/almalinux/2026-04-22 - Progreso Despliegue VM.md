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
6. **Fase 4 (En curso):** Preparación de Moodle 4.x (Base de datos creada, archivos descargados y permisos configurados).

## 🛠️ Notas Técnicas
- PHP 8.1 configurado con todas las extensiones requeridas por Moodle (intl, gd, xmlrpc, etc.).
- `/var/moodledata` configurado con el contexto de SELinux `httpd_sys_rw_content_t`.
