# Việc chủ dự án cần tự làm

Xếp theo thứ tự gần tiền nhất. Xong việc nào thì nhắn Claude câu in đậm ở cuối việc đó. Không gửi mật khẩu hay khóa vào khung chat.

Khóa của dự án dán vào GitHub Secrets (để máy chủ GitHub chạy hằng ngày dùng được):
https://github.com/duongtrongtin0506-hue/game-factory/settings/secrets/actions → **New repository secret** → điền Name đúng như ghi dưới, dán giá trị vào Secret → **Add secret**.

## 1. Chơi thử Car Jam Escape bản 2 (5 phút)

Mở `C:\Users\Administrator\Desktop\GAME\web\web\car-jam\index.html` bằng Chrome, chơi 5 màn. Thấy ổn thì Claude tạo bài nộp mới trên CrazyGames. Nhắn: **car jam ổn** hoặc mô tả chỗ chưa ổn.

## 2. Đăng nhập GameMonetize trong Chrome (2 phút)

1. Mở https://gamemonetize.com/account/login.php trong Chrome thường, đăng nhập.
2. Nhắn: **xong gamemonetize**. Claude xem kết quả duyệt Tap Arcade (nộp 2026-10-09).

## 3. Webhook Discord kênh #game (2 phút)

1. Server **Máy chủ của net24**: giữ (hoặc chuột phải) kênh **#game** → **Chỉnh sửa kênh** → **Tích hợp** → **Webhook** → **Tạo webhook** → **Sao chép URL webhook**.
2. Dán vào GitHub Secrets với Name `DISCORD_WEBHOOK`.
3. Nhắn: **xong discord**.

Không dùng kênh #dang-tiktok hay server Coinnew24. Nếu đã tạo webhook từ trước: chỉ cần sao chép lại URL và làm bước 2.

## 4. healthchecks.io (3 phút, miễn phí)

1. Mở https://healthchecks.io → tạo check tên `game-factory`, **Period 1 day**, **Grace 6 hours**.
2. Sao chép **Ping URL**, dán vào GitHub Secrets với Name `HC_PING`.
3. **Integrations** → **Discord** → chọn server **Máy chủ của net24**, kênh **#game**.
4. Nhắn: **xong healthchecks**.

## 5. Kiểm tra Gmail

Tìm thư từ GameDistribution hoặc Azerion Connect (đăng ký 2026-10-09), làm theo hướng dẫn kích hoạt. Nhắn: **có thư gamedistribution**.

## 6. Tài khoản itch.io (5 phút, miễn phí)

1. Đăng ký tại https://itch.io/register (bạn tự đặt mật khẩu).
2. Mở https://itch.io/user/settings/api-keys → **Generate new API key** → sao chép.
3. GitHub Secrets: Name `BUTLER_API_KEY` = khóa vừa sao chép; Name `ITCH_USER` = tên tài khoản itch.io.
4. Nhắn: **xong itch**.

## Chưa cần làm

Tài khoản và khóa Roblox: chưa thấy dấu vết bạn đã có. Chỉ cần khi đã chọn được game làm bản Roblox, tức là sau khi có 14 ngày số liệu.
