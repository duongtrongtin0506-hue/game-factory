# Việc chủ dự án cần tự làm

Mỗi việc 1 dòng có link; xong thì nhắn Claude câu in đậm (hoặc nhờ Claude Desktop có Chrome trên máy 2 làm). Không gửi mật khẩu hay khóa vào khung chat. Máy tự thêm/bớt dòng ở 3 mục dưới; `[ ]` = chưa làm.

## CẦN NỘP (1 lần/tuần)

Mỗi gói có sẵn tệp zip và `mo-ta.md` (tên, mô tả, thẻ tiếng Anh để dán, danh sách ảnh bìa/video). Trước khi nộp: `git pull`. Nên nộp 2 game đầu trước, 3 game sau chờ kết quả (cả 4 game cũ từng bị CrazyGames chê chất lượng; nay đã đổi giao diện, nộp dồn một lúc mà bị từ chối tiếp thì hại tài khoản).

- [ ] Car Jam Escape → CrazyGames (bài nộp MỚI): https://developer.crazygames.com/ · `phat-hanh\crazygames\car-jam\car-jam.zip` · mô tả `phat-hanh\crazygames\car-jam\mo-ta.md`. Nhắn: **đã nộp car jam crazygames**.
- [ ] One Line Fill → CrazyGames (chưa nộp lần nào): https://developer.crazygames.com/ · `phat-hanh\crazygames\one-line\one-line.zip` · `phat-hanh\crazygames\one-line\mo-ta.md`. Nhắn: **đã nộp one line crazygames**.
- [ ] Sprout Merge (game mới, cơ chế gộp + idle, chưa nộp lần nào) → CrazyGames: https://developer.crazygames.com/ · `phat-hanh\crazygames\merge-harvest\merge-harvest.zip` · `phat-hanh\crazygames\merge-harvest\mo-ta.md`. Nhắn: **đã nộp sprout merge crazygames**.
- [ ] (sau khi 2 game trên có kết quả) Boba Sort, Tile Trio, Tap Arcade → CrazyGames, bài nộp mới: `phat-hanh\crazygames\<game>\`.
- [ ] Xem kết quả duyệt Tap Arcade trên GameMonetize: https://gamemonetize.com/account/login.php → My Games. Nhắn: **gamemonetize: duyệt / từ chối + lý do**.
- [ ] GameMonetize, 4 game còn lại (Car Jam, Boba Sort, Tile Trio, One Line Fill): https://gamemonetize.com/account/ → thêm game mới để lấy GameId của từng game → nhắn **gameid <tên game> <mã>** (mã game không phải mật khẩu) → máy build lại → tải `phat-hanh\gamemonetize\<game>\<game>.zip`.
## CẦN CHỌN (không chặn máy; chưa chọn thì máy giữ tên cũ)

- [ ] Tên game trùng game có thật (bảng ở `ASSETS.md`): Tile Trio trùng chính xác một app cùng thể loại; Boba Sort trùng một game itch.io và gần giống 2 app; Car Jam Escape trùng một trang web game. Tên thay thế đề xuất (mỗi tên đã tìm 0 lượt, máy sẽ tra trước khi đổi): Tile Trio → **Three of a Tile**; Boba Sort → **Pearl Cup Sort**; Car Jam Escape → **Red Car Out**. Nhắn: **đổi tên <tên cũ> thành <tên mới>** hoặc **giữ tên**. Nên chọn trước khi nộp 3 game này.

## CẦN TẠO TÀI KHOẢN

- [ ] GameDistribution: tìm thư kích hoạt (đăng ký 09/10) trong Gmail, từ GameDistribution hoặc Azerion. Nhắn: **có thư gamedistribution**.
- [ ] Cài Claude GitHub App cho kho game-factory (để routine đám mây đẩy mã được): https://github.com/apps/claude/installations/select_target → chọn tài khoản → **Only select repositories** → `game-factory` → **Save**. Nhắn: **xong github app**.
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
