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
5. **Fase 3:** Instalación de **Apache 2.4** y configuración del **Firewall** (Puertos 80/443 abiertos).

## 🛠️ Notas Técnicas
- Se cambió la red de **Bridged** a **NAT** para estabilizar la asignación de IP y asegurar salida a internet.
- SSH configurado con el algoritmo `ed25519` por ser el más moderno y seguro.
- SELinux está en modo **Enforcing** (se mantendrá así para simular producción).
