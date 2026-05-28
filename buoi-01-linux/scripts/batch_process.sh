#!/bin/bash
# Xử lý nhiều file trong một thư mục

INPUT_DIR="data/raw"
OUTPUT_DIR="data/processed"
mkdir -p "$OUTPUT_DIR"

echo "🚀 Bắt đầu batch processing..."
PROCESSED=0
FAILED=0

for file in "$INPUT_DIR"/*.csv; do
    filename=$(basename "$file" .csv)
    output="$OUTPUT_DIR/${filename}_clean.csv"

    # Bỏ qua file rỗng
    if [ ! -s "$file" ]; then
        echo "  [SKIP] $file — file rỗng"
        continue
    fi

    # Xử lý: giữ header, bỏ dòng cancelled
    {
        head -1 "$file"                          # Giữ header
        grep -v "cancelled" "$file" | tail -n +2 # Lọc data
    } > "$output"

    lines=$(wc -l < "$output")
    echo "  [OK] $filename → $lines dòng"
    ((PROCESSED++))
done

echo ""
echo "✅ Hoàn tất: $PROCESSED files processed, $FAILED failed"
