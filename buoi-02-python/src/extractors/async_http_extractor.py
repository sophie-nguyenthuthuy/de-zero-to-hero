"""
Async HTTP Extractor — Fetch nhiều URL đồng thời
So sánh sync vs async performance
"""
import asyncio
import json
import logging
import time
import urllib.request

logger = logging.getLogger(__name__)

URLS = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
]


# ===== SYNC VERSION =====
def fetch_sync(url: str) -> dict:
    """Fetch URL theo kiểu đồng bộ"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read())
    except Exception as e:
        return {"error": str(e), "url": url}


def run_sync(urls: list[str]) -> list[dict]:
    """Fetch tuần tự — chậm"""
    results = []
    for url in urls:
        result = fetch_sync(url)
        results.append(result)
    return results


# ===== ASYNC VERSION =====
# Vì httpbin có thể chậm, demo bằng asyncio.sleep thay thế
async def fetch_async_simulated(url: str, delay: float = 1.0) -> dict:
    """Simulate async HTTP fetch"""
    await asyncio.sleep(delay)   # Giả lập network I/O
    return {"url": url, "fetched_at": time.time()}


async def run_async(tasks: list) -> list:
    """Chạy tất cả tasks đồng thời"""
    return await asyncio.gather(*tasks)


def demo_sync_vs_async():
    NUM_TASKS = 5
    DELAY = 1.0   # Giây mỗi task

    print(f"\n{'=' * 50}")
    print(f"  SYNC vs ASYNC Demo — {NUM_TASKS} tasks × {DELAY}s each")
    print(f"{'=' * 50}")

    # ===== SYNC =====
    print("\n[SYNC] Chạy tuần tự...")
    start = time.time()

    sync_results = []
    for i in range(NUM_TASKS):
        time.sleep(DELAY)   # Blocking I/O
        sync_results.append({"task": i, "done": True})

    sync_time = time.time() - start
    print(f"  Sync time: {sync_time:.2f}s (expected: ~{NUM_TASKS * DELAY:.0f}s)")

    # ===== ASYNC =====
    print("\n[ASYNC] Chạy đồng thời...")
    start = time.time()

    async def main_async():
        tasks = [fetch_async_simulated(f"url_{i}", DELAY) for i in range(NUM_TASKS)]
        return await run_async(tasks)

    async_results = asyncio.run(main_async())
    async_time = time.time() - start
    print(f"  Async time: {async_time:.2f}s (expected: ~{DELAY:.0f}s)")

    speedup = sync_time / async_time
    print(f"\n  🚀 Speedup: {speedup:.1f}x faster với async!")
    print("\n  ⚠️  Khi nào KHÔNG dùng async:")
    print("      - CPU-bound tasks (dùng multiprocessing thay thế)")
    print("      - Khi code phức tạp hơn không đáng")
    print("  ✅ Khi nào NÊN dùng async:")
    print("      - Nhiều HTTP requests đồng thời")
    print("      - Đọc/ghi nhiều files")
    print("      - DB queries không block nhau")


if __name__ == "__main__":
    demo_sync_vs_async()
