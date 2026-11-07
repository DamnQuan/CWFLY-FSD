# 部署说明（重构后）

## 目录约定

```
CWFLY-FSD/
├── main.py            # 唯一入口：python main.py [fsd.conf]
├── fsd/               # 核心包（服务端代码，全部模块）
├── config/            # fsd.conf.example / fsd-db.conf.example
├── tools/             # 运维诊断脚本（非运行必需）
├── tests/             # 离线单测/回归脚本
├── docs/              # 协议与部署文档
└── requirements.txt
```

运行时数据文件**不在仓库内**，仍放在工作目录（默认 `/opt/cwfly/fsd-py`）：

- `fsd.conf`、`fsd-db.conf`（600）
- `cert.txt`（600，启动时由 `save_public()` 只写低等级文件证书）
- `.fsd-admin-000000`（600，随机管理员口令）
- `whazzup.txt`、`fsd.log`

## 部署步骤

```bash
# 1) 本地打包（仓库根目录）
tar -czf fsd.tgz main.py fsd config requirements.txt

# 2) 上传到服务器并备份旧目录
cd /opt/cwfly/fsd-py
TS=$(date +%Y%m%d-%H%M%S)
tar -czf /tmp/fsd-py-backup-$TS.tgz --exclude='.venv' --exclude='__pycache__' .
tar -xzf /tmp/fsd.tgz -C /opt/cwfly/fsd-py

# 3) 语法检查 + 重启
python3 -m compileall -q fsd main.py
pm2 restart cwfly-fsd

# 4) 验证
pm2 logs cwfly-fsd --lines 50
ss -lntp | grep 6809
```

> 注意：旧版本是根目录平铺的 `.py`；升级到新结构后，**不要再把旧平铺文件复制回来**，否则会覆盖 `fsd/` 包外的同名模块导致导入混乱。清理旧文件前先确认 `fsd/`、`main.py` 已就位。
