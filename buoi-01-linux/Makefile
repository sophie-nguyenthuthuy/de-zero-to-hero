# ===================================================
# Makefile — DE Lab Workflow Automation (Buổi 1)
# Dùng: make <target>
# ===================================================
.PHONY: all crawl process check clean help setup pipeline status

# Biến
DATA_DIR  = data
RAW_DIR   = $(DATA_DIR)/raw
PROCESSED = $(DATA_DIR)/processed
LOG_DIR   = logs
CRAWLER   = scripts/web_crawler.sh
PROCESSOR = scripts/batch_process.sh
CHECKER   = scripts/check_data.sh

help: ## Hiển thị các lệnh có thể dùng
	@echo "Data Engineer Lab — Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-12s %s\n", $$1, $$2}'

setup: ## Tạo cấu trúc thư mục
	mkdir -p $(RAW_DIR) $(PROCESSED) $(LOG_DIR)
	@echo "✅ Thư mục đã được tạo"

crawl: setup ## Crawl dữ liệu từ web
	@echo "🕷️  Bắt đầu crawl..."
	./$(CRAWLER) "https://news.ycombinator.com" "data" $(RAW_DIR)/hn
	./$(CRAWLER) "https://www.python.org/about/" "" $(RAW_DIR)/python

process: ## Xử lý dữ liệu đã crawl
	@echo "⚙️  Đang process files..."
	./$(PROCESSOR)

check: ## Kiểm tra chất lượng data
	@echo "🔍 Kiểm tra data quality..."
	./$(CHECKER) $(RAW_DIR)/orders.csv

pipeline: crawl process check ## Chạy toàn bộ pipeline
	@echo "🚀 Pipeline hoàn tất!"

clean: ## Xoá files tạm
	rm -rf $(PROCESSED)/* $(LOG_DIR)/*
	@echo "🧹 Đã dọn dẹp"

status: ## Xem trạng thái files
	@echo "=== RAW FILES ==="
	@ls -lh $(RAW_DIR)/ 2>/dev/null || echo "(trống)"
	@echo ""
	@echo "=== PROCESSED FILES ==="
	@ls -lh $(PROCESSED)/ 2>/dev/null || echo "(trống)"
	@echo ""
	@echo "=== LOGS ==="
	@ls -lh $(LOG_DIR)/ 2>/dev/null || echo "(trống)"
