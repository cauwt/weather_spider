import requests
import re
import json
from datetime import datetime
import pandas as pd
import logging

def fetch_weather_data(url: str) -> dict:
    """获取天气数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        # 使用正则表达式提取observe24h_data变量的值
        pattern = r'var observe24h_data = (.*?);'
        match = re.search(pattern, response.text)
        
        if not match:
            raise ValueError("未找到天气数据")
            
        weather_data = json.loads(match.group(1))
        return weather_data
    
    except Exception as e:
        logging.error(f"获取天气数据失败: {str(e)}", exc_info=True)
        raise

def process_weather_data(weather_data: dict) -> pd.DataFrame:
    """处理天气数据"""
    try:
        # 解析时间和城市名
        date_hour = datetime.strptime(weather_data['od']['od0'], '%Y%m%d%H%M%S')
        city_name = weather_data['od']['od1']
        
        # 处理小时数据
        records = []
        # 由于od2是数组，需要遍历处理
        for hour_data in weather_data['od']['od2']:
            record = {
                'city_name': city_name,
                'date_hour': date_hour,
                'hour': hour_data['od21'],        # 小时
                'temperature': hour_data['od22'],  # 温度
                'wind_direction': hour_data['od24'],  # 风向
                'wind_force': hour_data['od25'],     # 风力
                'precipitation': hour_data['od26'],   # 降水量
                'humidity': hour_data['od27']         # 相对湿度
            }
            records.append(record)
        # 处理小时数据的时间转换
        found_23 = False
        for record in records:
            hour = int(record['hour'])
            if hour == 23:
                found_23 = True
            
            if not found_23:
                # 23点之前的数据加1天
                record['hour'] = date_hour.replace(hour=hour) + pd.Timedelta(days=1)
            else:
                # 23点及之后的数据使用当天
                record['hour'] = date_hour.replace(hour=hour)
        return pd.DataFrame(records)
    
    except Exception as e:
        logging.error(f"处理天气数据失败: {str(e)}", exc_info=True)
        raise

def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """保存数据到CSV文件"""
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"数据已保存到 {filename}")
    except Exception as e:
        logging.error(f"保存CSV文件失败: {str(e)}", exc_info=True)
        raise

def crawler(city_code: str = '101230201'):
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 目标URL
    url = f'https://www.weather.com.cn/weather1d/{city_code}.shtml'
    
    try:
        # 获取数据
        weather_data = fetch_weather_data(url)
        
        # 处理数据
        df = process_weather_data(weather_data)
        
        # 保存数据
        save_to_csv(df, 'output/weather_data.csv')
        
    except Exception as e:
        logging.error(f"程序执行失败: {str(e)}")
        return

if __name__ == '__main__':
    crawler()