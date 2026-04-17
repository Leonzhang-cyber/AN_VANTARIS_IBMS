# src/blockchain/mining_scheduler.py
import threading
import time
from typing import List, Optional
from web3 import Web3

class MiningScheduler:
    """
    全局挖矿调度器（单例）
    负责管理所有节点的挖矿启停，支持空闲自动停止。
    """
    _instance: Optional['MiningScheduler'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, node_urls: List[str], idle_timeout: int = 600):
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.node_urls = node_urls
        self.idle_timeout = idle_timeout  # 秒，默认10分钟

        self._mining = False              # 当前是否处于挖矿状态
        self._last_activity = time.time()
        self._timer: Optional[threading.Timer] = None
        self._state_lock = threading.RLock()

        # 启动后台监控线程
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _start_mining_all(self):
        """实际启动所有节点挖矿"""
        print("⛏️ [Scheduler] 正在启动所有节点挖矿...")
        for url in self.node_urls:
            try:
                # 注意：这里需要 Web3 实例，但调度器没有持有全局 client，因此通过外部注入临时实例
                # 这里采用延迟绑定：由调用方通过 start() 时传入一个 Web3 工厂函数
                # 为简化，我们将启动逻辑委托给一个外部回调
                pass
            except Exception as e:
                print(f"⚠️ 节点 {url} 启动失败: {e}")

    def _stop_mining_all(self):
        """实际停止所有节点挖矿"""
        print("🛑 [Scheduler] 正在停止所有节点挖矿...")
        for url in self.node_urls:
            try:
                w3_temp = Web3(Web3.HTTPProvider(url))
                w3_temp.provider.make_request('miner_stop', [])
            except Exception as e:
                print(f"⚠️ 节点 {url} 停止失败: {e}")

    def _reset_timer(self):
        """重置空闲定时器"""
        with self._state_lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self.idle_timeout, self._idle_timeout_callback)
            self._timer.start()

    def _idle_timeout_callback(self):
        """定时器回调：空闲超时则停止挖矿"""
        with self._state_lock:
            if time.time() - self._last_activity >= self.idle_timeout:
                self._stop_mining_all()
                self._mining = False
                print("🛑 [Scheduler] 空闲超时，所有节点挖矿已停止")

    def _monitor_loop(self):
        """后台监控线程，定期检查状态（备用）"""
        while True:
            time.sleep(30)
            with self._state_lock:
                if self._mining and (time.time() - self._last_activity >= self.idle_timeout):
                    self._stop_mining_all()
                    self._mining = False
                    print("🛑 [Scheduler] 空闲超时，所有节点挖矿已停止（监控触发）")

    def start(self, start_func):
        """
        请求开始挖矿。若未在挖矿，则调用 start_func 启动；无论如何都重置空闲计时。
        :param start_func: 无参函数，用于实际启动挖矿（由调用方提供，避免循环依赖）
        """
        with self._state_lock:
            if not self._mining:
                start_func()
                self._mining = True
                print("⛏️ [Scheduler] 挖矿已启动")
            self._last_activity = time.time()
            self._reset_timer()

    def stop(self):
        """立即停止挖矿（供外部手动调用）"""
        with self._state_lock:
            if self._mining:
                self._stop_mining_all()
                self._mining = False
                if self._timer:
                    self._timer.cancel()
                    self._timer = None

    def is_mining(self) -> bool:
        with self._state_lock:
            return self._mining