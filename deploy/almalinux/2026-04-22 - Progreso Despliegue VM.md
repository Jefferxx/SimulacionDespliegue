# 🗒️ Progreso de Despliegue — 22 de Abril, 2026

## 🔐 Credenciales del Servidor (Simulación)
> [!warning] Seguridad
> Estas credenciales son solo para el entorno de simulación local.

| Usuario | Password | Rol |
| :--- | :--- | :--- |
| `admin` | `AlmaLinux` | Administrador inicial (Sudoer) |
| `deployer` | `AlmaLinux` | Usuario de despliegue (Simulación CEDIA) |
| `Moodle Admin` | `AlmaLinux2024!` | Administrador del Aula Virtual |
| `DB Moodle` | `MoodlePass2024!` | Usuario de base de datos (moodleuser) |

## 🌐 Información de Red
- **IP Local (NAT):** `192.168.42.128`
- **Hostname:** `dashboard-server.local`
- **URL Moodle:** `http://192.168.42.128/moodle`

## ✅ Hitos Alcanzados Hoy
1. **Fase 0:** Repo GitHub y rama `feature/despliegue-almalinux` listos.
2. **Fase 1:** AlmaLinux 9.7 instalado, actualizado y con herramientas base.
3. **Fase 2:** Conexión SSH segura con llaves Ed25519 (Windows -> VM).
4. **Fase 3:** Stack LAMP (Apache 2.4, MySQL 8.0, PHP 8.1) configurado y optimizado.
5. **Fase 4:** Moodle 4.5.11 (LTS) instalado, configurado y funcional.

## 🏁 Estado al cierre del 22 de abril
- **Moodle:** Operativo y con cuenta de administrador creada.
- **Servidor:** Optimizado con `max_input_vars = 5000` y SELinux activo.
- **Próximo Paso:** Fase 5 - Despliegue del Dashboard Streamlit con Python 3.11.
