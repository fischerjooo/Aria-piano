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
assert "disconnectBLE(false)" in runtime
assert "autoConnectBLE();" in runtime
assert "navigator.bluetooth.getDevices()" in html
assert (ROOT/'dist/index.html').read_text()==html
print('PASS remembered BLE device, permission-safe reconnect and main app generation')
