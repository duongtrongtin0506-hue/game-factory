# Việc chủ dự án cần tự làm

Mỗi việc 1 dòng có link; xong thì nhắn Claude câu in đậm (hoặc nhờ Claude Desktop có Chrome trên máy 2 làm). Không gửi mật khẩu hay khóa vào khung chat. Máy tự thêm/bớt dòng ở 3 mục dưới; `[ ]` = chưa làm.

## CẦN NỘP

Từ 13/10 khung chat trên máy tự nộp CrazyGames bằng Chrome đang đăng nhập của chủ (cách làm ở `CONG.md`). Chủ không phải bấm gì ở mục này; chỉ cần giữ Chrome đăng nhập CrazyGames.

- [x] 13/10 One Line Fill → CrazyGames: đã nộp, chờ duyệt.
- [x] 13/10 Sprout Merge → CrazyGames: đã nộp, chờ duyệt.
- [ ] (máy tự làm, sau khi One Line Fill có kết quả) Car Jam Escape, Boba Sort, Tile Trio, Tap Arcade → CrazyGames, bài nộp mới.
- [x] 13/10 Đã xem GameMonetize: Tap Arcade bản 5 trò BỊ TỪ CHỐI (không đạt chuẩn chất lượng; cổng không nhận game làm bằng AI, nộp lặp lại có thể khóa tài khoản). Máy tạm dừng cổng này, không lấy GameId cho các game khác. Muốn nộp tiếp thì nhắn: **nộp tiếp gamemonetize**.

## CẦN CHỌN

- [x] 13/10 Tên game trùng: chủ giao toàn quyền nên máy đã chọn theo đề xuất: Tile Trio → **Three of a Tile**, Boba Sort → **Pearl Cup Sort**, Car Jam Escape → **Red Car Out**. Máy đổi tên từng game ngay trước khi nộp bài mới của game đó (tra trùng lại lúc đổi). Muốn giữ tên cũ thì nhắn: **giữ tên <tên game>**.

## CẦN TẠO TÀI KHOẢN

- [ ] GameDistribution: 13/10 máy đã tìm trong Gmail, chưa có thư nào từ GameDistribution hoặc Azerion (mục Spam chưa xem). Nếu chủ nhớ đã đăng ký xong thì xem Spam; chưa thì đăng ký lại ở https://developer.gamedistribution.com/ (máy không được tự tạo tài khoản). Nhắn: **có thư gamedistribution**.
- [ ] Cài Claude GitHub App cho kho game-factory (để routine đám mây đẩy mã được). 13/10 máy đã thử làm thay: GitHub dừng ở trang "Confirm access" đòi xác minh danh tính qua email (mã gửi về hộp thư), bước này máy không được tự làm. Chủ mở https://github.com/settings/installations/167740239 → **Verify via email** → nhập mã → **Only select repositories** → thêm `game-factory` → **Save**. Nhắn: **xong github app**.
- [ ] Playgama (một lần nộp ra nhiều cổng đối tác, 6 gói đã sẵn): tạo tài khoản nhà phát triển tại https://developer.playgama.com/ → nhắn **xong tài khoản playgama** → máy chỉ từng bước Add Game / Test Game / Submit với `phat-hanh\playgama\<game>\<game>.zip`.
- [ ] Cổng khác (Yandex Games, GamePix…): chưa cần, xem `CONG.md`.
- [ ] (không bắt buộc) itch.io: tạo trang `car-jam-escape` theo mục 6 bên dưới.

## CẦN CHÉP SỐ (chủ nhật)

Chưa có: chưa game nào lên sóng.

---

## Hướng dẫn chi tiết (cũ, vẫn đúng)

Khóa của dự án dán vào GitHub Secrets (để máy chủ GitHub chạy hằng ngày dùng được):
https://github.com/duongtrongtin0506-hue/game-factory/settings/secrets/actions → **New repository secret** → điền Name đúng như ghi dưới, dán giá trị vào Secret → **Add secret**.

## 1. Chơi thử Car Jam Escape bản 2 (5 phút)

Mở `C:\Users\Administrator\Desktop\GAME\web\web\car-jam\index.html` bằng Chrome, chơi 5 màn. Thấy ổn thì Claude tạo bài nộp mới trên CrazyGames. Nhắn: **car jam ổn** hoặc mô tả chỗ chưa ổn.

## 2. Đăng nhập GameMonetize trong Chrome (2 phút)

1. Mở https://gamemonetize.com/account/login.php trong Chrome thường, đăng nhập.
2. Nhắn: **xong gamemonetize**. Claude xem kết quả duyệt Tap Arcade (nộp 2026-10-09).

## 3. Webhook Discord, 4. healthchecks.io

XONG 2026-10-12: hai khóa đã vào GitHub Secrets và lần chạy thử đã báo được.

## 5. Kiểm tra Gmail

Tìm thư từ GameDistribution hoặc Azerion Connect (đăng ký 2026-10-09), làm theo hướng dẫn kích hoạt. Nhắn: **có thư gamedistribution**.

## 6. Tạo trang Car Jam Escape trên itch.io (3 phút)

Tài khoản và hai khóa itch.io đã có (2026-10-12). Lần đẩy thử bị itch.io trả lời "invalid game": trang game chưa tồn tại, itch.io không tự tạo.

1. Mở https://itch.io/game/new (đang đăng nhập tài khoản itch.io của bạn).
2. **Title**: `Car Jam Escape`. **Project URL**: sửa phần cuối thành đúng `car-jam-escape`.
3. **Kind of project**: chọn **HTML**. **Pricing**: **No payments**. Không cần tải tệp nào lên.
4. Cuối trang, **Visibility & access** để **Draft** → **Save & view page**.
5. Nhắn: **xong trang itch**. Claude đẩy game lên rồi chỉ bạn hai ô cần tích để game chơi được trong trình duyệt.

Nếu itch.io không cho lưu khi chưa có tệp: bấm **Upload files**, chọn `C:\Users\Administrator\Desktop\GAME\web\dist\car-jam\car-jam-none.zip`, tích **This file will be played in the browser**, rồi lưu.

## Chưa cần làm

Tài khoản và khóa Roblox: chưa thấy dấu vết bạn đã có. Chỉ cần khi có game thắng (top 20% theo số liệu) để làm bản Roblox.

## Bản cập nhật tháng cho cổng web (chỉ làm khi game ĐÃ được cổng duyệt)

Máy tự thêm 20 màn mỗi thứ hai vào Boba Sort, Tile Trio, One Line Fill và tự đẩy lên itch.io. Cổng web (GameMonetize, CrazyGames, GameDistribution) phải nộp tay, mỗi tháng 1 lần, và chỉ với game đang ở trạng thái đã duyệt. Game đang chờ duyệt hoặc bị từ chối: không nộp bản này.

1. Trong khung chat game, nhắn: **bản tháng**. Claude kéo mã mới, build, và báo tệp cần tải của từng game, ví dụ `dist\boba-sort\boba-sort-gamemonetize.zip`.
2. GameMonetize: đăng nhập → **My Games** → game → **Edit** → tải tệp zip `...-gamemonetize.zip` mới vào ô game file → lưu, gửi duyệt lại.
3. CrazyGames: Developer Portal → game → **Update game** → tải `dist\<game>\crazygames\index.html` → tải lại ảnh bìa và video (CrazyGames xóa chúng mỗi lần đổi bản) từ `dist\<game>\assets` → gửi.
4. GameDistribution (khi tài khoản được duyệt): game → **Files** → tải `...-gamedistribution.zip` → gửi duyệt.
5. Nhắn: **xong bản tháng** kèm tên game và cổng đã nộp. Claude ghi ngày vào `THEO-DOI.md`.

Tên nút trên từng cổng có thể khác đôi chút: phần này viết sẵn theo cách đã nộp lần đầu, chưa nộp bản cập nhật nào thật.
