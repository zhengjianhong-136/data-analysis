# sql基础
# sql进阶
# sql 实例
## 行转列
```sql
# 原表结构: 姓名,课程,分数
select 姓名,
 max(case 课程 when '语文' then 分数 else 0 end)语文,
 max(case 课程 when '数学'then 分数 else 0 end)数学,
 max(case 课程 when '物理'then 分数 else 0 end)物理
from table
group by 姓名
```

## 列转行
```sql
# 原表结构: product_id, jan_sales, feb_sales, mar_sales
# 方法1：使用LATERAL VIEW和EXPLODE
SELECT product_id, 
       month,
       sales_value
FROM products
LATERAL VIEW EXPLODE(
  ARRAY(
    STRUCT('Jan', jan_sales),
    STRUCT('Feb', feb_sales),
    STRUCT('Mar', mar_sales)
  )
) sales_table AS month, sales_value;

# 方法2：使用UNION ALL
SELECT product_id, 'Jan' as month, jan_sales as sales
FROM products
UNION ALL
SELECT product_id, 'Feb' as month, feb_sales as sales
FROM products
UNION ALL
SELECT product_id, 'Mar' as month, mar_sales as sales
FROM products;
```

## 连续登录问题
```sql
# 例如求连续登录3天的用户
select userid,dis
 min(visit_date),
 max(visit_date),
 count(1)
 from   
 (
    #计算登录日期和访问顺序的差值，如果相同就是连续登录
    select userid,visit_date,date_sub(visit_date,rn) dis
    from
    (
        #给每个用户按照时间先后顺序排序，记录第几次访问
        select userid, visit_date ,
        row_number() over(partition by userid order by visit_date) rn
        from t1
    ) t2
) t3
group by userid,dis
having  count(1) > 2
```
## 生成连续日期
```sql
SELECT  get_dt_date(date_sub(get_date('${dt}'), pos)) as dt
FROM dual
lateral view posexplode(split(space(datediff(get_date('${dt}'),'2022-01-01')), ' ')) tmp as pos,val
```

## 求解中位数
```sql
#方法1：
SELECT AVG(value) as median
FROM (
  SELECT value
  FROM (
    SELECT value,
    ROW_NUMBER() OVER (ORDER BY value) as rn,
    COUNT(*) OVER () as total
    FROM your_table
  ) T
  WHERE rn IN (FLOOR((total + 1)/2), CEIL((total + 1)/2))

#方法2：
SELECT PERCENTILE(value, 0.5) as median
FROM your_table;
```
