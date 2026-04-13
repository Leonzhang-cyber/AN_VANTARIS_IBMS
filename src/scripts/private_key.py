# sign.py
import sys
from cryptography.hazmat.primitives.asymmetric import ed25519


def main():
    print("=== Ed25519 签名工具 ===")

    # 输入私钥（十六进制）
    private_key_hex = input("请输入私钥（十六进制）: ").strip()
    if not private_key_hex:
        print("错误：私钥不能为空")
        sys.exit(1)

    # 输入 challenge
    challenge = input("请输入 challenge 字符串: ").strip()
    if not challenge:
        print("错误：challenge 不能为空")
        sys.exit(1)

    try:
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
        signature = private_key.sign(challenge.encode())
        print("\n生成的签名（十六进制）:")
        print(signature.hex())
    except Exception as e:
        print(f"签名失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()