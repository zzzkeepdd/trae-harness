import time
import threading
import sys
sys.path.insert(0, 'src')

import sys; sys.path.insert(0, 'src'); from cache import Cache

def test_set_get():
    c = Cache(max_size=10)
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.get("nonexist") is None

def test_ttl_expiry():
    c = Cache(max_size=10)
    c.set("a", 1, ttl=1)
    assert c.get("a") == 1
    time.sleep(1.1)
    assert c.get("a") is None

def test_ttl_refresh():
    c = Cache(max_size=10)
    c.set("a", 1, ttl=1)
    time.sleep(0.5)
    c.set("a", 2, ttl=2)
    time.sleep(0.7)
    assert c.get("a") == 2  # 没到新TTL

def test_lru_eviction():
    c = Cache(max_size=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.set("d", 4)
    assert c.get("a") is None  # a 最旧
    assert c.get("b") == 2
    assert c.get("c") == 3
    assert c.get("d") == 4

def test_lru_touch_on_get():
    c = Cache(max_size=2)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")            # touch a
    c.set("c", 3)
    assert c.get("a") == 1  # a 被 touch 过
    assert c.get("b") is None  # b 最旧

def test_delete():
    c = Cache(max_size=10)
    c.set("a", 1)
    c.delete("a")
    assert c.get("a") is None
    c.delete("never_exist")  # 不抛异常

def test_size_and_clear():
    c = Cache(max_size=10)
    c.set("a", 1)
    c.set("b", 2)
    assert c.size() == 2
    c.clear()
    assert c.size() == 0

def test_expired_not_touch_lru():
    """AC-9: 过期key不应该被move_to_end——否则污染LRU"""
    c = Cache(max_size=2)
    c.set("a", 1, ttl=0.1)
    c.set("b", 2)
    time.sleep(0.2)
    r = c.get("a")  # 已过期，应返回None且不更新LRU
    assert r is None
    c.set("c", 3)
    assert c.get("b") == 2  # b不应被淘汰因为a已过期且未touch

def test_set_existing_key_no_eviction():
    """AC-10: set已存在的key时不应淘汰自身"""
    c = Cache(max_size=2)
    c.set("a", 1)
    c.set("b", 2)
    c.set("b", 99)  # 更新b，不应淘汰a或b
    assert c.get("a") == 1
    assert c.get("b") == 99
    assert c.size() == 2

def test_concurrent_safety():
    """AC-8: 100并发线程不崩溃"""
    c = Cache(max_size=500)
    errors = []
    def worker(n):
        try:
            for i in range(50):
                key = f"k{n}-{i % 10}"
                c.set(key, i, ttl=10)
                v = c.get(key)
                if i % 20 == 0:
                    c.delete(key)
        except Exception as e:
            errors.append(str(e))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(errors) == 0, f"并发错误: {errors}"

def test_concurrent_lru_integrity():
    """并发下size不超过max_size"""
    c = Cache(max_size=10)
    def worker(n):
        for i in range(100):
            c.set(f"k{n}-{i}", i)
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.size() <= 10  # 容量约束

if __name__ == "__main__":
    tests = [
        test_set_get, test_ttl_expiry, test_ttl_refresh,
        test_lru_eviction, test_lru_touch_on_get, test_delete,
        test_size_and_clear, test_expired_not_touch_lru,
        test_set_existing_key_no_eviction,
        test_concurrent_safety, test_concurrent_lru_integrity,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} 通过")