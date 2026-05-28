#!/bin/bash
# ===================================================
# web_crawler.sh — CLI Web Crawler cho Data Engineer
# Sử dụng:
#   ./web_crawler.sh [URL] [KEYWORD] [OUTPUT_DIR]
# Ví dụ:
#   ./web_crawler.sh "https://news.ycombinator.com" "data" data/raw/hn
# ===================================================
set -euo pipefail   # Dừng nếu có lỗi, unbound variable, pipe fail

# ==================== CONFIG ====================
URL="${1:-https://news.ycombinator.com}"
KEYWORD="${2:-}"
OUTPUT_DIR="${3:-data/raw/crawled}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/crawl_${TIMESTAMP}.txt"
LOG_FILE="logs/crawler_${TIMESTAMP}.log"
MAX_RETRIES=3
DELAY=1   # Giây delay giữa các request (lịch sự với server)

# ==================== SETUP ====================
mkdir -p "$OUTPUT_DIR" logs

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_FILE"
}

# ==================== FUNCTIONS ====================
# Kiểm tra dependencies
check_deps() {
    local missing=()
    for cmd in curl awk grep sed; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log "ERROR" "Thiếu commands: ${missing[*]}"
        exit 1
    fi
    log "INFO" "Tất cả dependencies OK"
}

# Lấy nội dung trang web với retry
fetch_page() {
    local url="$1"
    local attempt=1

    while [ $attempt -le $MAX_RETRIES ]; do
        log "INFO" "Fetching: $url (lần $attempt/$MAX_RETRIES)"

        local http_code

        # Lấy HTTP code và content
        http_code=$(curl -s -o /tmp/page_content.html \
            -w "%{http_code}" \
            --connect-timeout 10 \
            --max-time 30 \
            -H "User-Agent: Mozilla/5.0 (compatible; DE-Lab-Crawler/1.0)" \
            "$url" 2>/dev/null)

        if [ "$http_code" = "200" ]; then
            log "INFO" "HTTP $http_code — OK"
            cat /tmp/page_content.html
            return 0
        elif [ "$http_code" = "429" ]; then
            log "WARN" "Rate limited (429), chờ 5 giây..."
            sleep 5
        else
            log "WARN" "HTTP $http_code — thử lại sau ${DELAY}s"
            sleep "$DELAY"
        fi

        ((attempt++))
    done

    log "ERROR" "Không thể fetch sau $MAX_RETRIES lần thử"
    return 1
}

# Extract và clean text từ HTML
extract_text() {
    local html_content="$1"

    echo "$html_content" \
        | sed 's/<script[^>]*>.*<\/script>//gI' \
        | sed 's/<style[^>]*>.*<\/style>//gI' \
        | sed 's/<[^>]*>//g' \
        | sed 's/&nbsp;/ /g' \
        | sed 's/&amp;/\&/g' \
        | sed 's/&lt;/</g' \
        | sed 's/&gt;/>/g' \
        | sed 's/&quot;/"/g' \
        | awk 'NF > 0' \
        | awk '{$1=$1; print}' \
        | grep -v '^[[:space:]]*$'
}

# Lọc theo keyword (nếu có)
filter_keyword() {
    local keyword="$1"

    if [ -z "$keyword" ]; then
        cat   # Nếu không có keyword, giữ nguyên
    else
        grep -i "$keyword" || true
    fi
}

# Tạo metadata header
write_metadata() {
    cat << METADATA
===================================================
CRAWLER REPORT
===================================================
URL       : $URL
Keyword   : ${KEYWORD:-"(không lọc)"}
Timestamp : $TIMESTAMP
Output    : $OUTPUT_FILE
===================================================
METADATA
}

# ==================== MAIN ====================
main() {
    log "INFO" "========= Web Crawler bắt đầu ========="
    log "INFO" "URL: $URL"
    log "INFO" "Keyword: ${KEYWORD:-"(tất cả)"}"
    log "INFO" "Output: $OUTPUT_FILE"

    check_deps

    # Fetch trang web
    local raw_content
    raw_content=$(fetch_page "$URL")

    # Extract text
    log "INFO" "Đang extract text..."
    local clean_text
    clean_text=$(extract_text "$raw_content")

    # Đếm dòng trước khi lọc
    local total_lines
    total_lines=$(echo "$clean_text" | wc -l)
    log "INFO" "Tổng số dòng sau extract: $total_lines"

    # Lọc keyword và ghi output
    {
        write_metadata
        echo "$clean_text" | filter_keyword "$KEYWORD"
    } > "$OUTPUT_FILE"

    local output_lines
    output_lines=$(wc -l < "$OUTPUT_FILE")

    log "INFO" "Ghi ra file: $OUTPUT_FILE ($output_lines dòng)"
    log "INFO" "========= Hoàn tất ========="

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ CRAWL THÀNH CÔNG"
    echo "   📄 Output : $OUTPUT_FILE"
    echo "   📋 Log    : $LOG_FILE"
    echo "   📊 Dòng   : $output_lines"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main "$@"
