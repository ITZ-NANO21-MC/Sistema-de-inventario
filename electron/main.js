const { app, BrowserWindow, ipcMain, session } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let flaskProcess;
let tunnelProcess;
let tunnelUrl = null;

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

  mainWindow.loadURL('http://localhost:5000');

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
      console.error(`Python no encontrado en: ${pythonPath}`);
      reject(new Error('Python no encontrado'));
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

    setTimeout(() => {
      if (flaskProcess && !flaskProcess.killed) {
        console.log('[Flask] Servidor iniciado en http://localhost:5000');
        resolve();
      } else {
        reject(new Error('Flask no inició correctamente'));
      }
    }, 3000);
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

    tunnelProcess = spawn(binaryPath, ['tunnel', '--url', 'http://localhost:5000'], {
      stdio: ['ignore', 'pipe', 'pipe']
    });

    tunnelProcess.stderr.on('data', (data) => {
      const output = data.toString();
      console.log(`[Cloudflare] ${output.trim()}`);
      
      const urlMatch = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
      if (urlMatch) {
        tunnelUrl = urlMatch[0];
        console.log(`[Tunnel] URL pública: ${tunnelUrl}`);
        
        if (mainWindow) {
          mainWindow.webContents.send('tunnel-url', tunnelUrl);
        }
        resolve(tunnelUrl);
      }
    });

    tunnelProcess.stdout.on('data', (data) => {
      console.log(`[Cloudflare stdout] ${data.toString().trim()}`);
    });

    tunnelProcess.on('error', (err) => {
      console.error(`[Tunnel] Error: ${err.message}`);
      reject(err);
    });

    setTimeout(() => {
      if (!tunnelUrl) {
        console.log('[Tunnel] No se pudo obtener URL. La app funciona localmente.');
        resolve(null);
      }
    }, 15000);
  });
}

async function startApp() {
  try {
    console.log('[App] Iniciando Flask...');
    await startFlask();
    
    console.log('[App] Iniciando túnel...');
    await startTunnel();
    
    createWindow();
  } catch (error) {
    console.error(`[App] Error al iniciar: ${error.message}`);
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
