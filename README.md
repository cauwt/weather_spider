# weather_spider 天气爬虫

## 天气爬虫
本项目是天气爬虫，用于爬取天气数据，并保存到本地。
目标网站：https://www.weather.com.cn/

### 爬取步骤：
1. 在首页获取城市名称和城市编码
2. 根据城市编码获取该城市的天气页面地址
3. 解析天气页面，获取天气数据
4. 保存天气数据
### 数据格式

数据以CSV格式保存,包含以下字段:

| 字段名 | 说明 | 示例 |
|--------|------|------|
| city_code | 城市编码 | 101010100 |
| date | 日期 | 2024-01-20 |
| hour | 小时 | 14 |
| temperature | 温度(摄氏度) | 25 |

示例数据:



## 使用方法

```
python spider.py
```


