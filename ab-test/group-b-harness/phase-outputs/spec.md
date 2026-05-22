# 内存缓存库需求规格说明书

## 功能需求
1. set(key, value, ttl=None): 设置键值对，可选TTL秒数
2. get(key): 获取值，过期返回None
3. delete(key): 删除键，不存在时静默
4. size(): 返回当前缓存条目数
5. clear(): 清空所有缓存

## 非功能需求
- LRU淘汰：max_size控制，超容量淘汰最久未访问条目
- 线程安全：使用threading.Lock保护所有操作
- 惰性TTL清理：get时检查过期并清理
- 使用time.monotonic()防时钟跳变

## 验收标准
AC-1: set后get返回正确值 [判定: boolean]
AC-2: TTL过期后get返回None [判定: boolean]
AC-3: 同key重新set更新TTL值 [判定: boolean]
AC-4: max_size=3时插入第4个key淘汰最旧项 [判定: state_check]
AC-5: get(key)后key不视为最旧 [判定: state_check]
AC-6: delete后get返回None [判定: boolean]
AC-7: clear后size=0 [判定: numeric]
AC-8: 100并发线程不崩溃 [判定: boolean]
AC-9: get中先检查过期再移动LRU位置 [判定: state_check]
AC-10: set已存在key时不淘汰自身 [判定: state_check]