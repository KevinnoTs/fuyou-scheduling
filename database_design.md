# 医院排班系统 - 数据库设计

## 1. doctors (医生表)
```sql
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(2) NOT NULL,          -- 性别: 男/女
    specialty VARCHAR(20) NOT NULL,      -- 擅长方向: 妇科/产科/儿科/筛查
    annual_leave_days INTEGER DEFAULT 0,  -- 每年年假天数
    used_leave_days INTEGER DEFAULT 0,   -- 本年已休息天数
    avatar VARCHAR(255),                 -- 头像文件路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 2. specialties (擅长方向表)
```sql
CREATE TABLE specialties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#007bff', -- 显示颜色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 科室详细配置
1. **妇科**
   - 开放时间: 早8点-下午5点半 (08:00-17:30)

2. **产科**
   - 开放时间: 早8点-下午5点半 (08:00-17:30)

3. **儿科**
   - 每年5月至10月: 早8点-中午12点, 下午2点半-下午5点半 (08:00-12:00, 14:30-17:30)
   - 每年10月至次年5月: 早8点-中午12点, 下午2点-下午5点 (08:00-12:00, 14:00-17:00)

4. **筛查**
   - 每年5月至10月: 早8点-中午12点, 下午2点半-下午5点半 (08:00-12:00, 14:30-17:30)
   - 每年10月至次年5月: 早8点-中午12点, 下午2点-下午5点 (08:00-12:00, 14:00-17:00)

## 3. shift_types (班次类型表)
```sql
CREATE TABLE shift_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_hours DECIMAL(4,2) NOT NULL,
    work_score DECIMAL(4,1) NOT NULL,  -- 工作量分值
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 班次详细配置

1. **白班**
   - 时间段: 早8点-中午12点 + 下午时间段
   - 每年5月至10月: 08:00-12:00, 14:30-17:30 (总时长7.5小时)
   - 每年10月至次年5月: 08:00-12:00, 14:00-17:00 (总时长7小时)

2. **中班**
   - 时间段: 早8点-中午11点半 + 下午时间段
   - 每年5月至10月: 08:00-11:30, 12:00-14:30 (总时长6小时)
   - 每年10月至次年5月: 08:00-11:30, 12:00-14:00 (总时长5.5小时)

3. **值班**
   - 时间段: 早8点-中午12点 + 下午时间段 + 夜间
   - 每年5月至10月: 08:00-12:00, 14:30-23:59 (总时长13.5小时)
   - 每年10月至次年5月: 08:00-12:00, 14:00-23:00 (总时长13小时)

4. **下夜**
   - 时间段: 当天0点-早晨8点 (总时长8小时)

5. **休息**
   - 状态: 放假休息

6. **探亲假**
   - 状态: 放假休息

7. **公休**
   - 状态: 年假休息 (对应医生表中的年假天数)