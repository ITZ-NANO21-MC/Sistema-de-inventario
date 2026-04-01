const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getTunnelUrl: () => ipcRenderer.invoke('get-tunnel-url'),
  onTunnelUrl: (callback) => {
    ipcRenderer.on('tunnel-url', (event, url) => callback(url));
  },
  openExternal: (url) => ipcRenderer.send('open-external', url)
});
