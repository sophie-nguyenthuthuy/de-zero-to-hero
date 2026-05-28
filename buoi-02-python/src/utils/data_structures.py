"""
Demo: Python data structures và patterns cho Data Engineering
"""
from collections import defaultdict


# ===== List Operations =====
def demo_list_ops():
    # Raw data từ API/DB
    raw_records = [
        {"id": 1, "amount": 1500000, "status": "completed"},
        {"id": 2, "amount": 800000, "status": "pending"},
        {"id": 3, "amount": None, "status": "completed"},
        {"id": 4, "amount": 200000, "status": "failed"},
        {"id": 5, "amount": 3000000, "status": "completed"},
    ]

    # ❌ Cách thông thường (verbose)
    completed_old = []
    for r in raw_records:
        if r["status"] == "completed" and r["amount"] is not None:
            completed_old.append(r["amount"])

    # ✅ List comprehension (Pythonic)
    completed_amounts = [
        r["amount"]
        for r in raw_records
        if r["status"] == "completed" and r["amount"] is not None
    ]

    print(f"Completed amounts: {completed_amounts}")
    print(f"Total: {sum(completed_amounts):,} VND")

    return completed_amounts


# ===== Dict Operations =====
def demo_dict_ops():
    raw_records = [
        {"id": 1, "status": "completed", "amount": 1500000},
        {"id": 2, "status": "pending", "amount": 800000},
        {"id": 3, "status": "completed", "amount": 3000000},
        {"id": 4, "status": "failed", "amount": 200000},
    ]

    # Group by status
    grouped: dict[str, list] = defaultdict(list)
    for record in raw_records:
        grouped[record["status"]].append(record)

    # Dict comprehension — tổng amount theo status
    total_by_status = {
        status: sum(r["amount"] for r in records)
        for status, records in grouped.items()
    }

    print(f"Grouped count: { {k: len(v) for k, v in grouped.items()} }")
    print(f"Total by status: {total_by_status}")


# ===== Set Operations (dedup) =====
def demo_set_ops():
    customer_ids = ["C001", "C002", "C001", "C003", "C002", "C004", "C001"]
    unique_ids = list(set(customer_ids))
    print(f"Unique ids: {unique_ids}")

    # Set operations cho data reconciliation
    source_ids = {"C001", "C002", "C003", "C004", "C005"}
    target_ids = {"C001", "C003", "C005", "C006"}

    missing_in_target = source_ids - target_ids  # Cần insert
    extra_in_target = target_ids - source_ids    # Cần xoá
    common = source_ids & target_ids             # Cần update

    print(f"Missing (cần insert): {missing_in_target}")
    print(f"Extra (cần xoá):      {extra_in_target}")
    print(f"Common (cần update):  {common}")


if __name__ == "__main__":
    print("=== List Operations ===")
    demo_list_ops()
    print("\n=== Dict Operations ===")
    demo_dict_ops()
    print("\n=== Set Operations ===")
    demo_set_ops()
