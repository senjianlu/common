<div align="center">
    <img src=https://raw.githubusercontent.com/senjianlu/common/master/Logo.png width=40%/>
</div>

# common
针对 Python3 爬虫开发的共通包。  
配置文件样式参照 `config.template.toml`

### 导入
推荐的项目结构：
```text
|- my_python_project
    |- app
        |- common
        |- models
        |- main.py
    |- config.toml
    |- README.md
    |- requirements.txt
```
将 `common` 作为子模块导入到 `app/` 目录下：
```bash
git submodule add https://github.com/senjianlu/common.git app/common
```

### 使用
这里以启动 AdsPower 浏览器并设置代理为例：
```python
from common import chrome
from common import proxy
from common import adspower

# 1. 获取代理
proxy_str = proxy.get_proxy_str("HK", True)
# 2. 初始化 Chrome
# 2.1 查看 Ads Power 浏览器是否已启动
if adspower.is_browser_active(serial_number=1):
    print("AdsPower 浏览器已启动，开始关闭...")
    adspower.stop_browser(serial_number=1)
    print("AdsPower 浏览器关闭成功！")
else:
    print("AdsPower 浏览器未启动，无需关闭。")
# 2.2 启动 Ads Power 浏览器
debug_address, debug_port = chrome.start_adspower_browser(serial_number=1, proxy_str=proxy_str, is_open_tabs=True, launch_args=["--disable-popup-blocking"])
# 2.3 连接浏览器
driver = chrome.connect_debug_chrome(debug_address, debug_port, chrome_version=122)
# 3. 访问网站
driver.get("https://www.google.com")
# 4. 关闭浏览器
chrome.close_browser(driver)
```

### 依赖说明
```bash
# common.config
toml==0.10.2
# common.redis
redis==5.0.1
# common.Base
SQLAlchemy==2.0.25
psycopg2==2.9.9
# common.chrome
selenium==4.17.2
# common.rabbitmq
pika==1.3.2
# common.rabbitmq & common.adspower & common.gost & common.bark
requests==2.31.0
# common.proxy
cachetools==5.3.2
# common.influxdb
influxdb-client==1.43.0
```

### 同步

| 模块               | 同步完成 | 同步时间       |
|------------------|--|------------|
| common.config    | ✅ | 2024/03/24 |
| common.logger    | ✅ | 2024/03/24 |
| common.redis     | ✅ | 2024/03/24 |
| common.Base      | ✅ | 2024/03/24 |
| common.chrome    | ✅ | 2024/03/25 |
| common.rabbitmq  | ✅ | 2024/06/11 |
| common.adspower  | ✅ | 2024/03/25 |
| common.gost      | ✅ | 2024/03/25 |
| common.proxy     | ✅ | 2024/03/24 |
| common.currency  | ✅ | 2024/03/24 |
| common.anonymous | ✅ | 2024/03/24 |
| common.bark      | ✅ | 2024/03/25 |
| common.work      | ✅ | 2024/05/15 |
| common.sms       | ✅ | 2024/05/27 |
| common.intranet  | ✅ | 2024/06/11 |
| common.influxdb  | ✅ | 2024/06/14 |

### 其他
Logo 作者: [さわらつき](https://x.com/sawaratsuki1004)