import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import yaml
from pathlib import Path

def load_db_config() -> dict:
    """加载数据库配置"""
    try:
        config_path = Path('config/database.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['postgres']
    except Exception as e:
        logging.error(f"加载数据库配置失败: {str(e)}", exc_info=True)
        raise

def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """保存数据到CSV文件"""
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"数据已保存到 {filename}")
    except Exception as e:
        logging.error(f"保存CSV文件失败: {str(e)}", exc_info=True)
        raise

def save_to_database(df: pd.DataFrame, province_name: str, region_name: str) -> None:
    """保存数据到PostgreSQL数据库"""
    try:
        # 加载数据库配置
        db_config = load_db_config()
        
        # 建立数据库连接
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # 设置schema
        cur.execute('SET search_path TO crawler')
        
        # 准备插入语句
        insert_query = """
            INSERT INTO weather_data (
                province_name, region_name, city_name, date_hour, 
                hour, temperature, wind_direction, wind_force, 
                precipitation, humidity
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT ON CONSTRAINT idx_weather_location_time DO UPDATE SET
                temperature = EXCLUDED.temperature,
                wind_direction = EXCLUDED.wind_direction,
                wind_force = EXCLUDED.wind_force,
                precipitation = EXCLUDED.precipitation,
                humidity = EXCLUDED.humidity;
        """
        
        # 准备数据
        records = []
        for _, row in df.iterrows():
            record = (
                province_name,
                region_name,
                row['city_name'],
                row['date_hour'],
                row['hour'],
                row['temperature'],
                row['wind_direction'],
                row['wind_force'],
                row['precipitation'],
                row['humidity']
            )
            records.append(record)
        
        # 批量插入数据
        execute_batch(cur, insert_query, records)
        
        # 提交事务
        conn.commit()
        logging.info(f"成功保存 {len(records)} 条数据到数据库")
        
    except Exception as e:
        logging.error(f"保存数据到数据库失败: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close() 