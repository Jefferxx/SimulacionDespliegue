# 🗒️ Progreso de Despliegue — 23 y 24 de Abril, 2026

## 🏆 ESTADO FINAL: DESPLIEGUE SIMULADO EXITOSO AL 100% 🏆

## 🌐 Direcciones de Producción Simulada
- **IP del Servidor:** `192.168.42.128` (NAT)
- **Moodle LMS:** [http://192.168.42.128/moodle](http://192.168.42.128/moodle)
- **Dashboard ETalent:** [http://192.168.42.128/dashboard](http://192.168.42.128/dashboard)

## ✅ Hitos Alcanzados (Resumen Total)
1. **Infraestructura Base:** AlmaLinux 9.7 instalado con red NAT y acceso SSH mediante llaves Ed25519.
2. **Stack LAMP (Fases 3 y 4):** Apache 2.4, MySQL 8.0 y PHP 8.1 instalados. Moodle 4.5.11 (LTS) configurado y operativo.
3. **Entorno Python (Fases 5 a 8):** Python 3.11 instalado. Entorno virtual (`venv`) creado. Archivos del proyecto (`dashboard.py`, CSVs, configs) transferidos exitosamente vía SCP y dependencias instaladas.
4. **Servicio Systemd (Fase 9):** Dashboard configurado como un servicio del sistema (`streamlit-dashboard.service`) para arranque automático y persistencia, resolviendo errores de permisos `203/EXEC`.
5. **Proxy Reverso y SELinux (Fases 7 y 10):** Apache configurado como proxy reverso en el puerto 80 hacia el puerto 8501 interno. **Victoria sobre SELinux** permitiendo conexiones de red (`httpd_can_network_connect`, `httpd_can_network_relay`) y etiquetando puertos y ejecutables (`bin_t`, `http_port_t`) correctamente.

## 📋 Aprendizajes Clave para el Despliegue Real (CEDIA)
- **SELinux es estricto:** Los comandos `chcon`, `semanage` y `setsebool` son indispensables para que Apache funcione como proxy hacia Streamlit.
- **Systemd requiere precisión:** Las rutas absolutas en el archivo `.service` y los permisos de ejecución en toda la cadena de carpetas son vitales.
- **WebSockets:** La directiva `RewriteRule ws://...` en Apache es obligatoria para que Streamlit no se quede congelado.

¡Proyecto de simulación completado con excelencia!
