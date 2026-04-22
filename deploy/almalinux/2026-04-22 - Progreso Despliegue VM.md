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
5. **Fase 3:** Instalación de **Apache 2.4** y **MySQL 8.0** completada. Firewall configurado. PHP 8.1 en proceso.

## 🛠️ Notas Técnicas
- MySQL 8.0 instalado como versión nativa de AlmaLinux 9.
- Repositorio Remi añadido para soportar PHP 8.1 (requerido por Moodle 4.x).
