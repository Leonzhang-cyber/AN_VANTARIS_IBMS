# EDGE A0 Source Audit Input

- READY_TO_WRAP: `base_driver.py`
- NEEDS_ADAPTER: `http_driver.py`, `isup_driver.py`, `mqtt_driver.py`
- NEEDS_REWRITE: `isapi_driver.py`, `modbus_driver.py`
- SIMULATOR_ONLY: `rtsp_driver.py`
- `opcua_driver.py` missing

High-risk coupling list:

- DAO/model coupling in `mqtt_driver.py`
- SSE/API coupling in `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py`
- credential handling risk in `isapi_driver.py`, `mqtt_driver.py`
- socket/thread lifecycle risk in `isup_driver.py`, `rtsp_driver.py`
