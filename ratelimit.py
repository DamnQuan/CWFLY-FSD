"""共享限流 / 有界调度原语（2026-11-07 审计 P1-9 / P1-11）。

此模块不依赖 asyncio 事件循环以外的东西，也不做任何 I/O，便于离线单测：

- :class:`TokenBucket`        每客户端/每类报文的令牌桶（原先只有 ACC 转发有）
- :class:`ConnectionLimiter`  全局连接数 + 每 IP 并发连接数上限
- :class:`BoundedTaskGroup`   「在飞任务」上限，替代无界的 asyncio.ensure_future
"""

import asyncio
import time

from protocol import MAX_INFLIGHT_TASKS


class TokenBucket:
    """经典令牌桶：容量 ``capacity``，每秒补充 ``refill_per_sec``。

    ``now`` 参数只为可测试性（默认 :func:`time.monotonic`）。
    """

    __slots__ = ("capacity", "refill_per_sec", "_tokens", "_last")

    def __init__(self, capacity: float, refill_per_sec: float, now: float = None):
        self.capacity = max(1.0, float(capacity))
        self.refill_per_sec = max(0.0, float(refill_per_sec))
        self._tokens = self.capacity
        self._last = time.monotonic() if now is None else now

    def _refill(self, now: float) -> None:
        if now > self._last:
            self._tokens = min(
                self.capacity,
                self._tokens + (now - self._last) * self.refill_per_sec)
            self._last = now

    def tokens(self, now: float = None) -> float:
        """当前可用令牌数（不消耗）。"""
        self._refill(time.monotonic() if now is None else now)
        return self._tokens

    def take(self, amount: float = 1.0, now: float = None) -> bool:
        """尝试取走 ``amount`` 个令牌；不足则返回 False 且不消耗。"""
        self._refill(time.monotonic() if now is None else now)
        if self._tokens < amount:
            return False
        self._tokens -= amount
        return True


class ConnectionLimiter:
    """全局连接数 + 每 IP 并发连接数上限。

    安全(2026-11-07 审计 P1-9)：``config.max_clients`` 此前从未被引用，任何人都能
    开任意多连接（未认证也算）耗尽 FD/内存。现在连接在**进入协议处理之前**就被
    准入判断，超限直接回 ``$ER`` + 关闭。

    ``max_clients`` / ``max_per_ip`` 为 0 表示不限制该项。
    """

    def __init__(self, max_clients: int = 500, max_per_ip: int = 8):
        self.max_clients = max(0, int(max_clients or 0))
        self.max_per_ip = max(0, int(max_per_ip or 0))
        self.active = 0
        self._per_ip: dict = {}

    def admit(self, ip: str) -> tuple:
        """尝试准入一条连接，返回 ``(ok, reason)``。

        reason: ``"server_full"`` / ``"per_ip_limit"`` / ``""``
        """
        ip = ip or "unknown"
        if self.max_clients and self.active >= self.max_clients:
            return False, "server_full"
        if self.max_per_ip and self._per_ip.get(ip, 0) >= self.max_per_ip:
            return False, "per_ip_limit"
        self.active += 1
        self._per_ip[ip] = self._per_ip.get(ip, 0) + 1
        return True, ""

    def release(self, ip: str) -> None:
        """归还一条连接（必须在连接结束时调用，含异常路径）。"""
        ip = ip or "unknown"
        if self.active > 0:
            self.active -= 1
        left = self._per_ip.get(ip, 0) - 1
        if left > 0:
            self._per_ip[ip] = left
        else:
            self._per_ip.pop(ip, None)

    def count_for(self, ip: str) -> int:
        return self._per_ip.get(ip or "unknown", 0)

    def snapshot(self) -> dict:
        return {"active": self.active,
                "max_clients": self.max_clients,
                "max_per_ip": self.max_per_ip,
                "ips": len(self._per_ip)}


class BoundedTaskGroup:
    """有界「在飞任务」调度器。

    安全(2026-11-07 审计 P1-11)：广播/多播此前用 ``asyncio.ensure_future`` 无上限
    创建任务，慢客户端或广播风暴会让待发任务无限堆积。这里给在飞任务数设上限，
    超限直接丢弃并计数（顶多是某次广播没发出去，不会拖垮进程）。
    """

    def __init__(self, limit: int = MAX_INFLIGHT_TASKS):
        self.limit = max(1, int(limit or MAX_INFLIGHT_TASKS))
        self._tasks: set = set()
        self.dropped = 0
        self.total = 0

    def spawn(self, coro):
        """提交一个协程；超过上限时丢弃（并关闭协程，避免 never-awaited 告警）。"""
        if len(self._tasks) >= self.limit:
            self.dropped += 1
            try:
                coro.close()
            except Exception:
                pass
            return None
        self.total += 1
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def drain(self, timeout: float = 5.0) -> None:
        """等待所有在飞任务结束（停机/测试用，超时即放弃）。"""
        pending = [t for t in self._tasks if not t.done()]
        if not pending:
            return
        try:
            await asyncio.wait(pending, timeout=timeout)
        except Exception:
            pass

    @property
    def pending(self) -> int:
        return len(self._tasks)
