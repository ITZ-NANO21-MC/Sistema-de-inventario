# Integración de Túneles en Electron (Windows 11)

Para que tu aplicación de inventario se exponga automáticamente al abrirse en Windows 11, seguiremos el patrón de **"Sidecar Executable"**.

---

## 🏗️ 1. Estructura del Proyecto
Debes incluir el binario de Cloudflare (`cloudflared.exe`) en una carpeta de recursos:

```
inventario_app/
├── package.json
├── main.js (Proceso de Electron)
├── backend/ (Tu app Flask)
└── resources/
    └── binaries/
        └── cloudflared.exe  <-- Descarga el de Windows 64-bit
```

---

## ⚙️ 2. Configuración en `package.json`
Usa `electron-builder` para que el archivo `.exe` se incluya en el paquete final:

```json
"build": {
  "extraResources": [
    {
      "from": "resources/binaries/",
      "to": "binaries/",
      "filter": ["**/*"]
    }
  ]
}
```

---

## 💻 3. Código en `main.js` (Electron)
Este código iniciará el túnel automáticamente al abrir la app:

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let tunnelProcess;

function startTunnel() {
    // Determinar la ruta del binario (desarrollo vs producción)
    const binaryPath = app.isPackaged 
        ? path.join(process.resourcesPath, 'binaries', 'cloudflared.exe')
        : path.join(__dirname, 'resources', 'binaries', 'cloudflared.exe');

    // Iniciar túnel rápido de Cloudflare
    tunnelProcess = spawn(binaryPath, ['tunnel', '--url', 'http://localhost:5000']);

    tunnelProcess.stderr.on('data', (data) => {
        const output = data.toString();
        // Cloudflare imprime la URL en el stderr
        const urlMatch = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
        if (urlMatch) {
            console.log("URL de acceso remoto:", urlMatch[0]);
            // Enviar la URL a la ventana de Electron para mostrarla al usuario
            BrowserWindow.getAllWindows()[0].webContents.send('tunnel-url', urlMatch[0]);
        }
    });
}

app.whenReady().then(() => {
    createWindow();
    startTunnel(); // Iniciar automáticamente
});

app.on('window-all-closed', () => {
    if (tunnelProcess) tunnelProcess.kill(); // Cerrar túnel al salir
    if (process.platform !== 'darwin') app.quit();
});
```

---

## 💎 Ventajas de este Enfoque
1.  **Cero Configuración**: El usuario final solo abre el `.exe` y la app le muestra su URL pública.
2.  **Sin Advertencias**: A diferencia de ngrok, el túnel de Cloudflare entra directo.
3.  **Seguridad**: El túnel se cierra automáticamente cuando el usuario cierra la aplicación de Electron.

---

## ⚠️ Consideración para el Despliegue
Como estás en **Linux**, para compilar para **Windows** necesitarás usar `electron-builder` con soporte para multi-plataforma (o usar un CI/CD como GitHub Actions). Recuerda descargar el `cloudflared.exe` de Windows y ponerlo en la carpeta `resources/binaries/` de tu proyecto.
