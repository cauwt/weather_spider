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

def crawler(city_code: str = '101230201', city_name: str = '厦门', 
           province: str = '福建', region: str = '厦门'):
    """
    爬取天气数据
    
    Args:
        city_code: 城市代码
        city_name: 城市名称
        province: 省份名称
        region: 地区名称
    """
    try:
        # 获取数据
        url = f'https://www.weather.com.cn/weather1d/{city_code}.shtml'
        weather_data = fetch_weather_data(url)
        
        # 处理数据
        df = process_weather_data(weather_data)
        
        # 保存数据，文件名格式：省份_地区_城市
        output_file = f'output/weather_data_{province}_{region}_{city_name}.csv'
        save_to_csv(df, output_file)
        
    except Exception as e:
        logging.error(f"程序执行失败: {str(e)}")
        return

if __name__ == '__main__':
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='天气数据爬虫')
    parser.add_argument('--city_code', type=str, default='101230201', help='城市代码')
    parser.add_argument('--city_name', type=str, default='厦门', help='城市名称') 
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 使用参数调用爬虫
    crawler(city_code=args.city_code, city_name=args.city_name)