# tools — 运维 / 诊断脚本

这些脚本**不是**服务运行必需，按需手动执行；默认从仓库根目录运行（依赖当前目录的 `fsd.conf` / `fsd-db.conf`）。

| 脚本 | 用途 |
|---|---|
| `check_bcrypt.py` | 检查某账号的 bcrypt 口令哈希 |
| `check_cid5966.py` | 查询指定 CID |
| `debug_hash.py` | 根据环境变量打印 FSD 口令哈希（仅本地调试） |
| `debug_ping.py` | 手工发送 `$PI` 探活 |
| `list_users.py` | 列出用户 |
| `set_fsd_pwd.py` | 设置 FSD 口令哈希（危险，谨慎） |
| `test_*` | 端口/认证/欢迎消息等连通性测试 |
| `update_admin_fsd_hash.py` | 按环境变量更新管理员/机器人 FSD 哈希 |

> 这些脚本直接连数据库，请勿在生产机随意执行；`set_fsd_pwd.py` / `update_admin_fsd_hash.py` 会修改账号凭据。
