# sql基础
基础入门教程：https://www.w3school.com.cn/sql/sql_select.asp
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
## 面试笔试题
1.订单表：tmp.order_detail,  有如下字段，user_id（用户ID），pay_time(付款时间，格式2023-01-01 23:00），
	sku（商品名称），cate_nm（商品类别，有women，men，kids，young 四类），sales_cnt（销量）
备注：时间从2019-01-01开始

2.用户回访表：tmp.user_visit_di 有如下字段。user_id   ， dt（yyyymmdd格式）浏览时间
备注：时间从2019-01-01开始

问题：按首单购买品类将新客分为A（首单仅购买women），B(首单仅买women和men），C(其余的非A/B类）三种，
看三类客人在2020年及之后by 月在首单30天之内的回访人数，回访率，复购人数，复购率以及复购的top3品类（用逗号隔开）
新客：按首单落在时间窗内（如2020年1月的新客就是首单在2020.1.1-2020.1.31日之间）

回访率：回访人数/新客数
复购率：复购人数/新客数

数据输出格式：

首单月份，首单品类，新客人数，回访人数，回访率，复购人数，复购率，复购的top3品类

2020-01，A,1000,800,80%,500,50%,women，kids，young

2020-01，B,2000,700,35%,100,5%,men，women，kids

2020-01，C,5000,1000,20%,500,10%,kids，young，men
```
with user_fst_order_info as (	--用户首单信息
	select user_id
		,fst_pay_time
		,fst_pay_month
		,fst_cate_nm
		,size(fst_cate_nm) as fst_cate_num	--品类数
	from
	(
		select user_id
			,pay_time as fst_pay_time
			,date_format(pay_time,'yyyy-MM') as fst_pay_month	--用户首单月份
			,collect_set(cate_nm) as fst_cate_nm	--首购品类,数组形式存放，一个用户一条记录
		from
		(	--订单时间排序
			select user_id,pay_time,cate_nm,row_number() over(partition by user_id order by pay_time) as rn
			from
			(	--订单先去重，保留品类维度
				select user_id,pay_time,cate_nm
				from tmp.order_detail
				group by user_id,pay_time,cate_nm
			) t1
		) t2
		where rn = 1
		group by user_id,pay_time,date_format(pay_time,'yyyy-MM')
	) t3
),
user_fst_order_label as (	--用户首单标签
	select *
		,case
			when fst_cate_num = 1 and array_contains(fst_cate_nm) = 'women' then 'A'
			when fst_cate_num = 2 and array_contains(fst_cate_nm) = 'women' and array_contains(fst_cate_nm) = 'men' then 'B'
			else 'C'
		end as new_user_label
	from user_fst_order_info
),
re_visit as (	--用户回访
	select fst_pay_month
		,new_user_label
		,count(distinct user_id) as new_user_num	--新客人数
		,count(distinct if(is_revisit_30d=1,user_id,null)) as revisit_user_num	--回访人数
	from
	(
		select A1.user_id
			,A1.fst_pay_month
			,A1.new_user_label
			,if(A2.visit_dt is not null,1,0) is_revisit_30d	
		from
		(	--2020年开始的新用户
			select user_id,date_format(fst_pay_time,'yyyy-MM-dd') as fst_pay_dt,fst_pay_month,new_user_label
			from user_fst_order_label
			where fst_pay_month >= '2020-01'
		) A1
		left join
		(	--访问
			select user_id,date_format(dt,'yyyy-MM-dd') as visit_dt
			from tmp.user_visit_di
			where date_format(dt,'yyyy-MM-dd') >= '2020-01-01'
		) A2 ON A2.user_id = A1.user_id and (datediff(visit_dt,fst_pay_dt) between 1 and 30)	--30天内回访，不包含首购那天
	) t
	group by fst_pay_month
		,new_user_label
)，
re_order_detail as (	--用户复购明细
	select A1.user_id
		,A1.fst_pay_month
		,A1.new_user_label
		,A2.cate_nm
		,A2.sales_cnt
		,if(A2.order_dt is not null,1,0) is_reorder_30d	
	from
	(	--2020年开始的新用户
		select user_id,date_format(fst_pay_time,'yyyy-MM-dd') as fst_pay_dt,fst_pay_month,new_user_label
		from user_fst_order_label
		where fst_pay_month >= '2020-01'
	) A1
	left join
	(	--购买
		select user_id,date_format(pay_time,'yyyy-MM-dd') as order_dt,cate_nm,sum(sales_cnt) as sales_cnt
		from tmp.order_detail
		where date_format(pay_time,'yyyy-MM-dd') >= '2020-01-01'
		group by user_id,date_format(pay_time,'yyyy-MM-dd'),cate_nm
	) A2 ON A2.user_id = A1.user_id and (datediff(order_dt,fst_pay_dt) between 1 and 30)	--30天内复购，不包含首购那天,同时减少数据量
),
result as 
(
	select
		A1.fst_pay_month
		,A1.new_user_label
		,A1.new_user_num		--新客人数
		,A1.revisit_user_num	--回访人数
		,A2.reorder_user_num	--复购人数
		,A3.cate_nm_top3		--top3品类
	from 
	(
		select fst_pay_month
			,new_user_label
			,new_user_num		--新客人数
			,revisit_user_num	--回访人数
		from re_visit
	) A1
	left join
	(	--复购人数
		select fst_pay_month
			,new_user_label
			,count(distinct if(is_reorder_30d=1,user_id,null)) as reorder_user_num	--复购人数
		from re_order_detail
		group by fst_pay_month
			,new_user_label
	) A2 ON A2.fst_pay_month = A1.fst_pay_month and A2.new_user_label = A1.new_user_label
	left join
	(	--复购品类
		select fst_pay_month
			,new_user_label
			,concat_ws(',',cate_nm) as cate_nm_top3
		from
		(
			select fst_pay_month
				,new_user_label
				,cate_nm
				,row_number() over(partition by fst_pay_month,new_user_label order by sales_cnt desc) as rn
			from  
			(
				select fst_pay_month
					,new_user_label
					,cate_nm
					,sum(sales_cnt) as sales_cnt
				from re_order_detail
				group by fst_pay_month
					,new_user_label
					,cate_nm
			) t1
		) t2
		where rn <= 3
		group by fst_pay_month
			,new_user_label
	) A3 ON A3.fst_pay_month = A1.fst_pay_month and A3.new_user_label = A1.new_user_label
)

select
	fst_pay_month
	,new_user_label
	,new_user_num		--新客人数
	,revisit_user_num	--回访人数
	,coalesce(revisit_user_num / new_user_num,0) as revisit_rate	--回访率
	,reorder_user_num	--复购人数
	,coalesce(reorder_user_num / new_user_num,0) as reorder_rate	--复购率
	,cate_nm_top3		--复购的top3品类
from result
```
