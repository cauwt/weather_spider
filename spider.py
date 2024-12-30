from typing import List, Dict
import json
import re
import logging
from weather_crawler import crawler
import requests

def parse_city_data() -> List[Dict[str, str]]:
    """
    从网址获取并解析城市数据，提取城市代码和名称
    
    Returns:
        包含城市信息的字典列表，每个字典包含city_code和city_name
    """
    try:
        # 获取网页内容
        url = 'https://j.i8tq.com/weather2020/search/city.js'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        # 提取JSON数据
        json_data = re.sub(r'^var\s+city_data\s+=\s+', '', response.text)
        json_data = json_data.strip(';')
        
        # 解析JSON数据
        data = json.loads(json_data)
        
        # 存储解析后的城市数据
        city_data = []
        
        def extract_city_info(d: dict, province: str = None, region: str = None) -> None:
            """递归提取城市信息，包含省份、地区、城市三级结构"""
            for key, value in d.items():
                if isinstance(value, dict):
                    if 'AREAID' in value and 'NAMECN' in value:
                        # 当前是城市级别
                        city_data.append({
                            'province': province,
                            'region': region,
                            'city_name': value['NAMECN'],
                            'city_code': value['AREAID']
                        })
                    elif province is None:
                        # 当前是省份级别
                        extract_city_info(value, province=key)
                    else:
                        # 当前是地区级别
                        extract_city_info(value, province=province, region=key)
        
        # 开始递归提取
        extract_city_info(data)
        return city_data
        
    except Exception as e:
        logging.error(f"获取或解析城市数据失败: {str(e)}", exc_info=True)
        raise

def main(province: str = None):
    """
    主函数
    
    Args:
        province: 省份名称，如果不指定则爬取所有省份数据
    """
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 获取并解析城市数据
        city_data = parse_city_data()
        
        # 如果指定了省份，则只处理该省份的数据
        if province:
            city_data = [city for city in city_data if city['province'] == province]
            if not city_data:
                logging.warning(f"未找到省份 {province} 的数据")
                return
            
        # 遍历城市数据并调用爬虫
        for city in city_data:
            try:
                logging.info(f"开始爬取城市 {city['city_name']} 的数据")
                crawler(
                    city_code=city['city_code'],
                    city_name=city['city_name'],
                    province=city['province'],
                    region=city['region']
                )
            except Exception as e:
                logging.error(f"爬取城市 {city['city_name']} 数据失败: {str(e)}")
                continue
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")

if __name__ == '__main__':
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='天气数据爬虫')
    parser.add_argument('--province', type=str, help='省份名称，不指定则爬取所有省份数据')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用主函数
    main(province=args.province) 