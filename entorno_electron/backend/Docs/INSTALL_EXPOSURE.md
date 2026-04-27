# Guía de Exposición Local: Inventario App

Esta guía te ayudará a exponer tu servidor Flask (`http://127.0.0.1:5000`) para que sea accesible desde cualquier dispositivo con internet.

---

## 🚀 Opción Recomendada: Cloudflare Tunnel (Gratis y sin avisos)

### 1. Instalación (Linux)
Descarga el binario oficial de Cloudflare:

```bash
# Descargar el .deb para sistemas basados en Debian/Ubuntu
curl -LO https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Instalar
sudo dpkg -i cloudflared.deb
```

### 2. Ejecución (Túnel Rápido)
No necesitas cuenta si solo quieres una URL temporal (pero muy estable):

```bash
cloudflared tunnel --url http://localhost:5000
```

**Resultado:** Verás una URL similar a `https://random-words-generated.trycloudflare.com`. ¡Esa es la URL que debes abrir en tu teléfono!

---

## 🛠️ Opción Alternativa: zrok (Open Source)

### 1. Instalación
```bash
# Descargar e instalar zrok (vía script oficial)
curl -sSL https://get.zrok.io | sudo bash
```

### 2. Registro y Activación
1.  Ve a [my.zrok.io](https://my.zrok.io) y crea una cuenta.
2.  Copia tu **Enable Token** desde el panel.
3.  En tu terminal: `zrok enable <tu_token>`

### 3. Compartir
```bash
zrok share public http://localhost:5000
```

---

## 💡 Consejos para el Proyecto de Inventario

1.  **Configuración de Flask**: Normalmente basta con `http://localhost:5000`. No necesitas cambiar nada en `run.py` para que el túnel funcione.
2.  **Seguridad**: El túnel expone TODO lo que esté en el puerto 5000. No compartas la URL con personas no autorizadas.
3.  **Mantenimiento**: Si apagas la PC, la URL dejará de funcionar. Si usas Cloudflare con un dominio propio, puedes hacer que el túnel se inicie como un servicio del sistema (`sudo cloudflared service install`).
