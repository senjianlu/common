# common
Python3 开发自用的共通包。  
配置文件样式参照 `config.template.toml`

### 使用
```bash
git submodule add https://github.com/senjianlu/common.git app/common
```

### 依赖说明
```bash
# === common.config ===
toml==0.10.2

# === common.redis ===
redis==5.0.1

# === common.Base ===
SQLAlchemy==2.0.25
psycopg2==2.9.9

# === common.chrome ===
selenium==4.17.2

# === common.rabbitmq ===
pika==1.3.2

# === common.rabbitmq & common.adspower & common.gost & common.bark ===
requests==2.31.0
# requests==2.26.0

# === common.proxy ===
cachetools==5.3.2
```

### 同步

| 模块                 | 同步完成 | 同步时间       |
|--------------------|--|------------|
| common.config      | ✅ | 2024/03/24 |
| common.logger      | ✅ | 2024/03/24 |
| common.redis       | ✅ | 2024/03/24 |
| common.Base        | ✅ | 2024/03/24 |
| common.chrome      | ✅ | 2024/03/25 |
| common.rabbitmq    | ✅ | 2024/03/24 |
| common.adspower    | ✅ | 2024/03/25 |
| common.gost        | ✅ | 2024/03/25 |
| common.proxy       | ✅ | 2024/03/24 |
| common.currency    | ✅ | 2024/03/24 |
| common.anonymous   | ✅ | 2024/03/24 |
| common.bark        | ✅ | 2024/03/25 |

