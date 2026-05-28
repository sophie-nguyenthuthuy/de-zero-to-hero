#!/bin/bash
echo "================================================"
echo " BUỔI 1 LAB CHECK — Kết quả thực hành"
echo "================================================"
PASS=0
FAIL=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo "  ✅ $desc"
        ((PASS++))
    else
        echo "  ❌ $desc"
        ((FAIL++))
    fi
}

check "Ubuntu/WSL2 hoạt động"           "uname -a | grep -i linux"
check "Python 3 đã cài"                 "python3 --version"
check "Thư mục ~/de-lab tồn tại"        "[ -d ~/de-lab ]"
check "Thư mục data/raw tồn tại"        "[ -d ~/de-lab/data/raw ]"
check "Script web_crawler.sh tồn tại"   "[ -x ~/de-lab/scripts/web_crawler.sh ]"
check "Script check_data.sh tồn tại"    "[ -x ~/de-lab/scripts/check_data.sh ]"
check "Makefile tồn tại"                "[ -f ~/de-lab/Makefile ]"
check "Có file đã crawl"                "ls ~/de-lab/data/raw/hn/*.txt 2>/dev/null"
check "tmux đã cài"                     "command -v tmux"
check "Cron job đã setup"               "crontab -l | grep -q de-lab"

echo ""
echo "Kết quả: $PASS/10 ✅ | $FAIL ❌"
if [ $FAIL -eq 0 ]; then
    echo "🎉 HOÀN TOÀN ĐẠT! Chuyển sang Buổi 2."
elif [ $FAIL -le 2 ]; then
    echo "👍 GẦN ĐẠT! Kiểm tra lại các mục ❌"
else
    echo "🔄 CẦN ÔN LẠI — Xem lại hướng dẫn các bước bị lỗi"
fi
