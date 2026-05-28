# 🐧 Buổi 1 — Linux, Shell & Dev Environment

**Data Engineer: Zero to Hero | Phase 1 – Engineering Foundations**
Thời gian: 2.5 tiếng | Lab: 60 phút (80–140 phút)

## 🎯 Mục tiêu Lab

Sau buổi này học viên sẽ:

- Cài được Ubuntu trên WSL2 hoặc kết nối EC2
- Thành thạo 20 lệnh Linux cốt lõi cho DE
- Viết Bash script tự động crawl text từ web
- Setup tmux để làm việc multi-panel
- Tạo Cron job chạy script định kỳ

## 🛠 Yêu cầu cài đặt trước buổi học

| Tool | Link tải | Ghi chú |
|------|----------|---------|
| Windows 11 hoặc 10 (build 19041+) | — | Hoặc dùng EC2 Ubuntu |
| VS Code | https://code.visualstudio.com | Extension: Remote-WSL |
| AWS CLI | https://aws.amazon.com/cli | Nếu dùng EC2 |

---

## PHẦN 1 — Setup Ubuntu WSL2 (15 phút)

### 1.1 Cài WSL2 trên Windows

Mở PowerShell với quyền Administrator, chạy:

```powershell
# Bật WSL2
wsl --install
# Kiểm tra version
wsl --list --verbose
# Nếu chưa có Ubuntu, cài thêm
wsl --install -d Ubuntu-22.04
```

Sau khi cài xong, Ubuntu sẽ yêu cầu tạo username/password. Tạo user `deuser` với password tuỳ chọn.

### 1.2 Cập nhật hệ thống Ubuntu

```bash
# Cập nhật package list
sudo apt update && sudo apt upgrade -y
# Cài các tool cơ bản
sudo apt install -y \
  curl wget git vim tree \
  jq unzip net-tools \
  python3 python3-pip python3-venv \
  tmux htop
# Kiểm tra
python3 --version   # Python 3.10.x
git --version       # git version 2.x
curl --version      # curl 7.x
```

### 1.3 (Tuỳ chọn) Dùng EC2 Ubuntu thay WSL2

```bash
# Trên máy local — tạo key pair
ssh-keygen -t ed25519 -C "de-lab-key" -f ~/.ssh/de_lab_key
# Kết nối vào EC2 (thay IP thực)
ssh -i ~/.ssh/de_lab_key ubuntu@<EC2_PUBLIC_IP>
# Thêm vào ~/.ssh/config để dùng alias
cat >> ~/.ssh/config << 'EOF'
Host de-lab
    HostName <EC2_PUBLIC_IP>
    User ubuntu
    IdentityFile ~/.ssh/de_lab_key
    ServerAliveInterval 60
EOF
```

Sau này chỉ cần: `ssh de-lab`

---

## PHẦN 2 — Linux Filesystem & Permissions (10 phút)

### 2.1 Khám phá filesystem

```bash
ls -la /
ls /etc        # Config files
ls /var/log    # Log files — nơi tìm lỗi
ls /tmp        # Temporary files
ls /home       # User home directories
ls /opt        # Optional software
pwd
mkdir -p ~/de-lab/data ~/de-lab/scripts ~/de-lab/logs
cd ~/de-lab
tree .
```

### 2.2 Permissions — đọc và chỉnh sửa

```bash
touch scripts/test.sh
echo '#!/bin/bash
echo "Hello DE!"' > scripts/test.sh
ls -la scripts/test.sh          # -rw-r--r-- (Owner=rw, Group=r, Others=r)
chmod +x scripts/test.sh
ls -la scripts/test.sh          # -rwxr-xr-x
./scripts/test.sh               # Hello DE!

# Symbolic notation
chmod 755 scripts/test.sh       # rwxr-xr-x
chmod 644 data/file.csv         # rw-r--r--
chmod 700 ~/.ssh                # rwx------ (quan trọng cho SSH!)

whoami
id
sudo chown deuser:deuser scripts/test.sh
```

### 2.3 Lệnh thao tác file/thư mục

```bash
cd ~/de-lab
mkdir -p data/{raw,processed,archive}
touch data/raw/orders_{001..005}.csv
tree data/

cp data/raw/orders_001.csv data/processed/orders_001_clean.csv
mv data/raw/orders_005.csv data/archive/
mv data/raw/orders_004.csv data/raw/orders_004_backup.csv

rm data/raw/orders_004_backup.csv
rm -rf data/archive

find ~/de-lab -name "*.csv" -type f
find ~/de-lab -name "*.csv" -newer data/raw/orders_001.csv
find /var/log -name "*.log" -size +1M

du -sh ~/de-lab/*
df -h /
```

---

## PHẦN 3 — Text Processing Tools (10 phút)

### 3.1 Tạo data mẫu

```bash
cd ~/de-lab
cat > data/raw/orders.csv << 'EOF'
order_id,customer_id,product,amount,status,date
1001,C001,Laptop,15000000,completed,2024-01-15
1002,C002,Phone,8000000,completed,2024-01-15
1003,C003,Tablet,12000000,pending,2024-01-16
1004,C001,Headphones,2000000,cancelled,2024-01-16
1005,C004,Laptop,15000000,completed,2024-01-17
1006,C005,Phone,8000000,pending,2024-01-17
1007,C002,Monitor,5000000,completed,2024-01-18
1008,C006,Laptop,15000000,completed,2024-01-18
EOF

cat data/raw/orders.csv
head -3 data/raw/orders.csv
tail -3 data/raw/orders.csv
wc -l data/raw/orders.csv
```

### 3.2 grep — tìm kiếm pattern

```bash
grep "completed" data/raw/orders.csv
grep -i "LAPTOP" data/raw/orders.csv      # case insensitive
grep -c "completed" data/raw/orders.csv   # đếm
grep -n "pending" data/raw/orders.csv     # kèm line number
grep -v "cancelled" data/raw/orders.csv   # tìm ngược
grep -E "C00[1-3]" data/raw/orders.csv    # regex
```

### 3.3 awk — xử lý theo column

```bash
awk -F',' '{print $1, $3}' data/raw/orders.csv
awk -F',' 'NR>1 {sum += $4} END {print "Total:", sum}' data/raw/orders.csv
awk -F',' 'NR>1 && $4 > 10000000 {print $0}' data/raw/orders.csv
awk -F',' 'NR>1 {count[$5]++} END {for(s in count) print s, count[s]}' data/raw/orders.csv
```

### 3.4 sed — tìm và thay thế

```bash
sed 's/completed/done/g' data/raw/orders.csv
sed 's/pending/in_progress/g' data/raw/orders.csv > data/processed/orders_updated.csv
sed '1d' data/raw/orders.csv                 # xoá header
sed 's/^/ROW: /' data/raw/orders.csv | head -3
```

### 3.5 Pipe — kết hợp các lệnh

```bash
# Pipeline 1: lọc completed, lấy product, đếm từng loại
grep "completed" data/raw/orders.csv \
  | awk -F',' '{print $3}' \
  | sort \
  | uniq -c \
  | sort -rn

# Pipeline 2: Top 3 đơn hàng lớn nhất
tail -n +2 data/raw/orders.csv \
  | sort -t',' -k4 -rn \
  | head -3 \
  | awk -F',' '{printf "Order %s: %s - %s VND\n", $1, $3, $4}'

# Redirect
grep "completed" data/raw/orders.csv > data/processed/completed_orders.csv
echo "Processing done" >> logs/pipeline.log
```

---

## PHẦN 4 — Bash Scripting (10 phút)

Buổi này xây 2 script chính (xem code đầy đủ trong [`../buoi-01-linux/scripts/`](../buoi-01-linux/scripts/)):

- **`check_data.sh`** — kiểm tra file dữ liệu, thống kê số dòng/size, phân tích status, tổng doanh thu completed, ghi log. Dùng biến, điều kiện `if`, màu terminal.
- **`batch_process.sh`** — vòng lặp `for` xử lý nhiều file CSV trong thư mục, bỏ qua file rỗng, lọc dòng `cancelled`, đếm kết quả.

```bash
chmod +x scripts/check_data.sh && ./scripts/check_data.sh
chmod +x scripts/batch_process.sh && ./scripts/batch_process.sh
```

---

## PHẦN 5 — tmux & Dev Environment Setup (5 phút)

```bash
tmux -V
cat > ~/.tmux.conf << 'EOF'
# Đổi prefix sang Ctrl+A
set -g prefix C-a
unbind C-b
bind C-a send-prefix
# Mouse + split dễ nhớ
set -g mouse on
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind r source-file ~/.tmux.conf \; display "Config reloaded!"
# Status bar
set -g status-style bg=black,fg=green
set -g status-left "[DE-LAB] "
set -g status-right "%H:%M %d-%m-%Y"
set -g base-index 1
EOF

tmux new-session -d -s de-lab
tmux attach -t de-lab
```

Phím tắt cần nhớ: `Ctrl+A |` / `Ctrl+A -` (split), `Ctrl+A + arrow` (di chuyển pane), `Ctrl+A c` (window mới), `Ctrl+A n/p` (window kế/trước), `Ctrl+A d` (detach).

---

## PHẦN 6 — LAB CHÍNH: CLI Web Crawler (30 phút)

```bash
cd ~/de-lab
sudo apt install -y lynx
curl -s --head https://example.com | head -5
```

Script chính: [`../buoi-01-linux/scripts/web_crawler.sh`](../buoi-01-linux/scripts/web_crawler.sh). Tính năng: fetch URL với retry + xử lý HTTP 429, extract & clean text từ HTML, lọc theo keyword, ghi metadata + log, dùng `set -euo pipefail`.

```bash
# Crawl HackerNews, tìm từ "data"
./scripts/web_crawler.sh "https://news.ycombinator.com" "data" data/raw/hn
# Crawl không keyword
./scripts/web_crawler.sh "https://httpbin.org/html" "" data/raw/test
# Crawl Python docs
./scripts/web_crawler.sh "https://www.python.org/about/" "python" data/raw/python
```

Workflow automation qua [`../buoi-01-linux/Makefile`](../buoi-01-linux/Makefile): `make help`, `make setup`, `make crawl`, `make process`, `make check`, `make pipeline`, `make status`, `make clean`.

### Cron Job — lên lịch tự động

```bash
crontab -e
# Thêm:
# Crawl 2AM hàng ngày
0 2 * * * cd ~/de-lab && ./scripts/web_crawler.sh "https://news.ycombinator.com" "data" data/raw/hn >> logs/cron.log 2>&1
# Data quality 3AM
0 3 * * * cd ~/de-lab && ./scripts/check_data.sh data/raw/orders.csv >> logs/quality_check.log 2>&1
# Dọn log cũ > 30 ngày, Chủ nhật 4AM
0 4 * * 0 find ~/de-lab/logs -name "*.log" -mtime +30 -delete
```

---

## PHẦN 7 — Kiểm tra tổng kết

Chạy [`../buoi-01-linux/scripts/lab_check.sh`](../buoi-01-linux/scripts/lab_check.sh) — checklist PASS/FAIL 10 mục (Ubuntu, Python3, thư mục, scripts, Makefile, file crawled, tmux, cron).

---

## 📚 Homework

1. **Mở rộng crawler**: đọc nhiều URL từ file `urls.txt`.
   ```bash
   while IFS= read -r url; do
     ./scripts/web_crawler.sh "$url" "" data/raw/multi
     sleep 2
   done < urls.txt
   ```
2. **Báo cáo HTML**: sửa `check_data.sh` để xuất ra file HTML thay vì terminal.
3. **Cron nâng cao**: setup cron crawl 5 website khác nhau, mỗi job cách nhau 10 phút.

---

**Buổi tiếp theo:** [Buổi 2 — Python cho Data Engineering](buoi-02-python-etl.md)
