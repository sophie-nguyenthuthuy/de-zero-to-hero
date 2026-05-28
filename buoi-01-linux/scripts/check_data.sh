#!/bin/bash
# ===================================================
# Script: check_data.sh
# Mô tả: Kiểm tra file dữ liệu và báo cáo thống kê
# ===================================================

# --- Biến ---
DATA_FILE="${1:-data/raw/orders.csv}"   # Nhận tham số hoặc dùng default
LOG_FILE="logs/check_$(date +%Y%m%d).log"
THRESHOLD=5                              # Số dòng tối thiểu

# --- Màu sắc terminal ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'   # No Color

echo "================================================"
echo " DATA QUALITY CHECK — $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"

# --- Kiểm tra file tồn tại ---
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}[ERROR] File không tồn tại: $DATA_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] File tìm thấy: $DATA_FILE${NC}"

# --- Thống kê cơ bản ---
TOTAL_LINES=$(wc -l < "$DATA_FILE")
DATA_LINES=$((TOTAL_LINES - 1))   # Trừ header
FILE_SIZE=$(du -sh "$DATA_FILE" | cut -f1)

echo ""
echo "📊 Thống kê file:"
echo "   Tổng dòng  : $TOTAL_LINES"
echo "   Dòng data  : $DATA_LINES"
echo "   Kích thước : $FILE_SIZE"

# --- Kiểm tra ngưỡng ---
if [ "$DATA_LINES" -lt "$THRESHOLD" ]; then
    echo -e "${YELLOW}[WARN] Ít hơn $THRESHOLD bản ghi — kiểm tra lại nguồn dữ liệu!${NC}"
fi

# --- Thống kê theo status ---
echo ""
echo "📈 Phân tích Status:"
awk -F',' 'NR>1 {count[$5]++} END {
    for(s in count) printf "  %-15s: %d đơn\n", s, count[s]
}' "$DATA_FILE" | sort

# --- Tổng doanh thu ---
TOTAL=$(awk -F',' 'NR>1 && $5=="completed" {sum+=$4} END {printf "%.0f", sum}' "$DATA_FILE")
echo ""
echo "💰 Tổng doanh thu (completed): $(printf "%'.0f" "$TOTAL") VND"

# --- Ghi log ---
mkdir -p logs
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checked $DATA_FILE — $DATA_LINES rows" >> "$LOG_FILE"

echo ""
echo -e "${GREEN}✅ Kiểm tra hoàn tất. Log: $LOG_FILE${NC}"
