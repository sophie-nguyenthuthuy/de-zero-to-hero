"""
Error handling patterns cho Data Engineering
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Optional, TypeVar

# Setup logging đúng cách (không dùng print trong production)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Custom exceptions cho DE
class DataValidationError(Exception):
    """Raise khi data không pass validation"""

    def __init__(self, field: str, value, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(
            f"Validation failed — field='{field}', value='{value}': {reason}"
        )


class DataExtractionError(Exception):
    """Raise khi không thể đọc nguồn dữ liệu"""

    pass


class SchemaError(Exception):
    """Raise khi schema không khớp"""

    pass


# Pattern: Result type (tránh raise exception ở mọi nơi)
T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        return cls(success=False, error=error)


def safe_parse_amount(value: str) -> Result[float]:
    """Parse amount với xử lý lỗi an toàn"""
    try:
        cleaned = value.replace(",", "").replace("VND", "").strip()
        amount = float(cleaned)

        if amount < 0:
            return Result.fail(f"Amount âm không hợp lệ: {amount}")

        return Result.ok(amount)
    except ValueError as e:
        return Result.fail(f"Không thể parse '{value}': {e}")


def read_file_safe(filepath: str) -> Result[str]:
    """Đọc file với error handling đầy đủ"""
    path = Path(filepath)

    try:
        if not path.exists():
            return Result.fail(f"File không tồn tại: {filepath}")

        if path.stat().st_size == 0:
            return Result.fail(f"File rỗng: {filepath}")

        content = path.read_text(encoding="utf-8")
        logger.info(f"Đọc file thành công: {filepath} ({len(content)} chars)")
        return Result.ok(content)

    except PermissionError:
        return Result.fail(f"Không có quyền đọc file: {filepath}")
    except UnicodeDecodeError:
        return Result.fail(f"File không phải UTF-8: {filepath}")
    except Exception as e:
        logger.exception(f"Lỗi không xác định khi đọc {filepath}")
        return Result.fail(str(e))


if __name__ == "__main__":
    # Test Result pattern
    test_amounts = ["1,500,000", "abc", "-500", "3000000 VND", ""]

    print("=== Safe Amount Parsing ===")
    for val in test_amounts:
        result = safe_parse_amount(val)
        if result.success:
            print(f"  ✅ '{val}' → {result.data:,.0f}")
        else:
            print(f"  ❌ '{val}' → {result.error}")

    print("\n=== Safe File Reading ===")
    result = read_file_safe("data/raw/orders.csv")
    if result.success:
        print(f"  ✅ Đọc thành công: {len(result.data.splitlines())} dòng")
    else:
        print(f"  ❌ Lỗi: {result.error}")
