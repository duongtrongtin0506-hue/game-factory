# Hàng việc (tự lập, tự xếp ưu tiên theo mục 4 của KE-HOACH-V3.md)

Cách dùng: làm từ trên xuống; xong thì đổi `[ ]` thành `[x]` kèm ngày, commit + push; việc mới chèn đúng nhóm ưu tiên. `[nặng]` = cần model mạnh, routine đám mây bỏ qua. `[máy 2]` = cần máy có Chrome/dist/card hình, routine bỏ qua. Việc chỉ chủ làm được → đầu `HUONG-DAN-CHU.md`, không để ở đây. Dòng `[x]` cũ hơn 14 ngày thì xóa.

## 1. Lỗi làm game hỏng / không đăng được

- [ ] Xem `TRANG-THAI.md` + lần chạy `daily`, `weekly-selftest`, `bao-discord` gần nhất; 🔴 thì sửa theo bước lỗi (việc thường trực, mỗi lượt).
- [ ] `tools/test_ads.js` chỉ thử SDK giả: viết trang thử nạp SDK thật của từng cổng ở chế độ thử (CrazyGames có `?useLocalSdk=true`; GameDistribution có gameId thử) và ghi kết quả vào `CONG.md`.

## 2. Game bị cổng từ chối

- [ ] [nặng] Nâng chất lượng Boba Sort lên mức Car Jam bản 2 (cảnh nền theo chặng, hiệu ứng rót, nhạc, xu + sưu tầm cốc, phím tắt, hướng dẫn không chữ) rồi đưa vào CẦN NỘP cho CrazyGames (bài nộp mới) và các cổng khác.
- [ ] [nặng] Tương tự cho Tile Trio (kèm hạ độ khó 60 màn cuối: trung bình `hard` ~65 xuống ~45, xen màn dễ).
- [ ] [nặng] Tương tự cho Tap Arcade bản Journey.
- [x] 13/10 One Line Fill: giao diện mới, ảnh bìa mọi cỡ và 2 video đã có (`assets-goc/one-line`). Còn: nhạc nền.
- [x] 13/10 Gói của cả 5 game cho CrazyGames, GameMonetize, GameDistribution đã có và đã ghi vào CẦN NỘP ở đầu `HUONG-DAN-CHU.md`.

- [x] 13/10 Cả 5 game cũ đã đổi giao diện sang `THIET-KE.md` (Car Jam, Boba Sort, Tile Trio: nền giấy ấm + nhấn rừng; One Line Fill, Tap Arcade: nền đêm + nhấn đỏ); ảnh bìa mới ở `assets-goc/`. Chưa làm: 9 trò con trong Tap Arcade vẫn dùng màu vật thể cũ và chữ đậm (soát lại từng trò); video Tap Arcade (`?demo=` cũ còn chạy, chưa quay lại).

- [x] 13/10 Car Jam đổi giao diện sang `THIET-KE.md`: menu (thẻ đường xe chạy, 1 nút nhấn), chọn màn, gara, thanh trên, nút, màn thắng; luật chơi, bộ giải, quảng cáo giữ nguyên; kiểm thử đạt.
- [x] 13/10 Boba Sort đổi giao diện sang `THIET-KE.md` + `?demo=cover` + ảnh bìa, video mới (`assets-goc/boba-sort`); `tools/chup.py` chụp nhanh các màn hình để soát.
- [x] 13/10 Tile Trio đổi giao diện sang `THIET-KE.md` + `?demo=cover` + ảnh bìa, video mới (`assets-goc/tile-trio`).
- [x] 13/10 One Line Fill đổi giao diện sang `THIET-KE.md` bản nền đêm (nét vẽ là màu nhấn đỏ) + `?demo=cover` + ảnh bìa, video lần đầu có (`assets-goc/one-line`).
- [x] 13/10 `tools/quay.py <game>`: chụp ảnh bìa mọi cỡ (CrazyGames, GameMonetize, Playgama, Yandex) + 2 video bằng `?demo=` của game, ra `assets-goc/<game>/`; Car Jam đã chụp lại theo giao diện mới.
- [x] 13/10 Tap Arcade: 2 video mới theo giao diện mới (`assets-goc/tap-arcade`).

## 3. Game đang sống / gần lên sóng

- [x] 13/10 Car Jam: thêm 2 cảnh (DESERT ROAD, SUNSET HILLS), cảnh lặp lại khi hết, chữ thắng tính theo số màn, 120 màn, vào `TAKE_GAMES`; `run_daily --no-publish` đạt.
- [x] 13/10 `tools/carjam.py harden`: leo đồi đổi màn dễ trong hàng dự trữ thành màn ≥ 16 bước; nửa hàng dự trữ (20/40) đã là màn 16–23 bước; `run_daily` chạy thêm 40 giây mỗi ngày. Màn 101–120 đã vào game giữ nguyên (8–21 bước).
- [x] 13/10 Car Jam có thử thách ngày: 1 màn/ngày theo ngày (màn 21 trở đi), chuỗi ngày liên tiếp, thưởng 25–55 xu một lần/ngày, nút ở menu, `?daily=1` để thử.
- [x] 13/10 Thử thách ngày đã có ở Boba Sort, Tile Trio, One Line Fill (nút ở menu, chuỗi ngày, `?daily=1`).
- [ ] Car Jam: chọn mức khó + chướng ngại (ô khóa) theo `NGHIEN-CUU.md` mục game cùng thể loại. [nặng]

## 4. Game mới từ `Y-TUONG.md`

- [x] 13/10 Bản thử "Merge Harvest" ở `web/merge-harvest/` theo `THIET-KE.md`: lưới 5x6, 10 bậc, đơn hàng, xu theo giây + xu vắng mặt, nâng cấp hạt, bán, lưu tiến trình, tắt tiếng, quảng cáo thưởng (nạp hạt, nhân đôi xu vắng mặt), bot `?selftest=1`; đã vào `build.py` + `smoke_test.py`. ĐẠT.
- [x] 13/10 Merge Harvest thành game đủ: mùa (giao Golden Tree → làm lại, mọi xu x1,5 mỗi mùa, nâng cấp đắt x4), thưởng ngày theo chuỗi, vòng sáng khi gộp, mô tả `store`, `tools/merge_sim.js` (bot tới Golden Tree ~17 phút mỗi mùa; người thật ước 25–35 phút, chưa đo), đã vào `phat-hanh/`.
- [x] 13/10 Đổi tên phát hành thành Sprout Merge ("Merge Harvest" trùng "Farm: Merge Harvest" trên Playgama); thư mục và khóa lưu giữ `merge-harvest`.
- [x] 13/10 Tra trùng tên 5 game: bảng ở `ASSETS.md`; Tile Trio, Boba Sort, Car Jam Escape có trùng, đề xuất tên mới đã ghi ở mục CẦN CHỌN đầu `HUONG-DAN-CHU.md`. Khi chủ chọn: đổi tên theo các bước cuối bảng `ASSETS.md`.
- [ ] Sprout Merge: nhạc nền nhẹ có nút tắt; đổi màu lá theo mùa.
- [x] 13/10 Merge Harvest: ảnh bìa mọi cỡ + 2 video (`assets-goc/merge-harvest`), `?demo=cover` và `?demo=<tên>`.
- [ ] Bản thử ý tưởng kế tiếp theo điểm (Mini Garden Idle hoặc Bolt Jam) sau khi game trên có kết luận. [nặng]
- [ ] Thứ hai hằng tuần: quét xu hướng → thêm mục tuần vào `XU-HUONG.md`, ≥ 5 ý tưởng mới vào `Y-TUONG.md` (lần tới: 19/10; thử mở thẳng trang New của từng cổng).

## 5. Đóng gói cho mọi cổng

- [x] 13/10 `tools/build.py` có `release()`: `phat-hanh/<cổng>/<game>/<game>.zip` + `mo-ta.md` cho 5 game × 3 cổng (15 gói), zip có trong git, ảnh bìa dùng chung ở `assets-goc/<game>/` (không chép lặp); `run_daily` và `daily.yml` cập nhật gói mỗi lần build.
- [x] 13/10 Cổng `playgama` (Playgama Bridge v2) trong `web/ads.js`, `tools/build.py` (zip kèm `playgama-bridge-config.json`), `tools/test_ads.js`; 6 gói ở `phat-hanh/playgama/`. Chi tiết và phần chưa xác minh: `CONG.md`.
- [ ] Cổng `yandex` (kèm tiếng Nga + `LoadingAPI.ready()`) và `gamepix`: tra lại tài liệu ngay trước khi viết, ghi nguồn. Poki: không làm (độc quyền). [nặng]
- [ ] Playgama: đọc `platform.language` và `AUDIO_STATE_CHANGED`; khi chủ có tài khoản thì chạy Test Game và sửa theo kết quả.
- [x] 13/10 Mục `store` (mô tả tiếng Anh) cho 5 game trong `specs/`.
Quy ước: sau mỗi gói mới thì thêm dòng vào CẦN NỘP ở đầu `HUONG-DAN-CHU.md` (game, cổng, đường dẫn zip, link trang nộp) và cập nhật bảng game × cổng trong `THEO-DOI.md`.

## 6. Bản Roblox cho game thắng

- [ ] Chưa có game thắng (chưa có số liệu). Khi có: dựng khung Rojo + Luau đọc `levels/<game>.json`, ghi việc chi tiết ở đây. Tài khoản/khóa Roblox nằm ở CẦN TẠO TÀI KHOẢN.

## 7. Cải tiến bộ khung / công cụ / tài liệu

- [x] 13/10 `VAN-HANH.md`: sổ tay tiếp quản (chạy trên máy mới, lịch tự động, khóa, phương án B, chuyển nhượng 48 giờ).
- [x] 13/10 `CHI-SO.md` (bản đầu, điền tay).
- [ ] `run_daily --weekly` tự đếm số game, số gói, số màn rồi ghi một mục tuần vào `CHI-SO.md`.
- [x] 13/10 `ASSETS.md`: đã soát cả 6 game, không có tệp hình/âm thanh/font ngoài.
- [x] 13/10 `THEO-DOI.md` có bảng game × cổng. Còn: chủ nhật sinh danh sách CẦN CHÉP SỐ khi có game lên sóng.
- [ ] Chủ nhật: 7 câu tự vấn vào `NHAT-KY-CAI-TIEN.md` (lần đầu 18/10). Đầu tháng: soi 8 vai. Đầu quý: radar + `THU-NGHIEM.md`.
- [x] 13/10 `run_daily`: Discord ngày dạng "🎮 Xong … · Gói chờ nộp N · Việc còn N · 📌 chờ chủ N việc"; chủ nhật kèm bảng game × cổng, 3 ý tưởng tuần, 1 đề xuất.
