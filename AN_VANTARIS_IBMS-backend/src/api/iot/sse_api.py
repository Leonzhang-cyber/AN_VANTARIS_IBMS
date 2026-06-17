# src/api/iot/sse_api.py
"""
SSE (Server-Sent Events) 实时推送接口
每个设备独立的数据流
# 1. 测试 SSE 连接
curl -N "http://localhost:5000/api/iot/device/HVAC_SIM_001/stream"

# 2. 测试推送（手动触发）
curl -X POST "http://localhost:5000/api/iot/device/HVAC_SIM_001/test-sse-push"

# 3. 获取最新数据
curl "http://localhost:5000/api/iot/device/HVAC_SIM_001/latest"
"""

from flask import Response, stream_with_context, current_app
from src.api import api_bp
from src.common.utils.jwt_util import jwt_required
import json
import queue
import time
from datetime import datetime

# 存储每个设备的订阅队列
_device_queues = {}
# 存储每个设备的最新数据
_latest_data = {}


def get_device_queue(device_code: str) -> queue.Queue:
    """获取设备的消息队列"""
    if device_code not in _device_queues:
        _device_queues[device_code] = queue.Queue(maxsize=100)
    return _device_queues[device_code]


def push_to_device(device_code: str, data: dict):
    """推送数据到设备队列（供 device_manager 调用）"""
    try:
        q = get_device_queue(device_code)
        q.put_nowait(data)
        _latest_data[device_code] = data
    except queue.Full:
        try:
            q.get_nowait()
            q.put_nowait(data)
        except:
            pass


def get_latest_data(device_code: str) -> dict:
    """获取设备最新数据"""
    return _latest_data.get(device_code, {})


def _sse_test_endpoint_allowed():
    """SECURITY-A8B: block test-sse-push in production; require feature flag in non-production."""
    from src.common.models.response import Result

    if current_app.config.get("IS_PRODUCTION", False):
        return Result.error(message="SSE test endpoint disabled in production", code=403)
    sim_on = current_app.config.get("SIMULATOR_ENABLED", False)
    testmqtt_on = current_app.config.get("TESTMQTT_ENABLED", False)
    if not sim_on and not testmqtt_on:
        return Result.error(
            message=(
                "SSE test endpoint requires IBMS_SIMULATOR_ENABLED or "
                "IBMS_TESTMQTT_ENABLED in non-production"
            ),
            code=403,
        )
    return None


"""
    SSE 设备数据流
    前端连接: new EventSource('/api/iot/device/HVAC_SIM_001/stream')
"""


# src/api/iot/sse_api.py
@api_bp.route('/iot/device/<string:device_code>/stream')
def device_sse_stream(device_code: str):
    """
    SSE 设备数据流
    前端连接: new EventSource('/api/iot/device/HVAC_SIM_001/stream')
    """
    print(f"[SSE] 设备 {device_code} 开始监听")

    # 记录当前队列状态
    q = get_device_queue(device_code)
    print(f"[SSE] 设备 {device_code} 当前队列大小: {q.qsize()}")

    def generate():
        data_count = 0  # 计数器

        # 发送连接成功消息
        yield f"data: {json.dumps({'type': 'connected', 'device_code': device_code, 'timestamp': datetime.now().isoformat()})}\n\n"

        while True:
            try:
                data = q.get(timeout=30)
                data_count += 1

                # 📌 收到数据时打印
                print(f"[SSE] 设备 {device_code} 收到数据 #{data_count}, 类型: {data.get('type', 'unknown')}")

                yield f"data: {json.dumps(data)}\n\n"

            except queue.Empty:
                # 心跳
                yield ": heartbeat\n\n"

    response = Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'text/event-stream; charset=utf-8',
            'Connection': 'keep-alive'
        }
    )
    return response
# @api_bp.route('/iot/device/<string:device_code>/stream')
# def device_sse_stream(device_code: str):
#     """
#     SSE 设备数据流
#     前端连接: new EventSource('/api/iot/device/HVAC_SIM_001/stream')
#     """
#     print(f"[SSE] 设备 {device_code} 开始监听")
#
#     def generate():
#         q = get_device_queue(device_code)
#         # 发送连接成功消息
#         yield f"data: {json.dumps({'type': 'connected', 'device_code': device_code, 'timestamp': datetime.now().isoformat()})}\n\n"
#
#         while True:
#             try:
#                 data = q.get(timeout=30)
#                 yield f"data: {json.dumps(data)}\n\n"
#             except queue.Empty:
#                 yield ": heartbeat\n\n"
#
#     response = Response(
#         stream_with_context(generate()),
#         mimetype='text/event-stream',
#         headers={
#             'Cache-Control': 'no-cache',
#             'X-Accel-Buffering': 'no',
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Methods': 'GET',
#             'Access-Control-Allow-Headers': 'Content-Type',
#             'Content-Type': 'text/event-stream; charset=utf-8',
#             'Connection': 'keep-alive'
#         }
#     )
#     return response


# 添加 OPTIONS 预检请求处理
@api_bp.route('/iot/device/<string:device_code>/stream', methods=['OPTIONS'])
def device_sse_options(device_code):
    """处理 CORS 预检请求"""
    response = Response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

"""获取设备最新数据（轮询备用）"""
@api_bp.route('/iot/device/<string:device_code>/latest')
def get_device_latest_data(device_code: str):
    """获取设备最新数据（轮询备用）"""
    from src.common.models.response import Result
    return Result.success(data=get_latest_data(device_code))

"""测试 SSE 推送接口"""
@api_bp.route('/iot/device/<string:device_code>/test-sse-push', methods=['POST'])
@jwt_required
def test_sse_push(device_code: str):
    """测试 SSE 推送接口（production disabled; non-production requires feature flag)"""
    from src.common.models.response import Result

    blocked = _sse_test_endpoint_allowed()
    if blocked is not None:
        return blocked

    test_data = {
        'type': 'test',
        'device_code': device_code,
        'timestamp': datetime.now().isoformat(),
        'data': {'temperature': 25.5, 'power': 100, 'message': '测试数据'}
    }
    push_to_device(device_code, test_data)
    return Result.success(message=f"已推送测试数据到设备 {device_code}")