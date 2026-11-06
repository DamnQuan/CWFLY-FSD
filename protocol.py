"""FSD Protocol constants - matches fsd-master/fsd/protocol.h"""

import os
import re

# Server-to-server commands
CMD_NOTIFY = 0
CMD_REQMETAR = 1
CMD_PING = 2
CMD_PONG = 3
CMD_SYNC = 4
CMD_LINKDOWN = 5
CMD_NOWX = 6
CMD_ADDCLIENT = 7
CMD_RMCLIENT = 8
CMD_PLAN = 9
CMD_PD = 10   # Pilot data
CMD_AD = 11   # ATC data
CMD_CERT = 12
CMD_MULTIC = 13
CMD_WEATHER = 14
CMD_METAR = 15
CMD_ADDWPROF = 16
CMD_DELWPROF = 17
CMD_KILL = 18
CMD_RESET = 19

CMD_NAMES = [
    "NOTIFY", "REQMETAR", "PING", "PONG", "SYNC", "LINKDOWN",
    "NOWX", "ADDCLIENT", "RMCLIENT", "PLAN", "PD", "AD", "ADDCERT",
    "MC", "WX", "METAR", "AWPROF", "DWPROF", "KILL", "RESET"
]

# Client commands
CL_ADDATC = 0
CL_RMATC = 1
CL_ADDPILOT = 2
CL_RMPILOT = 3
CL_REQHANDOFF = 4
CL_MESSAGE = 5
CL_REQWEATHER = 6
CL_PILOTPOS = 7
CL_ATCPOS = 8
CL_PING = 9
CL_PONG = 10
CL_ACHANDOFF = 11
CL_PLAN = 12
CL_SB = 13
CL_PC = 14
CL_WEATHER = 15
CL_CLOUDDATA = 16
CL_WINDDATA = 17
CL_TEMPDATA = 18
CL_REQCOM = 19
CL_REPCOM = 20
CL_REQACARS = 21
CL_REPACARS = 22
CL_ERROR = 23
CL_CQ = 24
CL_CR = 25
CL_KILL = 26
CL_WDELTA = 27
CL_SECUREAUTH = 28

CL_CMD_NAMES = [
    "#AA", "#DA", "#AP", "#DP", "$HO", "#TM", "#RW", "@", "%",
    "$PI", "$PO", "$HA", "$FP", "#SB", "#PC", "#WX", "#CD", "#WD",
    "#TD", "$C?", "$CI", "$AX", "$AR", "$ER", "$CQ", "$CR", "$!!",
    "#DL", "$SA"
]

# Certificate operations
CERT_ADD = 0
CERT_DELETE = 1
CERT_MODIFY = 2

# Error codes
ERR_OK = 0
ERR_CSINUSE = 1
ERR_CSINVALID = 2
ERR_REGISTERED = 3
ERR_SYNTAX = 4
ERR_SRCINVALID = 5
ERR_CIDINVALID = 6
ERR_NOSUCHCS = 7
ERR_NOFP = 8
ERR_NOWEATHER = 9
ERR_REVISION = 10
ERR_LEVEL = 11
ERR_SERVFULL = 12
ERR_CSSUSPEND = 13

ERR_STR = [
    "No error", "Callsign in use", "Invalid callsign",
    "Already registered", "Syntax error", "Invalid source callsign",
    "Invalid CID/password", "No such callsign", "No flightplan",
    "No such weather profile", "Invalid protocol revision",
    "Requested level too high", "Too many clients connected",
    "CID/PID was suspended"
]

# Client types
CLIENT_PILOT = 1
CLIENT_ATC = 2
CLIENT_ALL = 3

# Feed strategies
FEED_IN = 1
FEED_OUT = 2
FEED_BOTH = 3

# Kill reasons
KILL_NONE = 0
KILL_COMMAND = 1
KILL_FLOOD = 2
KILL_INITTIMEOUT = 3
KILL_DATATIMEOUT = 4
KILL_CLOSED = 5
KILL_WRITEERR = 6
KILL_KILL = 7
KILL_PROTOCOL = 8

# Rating levels
LEV_SUSPENDED = 0
LEV_OBSPILOT = 1
LEV_STUDENT1 = 2
LEV_STUDENT2 = 3
LEV_STUDENT3 = 4
LEV_CONTROLLER1 = 5
LEV_CONTROLLER2 = 6
LEV_CONTROLLER3 = 7
LEV_INSTRUCTOR1 = 8
LEV_INSTRUCTOR2 = 9
LEV_INSTRUCTOR3 = 10
LEV_SUPERVISOR = 11
LEV_ADMINISTRATOR = 12
LEV_MAX = 12

CERT_LEVEL_NAMES = [
    "SUSPENDED", "OBSPILOT", "STUDENT1", "STUDENT2", "STUDENT3",
    "CONTROLLER1", "CONTROLLER2", "CONTROLLER3", "INSTRUCTOR1",
    "INSTRUCTOR2", "INSTRUCTOR3", "SUPERVISOR", "ADMINISTRATOR"
]

# 设施类型(% 报文 facilitytype 字段)→ 开放该席位所需的最低评级。
# 移植自 SimpleFSD RatingFacilityMap: DEL/GND 需 S1, TWR 需 S2, APP 需 S3,
# CTR 需 C1, FSS 需 C3(SimpleFSD 中 CTR3 及以上才含 FSS)。OBS 人人可用。
FACILITY_MIN_RATING = {
    0: LEV_OBSPILOT,      # Observer
    1: LEV_CONTROLLER3,   # FSS
    2: LEV_STUDENT1,      # Delivery
    3: LEV_STUDENT1,      # Ground
    4: LEV_STUDENT2,      # Tower
    5: LEV_STUDENT3,      # Approach/Departure
    6: LEV_CONTROLLER1,   # Enroute/Center
}

# 广播视程上限(海里): 防止客户端上报离谱 visual_range 导致裁剪失效,
# 也避免超大数值参与距离比较(SimpleFSD 无此限制, 这里加严)
MAX_VISUAL_RANGE = 3000

# Protocol constants
CALLSIGN_BYTES = 12
MAXLOG = 50
# ---- 单行长度上限（安全 2026-11-07 审计 P1-11/P2-25：此前这里定义了却从未使用）----
# 普通报文（所有 #/$/@/%/' 命令）单行字符上限。
MAX_LINE_LENGTH = 512
# 例外：swift 的 Aircraft Configuration 走 $CQ<cs>:<target>:ACC:<json>，全量 JSON
# 合法超过 512 字符（见 ACC_PROTOCOL.md / _ACC_MAX_PAYLOAD）。只对这一种报文放宽，
# 其他任何超长行仍然按 MAX_LINE_LENGTH 丢弃/断开。
MAX_ACC_LINE_LENGTH = 8192
# 超长行容忍次数：超过即断开（单次超长只丢弃，避免误伤偶发的长报文）
MAX_OVERSIZE_LINES = 5
MAX_HOPS = 10
NEED_REVISION = 9
USER_TIMEOUT = 500
SERVER_TIMEOUT = 800
# 读超时：客户端在线时每秒都在上报位置，300s 无任何上行即可判定链路已死。
# 下调(2026-10-16：800→300) 以便更快回收僵尸会话；可用 FSD_CLIENT_TIMEOUT 覆盖。
CLIENT_TIMEOUT = int(os.environ.get("FSD_CLIENT_TIMEOUT", "300"))
SILENT_CLIENT_TIMEOUT = 36000
PING_TIMEOUT = 200
SYNC_TIMEOUT = 120
SERVER_MAX_TOOK = 240

PRODUCT = "FSD Python Server v1.0"
VERSION = "V1.0"

# ============================================================================
# 安全加固常量 / 报文清洗（2026-11-07 审计 P1-9 / P1-10 / P1-11 / P2-25）
# ============================================================================

# ---- 字段长度上限 ----
MAX_CALLSIGN_LENGTH = CALLSIGN_BYTES     # 12
MAX_CID_LENGTH = 16                      # CID 正常 4~6 位，留余量
MAX_REALNAME_LENGTH = 64                 # 审计要求 ≤64
MAX_CHAT_LENGTH = 512                    # #TM 聊天正文
MAX_ATIS_LENGTH = 2048                   # 单条 ATIS 总长（与 _handle_atis_data 一致）
MAX_ATIS_SEGMENT_LENGTH = 512            # 单个 $CR ATIS 分段
MAX_ATIS_SEGMENTS = 40                   # $CR 分段聚合数量上限
MAX_FP_FIELD_LENGTH = 256                # $FP 备注/航路等文本字段

# ---- 连接与超时（可用环境变量覆盖）----
# 认证前超时：连接后 N 秒内未完成 #AA/#AP/$SA 即断开（防慢速连接耗尽 FD/内存）
PREAUTH_TIMEOUT = float(os.environ.get("FSD_PREAUTH_TIMEOUT", "15"))
# 每 IP 并发连接上限（0 = 不限制）
MAX_CLIENTS_PER_IP = int(os.environ.get("FSD_MAX_CLIENTS_PER_IP", "8"))
# 写缓冲高水位（字节）：单客户端待发数据超过该值即判定为慢客户端并断开
WRITE_BUFFER_HIGH_WATER = int(
    os.environ.get("FSD_WRITE_HIGH_WATER", str(256 * 1024)))
# 单次 drain() 最长等待（秒），超时同样按慢客户端处理
WRITE_DRAIN_TIMEOUT = float(os.environ.get("FSD_WRITE_DRAIN_TIMEOUT", "10"))
# 全服「在飞」异步投递任务上限（广播/多播一律走有界调度，防止无限堆积）
MAX_INFLIGHT_TASKS = int(os.environ.get("FSD_MAX_INFLIGHT_TASKS", "2000"))

# ---- 报文速率限制（每客户端令牌桶：突发容量, 每秒补充）----
RATE_LIMITS = {
    # 总行数：兜底闸门，正常客户端每秒最多个位数报文
    "line": (400.0, 100.0),
    # 认证报文：#AA/#AP/$SA（防在线爆破；重连会换 handler，即换新桶）
    "auth": (8.0, 0.5),
    # 位置报文：@ / % / '（EuroScope 雷达可达数 Hz，留足余量）
    "pos": (120.0, 30.0),
    # 飞行计划：$FP / $AM
    "plan": (12.0, 1.0),
    # 广播类：$CR / #TM / #AT / $AX / $!!（防放大）
    "chat": (60.0, 10.0),
    # 查询类：$CQ FP/RN/ATIS 请求
    "query": (60.0, 10.0),
    # ATC 视程点
    "subvis": (20.0, 5.0),
}

# 呼号白名单：首字符字母/数字，其余字母/数字/下划线/点/连字符，长度 2~12。
# 显式禁止 ':'（字段分隔）、'\r\n'（行分隔）、'<>' 等注入字符。
CALLSIGN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{1,11}$")
# CID 白名单（DB/同步/文件三处的证书 CID 校验）
CID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,15}$")

# 控制字符（含 \r \n \t \x00、DEL）
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

# FSD_RAW_LOG 需要打码的口令字段：命令前缀 -> 口令所在字段下标
_SENSITIVE_FIELDS = {
    "#AP": 3,   # callsign:type:cid:password:...
    "#AA": 4,   # callsign::realname:cid:password:...
    "$SA": 3,   # callsign:type:cid:hmac_response:...
}


def sanitize_field(value, max_len: int = MAX_LINE_LENGTH,
                   strip_colon: bool = True, strip_angle: bool = False) -> str:
    """统一把不可信文本清洗成「可安全拼进 FSD 报文」的字段。

    安全(2026-11-07 审计 P1-10)：FSD 报文用 ``\\r\\n`` 分行、用 ``:`` 分字段。
    只要把客户端可控文本（呼号/实名/ATIS/聊天/ACC payload/备注）原样拼进出站
    报文，就能伪造 ``#AP``/``#AA``/``$FP``/``$AX`` 等完整行去污染其他客户端。

    规则：
      - 删除 ``\\r``、``\\n``（永远删除，防整行伪造）
      - 删除控制字符（``\\x00-\\x1f`` 与 ``\\x7f``）
      - ``strip_colon=True`` 时删除 ``:``（防字段注入）；
        仅对「报文最后一个字段」的文本（聊天正文/ATIS/ACC JSON）保留冒号
      - ``strip_angle=True`` 时额外删除 ``<>``（实名等展示字段的 HTML 白名单）
      - 截断到 ``max_len`` 个字符

    :returns: 清洗后的 ``str``（``None``/非字符串一律安全化为空串）
    """
    if value is None:
        return ""
    s = value if isinstance(value, str) else str(value)
    s = s.replace("\r", "").replace("\n", "")
    s = _CONTROL_CHARS.sub("", s)
    if strip_colon:
        s = s.replace(":", "")
    if strip_angle:
        s = s.replace("<", "").replace(">", "")
    if max_len is not None and max_len >= 0 and len(s) > max_len:
        s = s[:max_len]
    return s


def sanitize_realname(value, max_len: int = MAX_REALNAME_LENGTH) -> str:
    """实名清洗：去 CR/LF/``:``/``<>``/控制字符，去掉首尾空白，限长 ≤64。

    保留中文、空格、``-``/``_``/``.`` 等真实姓名常见字符（不用 ASCII 白名单，
    否则 EuroScope 的中文实名会被清空）。
    """
    return sanitize_field(value, max_len, strip_colon=True,
                          strip_angle=True).strip()


def is_valid_callsign(value) -> bool:
    """呼号白名单校验（长度 + 字符集），不查重、不判是否已被占用。"""
    if not isinstance(value, str):
        return False
    return bool(CALLSIGN_PATTERN.match(value))


def is_valid_cid(value) -> bool:
    """CID 白名单校验（证书加载/同步时用）。"""
    if not isinstance(value, str):
        return False
    return bool(CID_PATTERN.match(value))


def _is_acc_line(line: str) -> bool:
    """是否为 swift Aircraft Configuration 报文（唯一允许超过 512 字符的报文）。"""
    return line.startswith("$CQ") and ":ACC:" in line


def line_length_limit(line: str) -> int:
    """返回该报文允许的最大字符长度（ACC 扩展报文放宽到 MAX_ACC_LINE_LENGTH）。"""
    return MAX_ACC_LINE_LENGTH if _is_acc_line(line) else MAX_LINE_LENGTH


def redact_line(line: str) -> str:
    """日志脱敏：把 #AP/#AA/$SA 里的口令/挑战响应替换为 ``***``。

    安全(2026-11-07 审计 P2-25)：``FSD_RAW_LOG=1`` 时此前会把明文口令写进日志。
    """
    if not line:
        return line
    for prefix, index in _SENSITIVE_FIELDS.items():
        if line.startswith(prefix):
            parts = line[len(prefix):].split(":")
            if len(parts) > index and parts[index]:
                parts[index] = "***"
            return prefix + ":".join(parts)
    return line
