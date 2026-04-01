const { app, BrowserWindow, ipcMain, session, net } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let flaskProcess;
let tunnelProcess;
let tunnelUrl = null;

/**
 * Registra la URL del túnel con el backend Flask para que sea visible en la UI.
 */
function registerTunnelWithFlask(url) {
  const request = net.request({
    method: 'POST',
    protocol: 'http:',
    hostname: '127.0.0.1',
    port: 5000,
    path: '/api/tunnel/register'
  });

  request.on('response', (response) => {
    console.log(`[Tunnel] Registro en backend exitoso (Status: ${response.statusCode})`);
  });

  request.on('error', (error) => {
    console.warn(`[Tunnel] Error al registrar en backend: ${error.message}. Reintentando...`);
    // Reintentar en 5 segundos (útil si Flask tarda más en estar listo para peticiones)
    setTimeout(() => registerTunnelWithFlask(url), 5000);
  });

  request.setHeader('Content-Type', 'application/json');
  request.write(JSON.stringify({ url: url, tipo: 'cloudflared' }));
  request.end();
}

function getBinaryPath(binaryName) {
  const isDev = !app.isPackaged;
  if (isDev) {
    return path.join(__dirname, 'resources', 'binaries', binaryName);
  }
  return path.join(process.resourcesPath, 'binaries', binaryName);
}

function getProjectRoot() {
  const isDev = !app.isPackaged;
  if (isDev) {
    return path.join(__dirname, 'backend');
  }
  return path.join(process.resourcesPath, 'backend');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'Sistema de Inventario',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  // Carga inicial
  mainWindow.loadURL('http://127.0.0.1:5000');

  // Si la carga falla (p.ej. Flask aún no acepta peticiones), reintentar automáticamente
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    if (errorDescription === 'ERR_CONNECTION_REFUSED' || errorCode === -102) {
      console.log('[App] Esperando a que el backend esté listo... (Reintentando carga)');
      setTimeout(() => {
        if (mainWindow) mainWindow.loadURL('http://127.0.0.1:5000');
      }, 1000); // Reintentar cada segundo
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startFlask() {
  return new Promise((resolve, reject) => {
    const projectRoot = getProjectRoot();
    const pythonPath = process.platform === 'win32' 
      ? path.join(projectRoot, 'venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, 'venv', 'bin', 'python');

    if (!fs.existsSync(pythonPath)) {
      console.error(`[App] Python no encontrado en: ${pythonPath}`);
      reject(new Error(`Entorno virtual no encontrado en ${pythonPath}. Ejecuta prepare_backend primero.`));
      return;
    }

    flaskProcess = spawn(pythonPath, ['run.py'], {
      cwd: projectRoot,
      env: { ...process.env, FLASK_DEBUG: 'False' },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    flaskProcess.stdout.on('data', (data) => {
      console.log(`[Flask] ${data.toString().trim()}`);
    });

    flaskProcess.stderr.on('data', (data) => {
      const output = data.toString();
      console.error(`[Flask Error] ${output.trim()}`);
    });

    flaskProcess.on('error', (err) => {
      console.error(`[Flask] Error al iniciar: ${err.message}`);
      reject(err);
    });

    // Aumentar tiempo de espera para que Flask inicie correctamente
    setTimeout(() => {
      if (flaskProcess && !flaskProcess.killed) {
        console.log('[Flask] Servidor iniciado en http://127.0.0.1:5000');
        resolve();
      } else {
        reject(new Error('El proceso de Flask se cerró inesperadamente.'));
      }
    }, 6000); // 6 segundos de gracia
  });
}

function startTunnel() {
  return new Promise((resolve, reject) => {
    const isWindows = process.platform === 'win32';
    const binaryName = isWindows ? 'cloudflared.exe' : 'cloudflared';
    const binaryPath = getBinaryPath(binaryName);

    if (!fs.existsSync(binaryPath)) {
      console.warn(`[Tunnel] Binario no encontrado en: ${binaryPath}`);
      console.warn('[Tunnel] La aplicación funcionará solo localmente.');
      resolve(null);
      return;
    }

    // Iniciar túnel apuntando a 127.0.0.1:5000
    tunnelProcess = spawn(binaryPath, ['tunnel', '--url', 'http://127.0.0.1:5000'], {
      stdio: ['ignore', 'pipe', 'pipe']
    });

    tunnelProcess.stderr.on('data', (data) => {
      const output = data.toString();
      
      const urlMatch = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
      if (urlMatch) {
        tunnelUrl = urlMatch[0];
        console.log(`[Tunnel] URL pública generada: ${tunnelUrl}`);
        
        // Notificar al backend Flask para que aparezca en el panel de configuración
        registerTunnelWithFlask(tunnelUrl);
        
        if (mainWindow) {
          mainWindow.webContents.send('tunnel-url', tunnelUrl);
        }
        resolve(tunnelUrl);
      }
    });

    tunnelProcess.on('error', (err) => {
      console.error(`[Tunnel] Error al iniciar binario: ${err.message}`);
      resolve(null); // No bloquear la app si falla el túnel
    });

    // Timeout para el túnel (Cloudflare puede tardar en responder)
    setTimeout(() => {
      if (!tunnelUrl) {
        console.warn('[Tunnel] Tiempo de espera agotado. Modo local únicamente.');
        resolve(null);
      }
    }, 20000); // 20 segundos para el túnel
  });
}

async function startApp() {
  try {
    console.log('[App] Iniciando backend Flask...');
    await startFlask();
    
    console.log('[App] Iniciando túnel de acceso remoto...');
    await startTunnel();
    
    createWindow();
  } catch (error) {
    console.error(`[App] Error crítico en inicio: ${error.message}`);
    // Intentar abrir la ventana de todos modos para mostrar errores si los hay
    createWindow();
  }
}

app.whenReady().then(() => {
  startApp();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  cleanup();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  cleanup();
});

function cleanup() {
  console.log('[App] Limpiando procesos...');
  
  if (tunnelProcess && !tunnelProcess.killed) {
    tunnelProcess.kill();
    console.log('[Tunnel] Túnel cerrado.');
  }
  
  if (flaskProcess && !flaskProcess.killed) {
    flaskProcess.kill();
    console.log('[Flask] Servidor Flask cerrado.');
  }
}

ipcMain.handle('get-tunnel-url', () => {
  return tunnelUrl;
});

ipcMain.on('open-external', (event, url) => {
  require('electron').shell.openExternal(url);
});
