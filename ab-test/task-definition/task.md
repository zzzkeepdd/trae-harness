# A/B 对照测试任务

## 任务描述
创建一个内存缓存库（cache.py），支持以下功能：
1. 设置键值对，支持 TTL（秒级过期时间）
2. 获取键值，过期返回 None
3. 删除键
4. 最大容量限制（max_size），超出时按 LRU 策略淘汰最久未使用的条目
5. 获取当前缓存大小
6. 清空缓存

## 约束
- 单文件实现，纯 Python stdlib
- 线程安全（threading.Lock）
- TTL 精度为秒级

## 验收标准
- 设置键值对后能正确读取
- TTL 过期后 get 返回 None
- max_size=3 时，插入第4个不同key，最久未使用的被淘汰
- 被 get 访问过的 key 不算"最久未使用"
- delete 后 get 返回 None
- clear 后 size=0
- 100个并发线程同时读写不崩溃