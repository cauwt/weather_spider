-- 创建 schema
CREATE SCHEMA IF NOT EXISTS crawler;

-- 创建用户
CREATE USER crawler WITH PASSWORD 'crawler_password';

-- 授予权限
GRANT USAGE ON SCHEMA crawler TO crawler;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA crawler TO crawler;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA crawler TO crawler;

-- 切换到 crawler schema
SET search_path TO crawler;

-- 创建天气数据表
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    province_name VARCHAR(50) NOT NULL,
    region_name VARCHAR(50) NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    date_hour TIMESTAMP NOT NULL,
    hour TIMESTAMP NOT NULL,
    temperature NUMERIC(4,1),
    wind_direction VARCHAR(20),
    wind_force VARCHAR(10),
    precipitation NUMERIC(5,1),
    humidity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 创建索引以优化查询性能
    CONSTRAINT idx_weather_location_time UNIQUE (province_name, region_name, city_name, hour)
);

-- 为表授予权限
GRANT ALL PRIVILEGES ON weather_data TO crawler;
GRANT USAGE, SELECT ON SEQUENCE weather_data_id_seq TO crawler;

-- 添加注释
COMMENT ON TABLE weather_data IS '天气数据表';
COMMENT ON COLUMN weather_data.province_name IS '省份名称';
COMMENT ON COLUMN weather_data.region_name IS '地区名称';
COMMENT ON COLUMN weather_data.city_name IS '城市名称';
COMMENT ON COLUMN weather_data.date_hour IS '数据获取时间';
COMMENT ON COLUMN weather_data.hour IS '观测小时时间';
COMMENT ON COLUMN weather_data.temperature IS '温度(摄氏度)';
COMMENT ON COLUMN weather_data.wind_direction IS '风向';
COMMENT ON COLUMN weather_data.wind_force IS '风力';
COMMENT ON COLUMN weather_data.precipitation IS '降水量(毫米)';
COMMENT ON COLUMN weather_data.humidity IS '相对湿度(%)';
COMMENT ON COLUMN weather_data.created_at IS '记录创建时间'; 