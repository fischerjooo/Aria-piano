"""Check BLE reconnect behavior is present in the deployed stable app."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
runtime=(ROOT/'src/app/runtime.js').read_text()
html=(ROOT/'index.html').read_text()
assert "navigator.bluetooth.getDevices()" in runtime
assert "devices.find(d=>d.id===saved.id)" in runtime
assert "rememberBLE(device)" in runtime
assert "disableBLEAutoReconnect()" in runtime
assert "window.addEventListener('pageshow'" in runtime
assert "document.addEventListener('visibilitychange'" in runtime
assert "scheduleBLEReconnect(3000)" in runtime
assert "window.addEventListener('pagehide'" in runtime
assert "window.addEventListener('pagehide',()=>{stopMic();clearTimeout(bleRetryTimer)" in runtime, "Preserve page-session BluetoothDevice across background/foreground"
assert "if(!navigator.bluetooth?.getDevices)" in runtime
assert "bleDevice?.id===saved.id&&bleDevice?.gatt" in runtime, "Reuse already authorized in-memory GATT device"
assert "device=devices.find(d=>d.id===saved.id)" in runtime, "Never use an unrecognized piano"
assert "after reopening. Automatic reconnection works while Aria stays open." in runtime
assert "Automatic reconnect is unavailable in this browser." not in runtime, "Avoid misleading old error"
assert "bleDevice?.gatt||navigator.bluetooth?.getDevices" in runtime
assert "function disconnectBLE(userInitiated=true)" in runtime
assert "if(userInitiated===true)disableBLEAutoReconnect()" in runtime
assert "autoConnectBLE();" in runtime
assert "navigator.bluetooth.getDevices()" in html
assert (ROOT/'dist/index.html').read_text()==html
print('PASS remembered BLE device, permission-safe reconnect and main app generation')
