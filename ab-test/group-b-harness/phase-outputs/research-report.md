调研员A（项目环境）：Python3 stdlib。需 time/threading/collections。
调研员B（行业标准）：标准LRU缓存参考functools.lru_cache设计；TTL参考Redis EXPIRE语义——惰性删除+可选主动清理。
调研员C（技术风险）：(1) TTL精度秒级在边界场景(time.time()浮动)可能差1秒；(2) OrderedDict的LRU在max_size=1时需验证；(3) 锁覆盖TTL过期和LRU淘汰的原子性。