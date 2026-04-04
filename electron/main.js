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

/**
 * Devuelve la ruta al ejecutable del backend generado con PyInstaller
 * (solo en modo producción).
 */
function getBackendExecutable() {
  const isDev = !app.isPackaged;
  if (isDev) return null;
  const platform = process.platform;
  const backendDir = path.join(process.resourcesPath, 'backend', 'dist', 'inventario_backend');
  if (platform === 'win32') {
    return path.join(backendDir, 'inventario_backend.exe');
  } else if (platform === 'linux') {
    return path.join(backendDir, 'inventario_backend');
  } else if (platform === 'darwin') {
    return path.join(backendDir, 'inventario_backend');
  }
  return null;
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

  mainWindow.loadURL('http://127.0.0.1:5000');

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    if (errorDescription === 'ERR_CONNECTION_REFUSED' || errorCode === -102) {
      console.log('[App] Esperando a que el backend esté listo... (Reintentando carga)');
      setTimeout(() => {
        if (mainWindow) mainWindow.loadURL('http://127.0.0.1:5000');
      }, 1000);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startFlask() {
  return new Promise((resolve, reject) => {
    const isDev = !app.isPackaged;
    const backendExecutable = getBackendExecutable();

    if (isDev || !backendExecutable || !fs.existsSync(backendExecutable)) {
      // --- MODO DESARROLLO: usar Python con entorno virtual ---
      console.log('[App] Modo desarrollo. Usando Python...');
      const projectRoot = getProjectRoot();
      let pythonPath;
      if (process.platform === 'win32') {
        pythonPath = path.join(projectRoot, 'venv', 'Scripts', 'python.exe');
      } else {
        pythonPath = path.join(projectRoot, 'venv', 'bin', 'python');
      }
      if (!fs.existsSync(pythonPath)) {
        reject(new Error(`Python no encontrado en ${pythonPath}`));
        return;
      }
      flaskProcess = spawn(pythonPath, ['run.py'], {
        cwd: projectRoot,
        env: { ...process.env, FLASK_DEBUG: 'False' },
        stdio: ['ignore', 'pipe', 'pipe']
      });
    } else {
      // --- MODO PRODUCCIÓN: usar el ejecutable de PyInstaller ---
      console.log(`[App] Iniciando backend empaquetado: ${backendExecutable}`);
      const backendDir = path.dirname(backendExecutable);

      // Sin variables de entorno personalizadas; solo el entorno del sistema
      flaskProcess = spawn(backendExecutable, [], {
        cwd: backendDir,
        env: { ...process.env, FLASK_DEBUG: 'False' },
        stdio: ['ignore', 'pipe', 'pipe']
      });
    }

    flaskProcess.stdout.on('data', (data) => {
      console.log(`[Flask] ${data.toString().trim()}`);
    });

    flaskProcess.stderr.on('data', (data) => {
      console.error(`[Flask Error] ${data.toString().trim()}`);
    });

    flaskProcess.on('error', (err) => {
      console.error(`[Flask] Error al iniciar: ${err.message}`);
      reject(err);
    });

    setTimeout(() => {
      if (flaskProcess && !flaskProcess.killed) {
        console.log('[Flask] Servidor iniciado en http://127.0.0.1:5000');
        resolve();
      } else {
        reject(new Error('El proceso de Flask se cerró inesperadamente.'));
      }
    }, 6000);
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

    tunnelProcess = spawn(binaryPath, ['tunnel', '--url', 'http://127.0.0.1:5000'], {
      stdio: ['ignore', 'pipe', 'pipe']
    });

    tunnelProcess.stderr.on('data', (data) => {
      const output = data.toString();
      const urlMatch = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
      if (urlMatch) {
        tunnelUrl = urlMatch[0];
        console.log(`[Tunnel] URL pública generada: ${tunnelUrl}`);
        registerTunnelWithFlask(tunnelUrl);
        if (mainWindow) {
          mainWindow.webContents.send('tunnel-url', tunnelUrl);
        }
        resolve(tunnelUrl);
      }
    });

    tunnelProcess.on('error', (err) => {
      console.error(`[Tunnel] Error al iniciar binario: ${err.message}`);
      resolve(null);
    });

    setTimeout(() => {
      if (!tunnelUrl) {
        console.warn('[Tunnel] Tiempo de espera agotado. Modo local únicamente.');
        resolve(null);
      }
    }, 20000);
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
