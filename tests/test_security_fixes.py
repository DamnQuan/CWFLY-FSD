# -*- coding: utf-8 -*-
"""2026-11-07 安全审计修复的离线单测（不联网、不写库、不连生产）。"""
import asyncio
import os
import sys
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsd import certificate  # noqa: E402  # noqa: E402
from fsd import protocol  # noqa: E402  # noqa: E402
from fsd.certificate import Certificate, CertificateStore, _sanitize_cert_row, hash_password  # noqa: E402
from fsd.ratelimit import ConnectionLimiter, TokenBucket  # noqa: E402
from fsd import client_handler  # noqa: E402  # noqa: E402
from fsd.client_handler import Client, ClientHandler  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + (("  " + str(extra)) if extra else ""))


def main():
    # 1) pass-the-hash 修复
    pw = "secret-password"
    cert = Certificate("1234", hash_password(pw), 1, 1, "local")
    check("明文口令可通过", cert.verify_password(pw) is True)
    check("哈希不能当口令（pass-the-hash 已修）", cert.verify_password(hash_password(pw)) is False)
    check("空口令被拒绝", cert.verify_password("") is False)

    # 2) 证书行清洗
    check("文件证书 level=12 被丢弃", _sanitize_cert_row("000000", 12, hash_password("x"), source="file") is None)
    row = _sanitize_cert_row("0000", 12, hash_password("x"), source="db")
    check("DB 0000 强制降为 OBSPILOT", row is not None and row["level"] == 1, row and row["level"])
    check("空哈希证书被丢弃", _sanitize_cert_row("1111", 1, "", source="db") is None)
    check("sha256('') 证书被丢弃", _sanitize_cert_row("1111", 1, hash_password(""), source="db") is None)
    row = _sanitize_cert_row("2222", -1, hash_password("x"), source="db")
    check("停用标记被识别", row is not None and row.get("suspended") and row["level"] == 0)

    # 3) 出站字段清洗（协议注入）
    check("sanitize_field 去 CR/LF/冒号",
          protocol.sanitize_field("A\r\nB:C\tD", 32) == "ABCD", repr(protocol.sanitize_field("A\r\nB:C\tD", 32)))
    check("sanitize_field 截断", len(protocol.sanitize_field("x" * 999, 16)) == 16)
    check("sanitize_realname 去换行", "\n" not in protocol.sanitize_realname("X\n#APPWNED:1:0000:12:9:0:FAKE"))
    check("非法呼号被拒", protocol.is_valid_callsign("A B") is False and protocol.is_valid_callsign("<b>X") is False)
    check("合法呼号通过", protocol.is_valid_callsign("CES1234") is True)

    # 4) 限流原语
    tb = TokenBucket(3, 1.0, now=0.0)
    check("令牌桶初始容量", abs(tb.tokens(now=0.0) - 3.0) < 1e-6)
    check("令牌桶可消耗 3 次", all(tb.take(now=0.0) for _ in range(3)))
    check("令牌桶第 4 次拒绝", tb.take(now=0.0) is False)
    check("令牌桶按秒回填", tb.take(now=1.5) is True)

    lim = ConnectionLimiter(2, 1)
    ok1, _ = lim.admit("1.1.1.1")
    ok2, r2 = lim.admit("1.1.1.1")
    ok3, r3 = lim.admit("2.2.2.2")
    ok5, r5 = lim.admit("3.3.3.3")
    check("每 IP 并发上限生效", ok1 and not ok2 and r2 == "per_ip_limit", r2)
    check("全局连接上限生效", ok3 is True and ok5 is False and r5 == "server_full", r5)
    lim.release("1.1.1.1")
    ok4, _ = lim.admit("1.1.1.1")
    check("释放后可重新接入", ok4 is True)

    # 5) ATIS：机组不能伪造
    class FakeServer:
        def __init__(self):
            self.clients = {}
        def get_client(self, cs):
            return self.clients.get(cs)

    srv = FakeServer()
    h = ClientHandler.__new__(ClientHandler)
    h.server = srv
    h.client = Client("1234", "CES1234", client_handler.CLIENT_PILOT, 1, "Tester", "9")
    h.callsign = "CES1234"
    h.cid = "1234"
    h.client_type = client_handler.CLIENT_PILOT
    h._closed = False
    h.writer = None
    h._atis_parts = []

    async def run():
        await h._handle_cr(["CES1234", "SERVER", "ATIS", "T", "PILOT-SPOOFED ATIS"])
    asyncio.run(run())
    check("机组 ATIS 被拒绝", not getattr(h.client, "atis", ""), repr(getattr(h.client, "atis", "")))

    print()
    print("通过 %d 项，失败 %d 项" % (len(PASS), len(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
