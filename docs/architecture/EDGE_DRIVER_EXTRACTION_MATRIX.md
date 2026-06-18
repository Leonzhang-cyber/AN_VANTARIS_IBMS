# EDGE Driver Extraction Matrix

| Driver | Protocol | Source Path | Coupling Risk | Extractability | Target EDGE Layer | Action |
| ------ | -------- | ----------- | ------------- | -------------- | ----------------- | ------ |
| `base_driver.py` | base abstraction | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/base_driver.py` | Low | READY_TO_WRAP | protocol-plugin | wrap-first |
| `http_driver.py` | HTTP/HTTPS | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/http_driver.py` | Medium | NEEDS_ADAPTER | connector-adapter | adapter-first |
| `isapi_driver.py` | ISAPI | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isapi_driver.py` | High | NEEDS_REWRITE | rewrite-required | rewrite-before-use |
| `isup_driver.py` | ISUP/Ehome | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isup_driver.py` | High | NEEDS_ADAPTER | connector-adapter | decouple-sse-first |
| `modbus_driver.py` | Modbus | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/modbus_driver.py` | Medium | NEEDS_REWRITE | rewrite-required | rewrite-before-use |
| `mqtt_driver.py` | MQTT | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/mqtt_driver.py` | High | NEEDS_ADAPTER | normalization-adapter | decouple-dao-first |
| `rtsp_driver.py` | RTSP/RTP | `AN_VANTARIS_IBMS-backend/src/Iot/drivers/rtsp_driver.py` | High | SIMULATOR_ONLY | simulator-only | leave-legacy |
