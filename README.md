<div align="center">
    <img src=https://raw.githubusercontent.com/senjianlu/common/master/Logo.png width=40%/>
</div>

[中文文档](https://github.com/senjianlu/common/blob/master/README_zh.md)

# common
A common package developed for Python3 web scraping.  
Configuration file style refers to `config.template.toml`.

### Import
Recommended project structure:
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
Add `common` as a submodule to the `app/` directory:
```bash
git submodule add https://github.com/senjianlu/common.git app/common
```

### Usage
Here is an example of starting the AdsPower browser and setting up a proxy:
```python
from common import chrome
from common import proxy
from common import adspower

# 1. Get the proxy
proxy_str = proxy.get_proxy_str("HK", True)
# 2. Initialize Chrome
# 2.1 Check if the AdsPower browser is already running
if adspower.is_browser_active(serial_number=1):
    print("AdsPower browser is running, shutting down...")
    adspower.stop_browser(serial_number=1)
    print("AdsPower browser shut down successfully!")
else:
    print("AdsPower browser is not running, no need to shut down.")
# 2.2 Start the AdsPower browser
debug_address, debug_port = chrome.start_adspower_browser(serial_number=1, proxy_str=proxy_str, is_open_tabs=True, launch_args=["--disable-popup-blocking"])
# 2.3 Connect to the browser
driver = chrome.connect_debug_chrome(debug_address, debug_port, chrome_version=122)
# 3. Visit a website
driver.get("https://www.google.com")
# 4. Close the browser
chrome.close_browser(driver)
```

### Dependencies
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
# common.mongodb
pymongo==3.12.0
# common.seafile
beautifulsoup4==4.10.0
```

### Synchronization

| Module           | Synced | Sync Date  |
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
| common.character | ✅ | 2024/07/27 |
| common.mongodb   | ✅ | 2024/08/11 |
| common.seafile   | ✅ | 2024/09/29 |

### Other
Logo author: [さわらつき](https://x.com/sawaratsuki1004)