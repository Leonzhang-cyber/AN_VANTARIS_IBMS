# test_udp.py
import socket
import time

# 测试 UDP 发送
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)

# 发送测试数据
test_data = b"test"
sock.sendto(test_data, ('127.0.0.1', 11610))
print("📤 已发送测试数据到 127.0.0.1:11610")

try:
    data, addr = sock.recvfrom(1024)
    print(f"📥 收到响应: {data} from {addr}")
except socket.timeout:
    print("⏰ 超时，没有响应")
finally:
    sock.close()