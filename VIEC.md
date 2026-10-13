# Hàng việc (tự lập, tự xếp ưu tiên theo mục 4 của KE-HOACH-V3.md)

Cách dùng: làm từ trên xuống; xong thì đổi `[ ]` thành `[x]` kèm ngày, commit + push; việc mới chèn đúng nhóm ưu tiên. `[nặng]` = cần model mạnh, routine đám mây bỏ qua. `[máy 2]` = cần máy có Chrome/dist/card hình, routine bỏ qua. Việc chỉ chủ làm được → đầu `HUONG-DAN-CHU.md`, không để ở đây. Dòng `[x]` cũ hơn 14 ngày thì xóa.

## 1. Lỗi làm game hỏng / không đăng được

- [ ] Xem `TRANG-THAI.md` + lần chạy `daily`, `weekly-selftest`, `bao-discord` gần nhất; 🔴 thì sửa theo bước lỗi (việc thường trực, mỗi lượt).
- [ ] `tools/test_ads.js` chỉ thử SDK giả: viết trang thử nạp SDK thật của từng cổng ở chế độ thử (CrazyGames có `?useLocalSdk=true`; GameDistribution có gameId thử) và ghi kết quả vào `CONG.md`.

## 2. Game bị cổng từ chối

- [ ] [nặng] Nâng chất lượng Boba Sort lên mức Car Jam bản 2 (cảnh nền theo chặng, hiệu ứng rót, nhạc, xu + sưu tầm cốc, phím tắt, hướng dẫn không chữ) rồi đưa vào CẦN NỘP cho CrazyGames (bài nộp mới) và các cổng khác.
- [ ] [nặng] Tương tự cho Tile Trio (kèm hạ độ khó 60 màn cuối: trung bình `hard` ~65 xuống ~45, xen màn dễ).
- [ ] [nặng] Tương tự cho Tap Arcade bản Journey.
- [ ] One Line Fill: nâng chất lượng tối thiểu (hiệu ứng, nhạc, sao) + tạo ảnh bìa các cỡ và 2 video xem trước bằng `?demo=` như Car Jam. [máy 2] cho phần quay video.
- [ ] Nộp các game đã bị CrazyGames từ chối sang cổng khác đã có gói (xem nhóm 5), không chờ nâng chất lượng: ghi vào CẦN NỘP.

- [ ] Đổi giao diện game cũ sang `THIET-KE.md` (chỉ menu, chọn màn, màn thắng/thua, nút, chữ; không đụng luật chơi, bộ giải, quảng cáo), mỗi game một việc, theo thứ tự: Boba Sort → Tile Trio → One Line Fill → Tap Arcade (Car Jam xong 13/10, xem `web/car-jam/index.src.html`: `C`, `head`, `tag`, `card`, `button`). Dùng lại `C`, `F`, `card`, `pill`, `label` của `web/merge-harvest/index.src.html`. Xong game nào thì chụp lại ảnh bìa game đó. [nặng]

- [x] 13/10 Car Jam đổi giao diện sang `THIET-KE.md`: menu (thẻ đường xe chạy, 1 nút nhấn), chọn màn, gara, thanh trên, nút, màn thắng; luật chơi, bộ giải, quảng cáo giữ nguyên; kiểm thử đạt.
- [x] 13/10 `tools/quay.py <game>`: chụp ảnh bìa mọi cỡ (CrazyGames, GameMonetize, Playgama, Yandex) + 2 video bằng `?demo=` của game, ra `assets-goc/<game>/`; Car Jam đã chụp lại theo giao diện mới.
- [ ] Thêm `?demo=cover` + `?demo=<tên>` (cùng giao thức `POST /frame` như Car Jam) cho Merge Harvest, One Line Fill, rồi chạy `tools/quay.py`; Boba Sort, Tile Trio, Tap Arcade chụp lại sau khi đổi giao diện.

## 3. Game đang sống / gần lên sóng

- [x] 13/10 Car Jam: thêm 2 cảnh (DESERT ROAD, SUNSET HILLS), cảnh lặp lại khi hết, chữ thắng tính theo số màn, 120 màn, vào `TAKE_GAMES`; `run_daily --no-publish` đạt.
- [ ] Car Jam: màn 101–120 chỉ 8–21 bước, dễ hơn màn 91–100 (18–31 bước). Sửa `tools/carjam.py fill` để hàng dự trữ có màn ≥ 20 bước (tăng thời gian tìm, giữ lại bàn nhiều bước nhất) trước lần thêm màn thứ hai 19/10.
- [ ] Thử thách ngày (1 màn/ngày theo hạt giống ngày, chuỗi ngày liên tiếp, lưu `localStorage`) cho Car Jam; đạt thì chép sang Boba Sort, Tile Trio, One Line Fill.
- [ ] Car Jam: chọn mức khó + chướng ngại (ô khóa) theo `NGHIEN-CUU.md` mục game cùng thể loại. [nặng]

## 4. Game mới từ `Y-TUONG.md`

- [x] 13/10 Bản thử "Merge Harvest" ở `web/merge-harvest/` theo `THIET-KE.md`: lưới 5x6, 10 bậc, đơn hàng, xu theo giây + xu vắng mặt, nâng cấp hạt, bán, lưu tiến trình, tắt tiếng, quảng cáo thưởng (nạp hạt, nhân đôi xu vắng mặt), bot `?selftest=1`; đã vào `build.py` + `smoke_test.py`. ĐẠT.
- [ ] Merge Harvest thành game đủ: (a) thử thách ngày + chuỗi ngày; (b) sau Golden Tree: "mùa mới" (làm lại, nhận hệ số xu, đổi bảng màu vật theo mùa: thu, đông/Giáng sinh, xuân, hạ); (c) hiệu ứng gộp (vòng sáng mềm, hạt nhỏ) và nhạc nền nhẹ có nút tắt; (d) cân kinh tế bằng bot: tới Golden Tree trong 25–40 phút chơi; (e) tra tên "Merge Harvest" không trùng game có thật, trùng thì đổi; (f) mục `store` trong `specs/merge-harvest.json`. [nặng] cho (b), (d).
- [ ] Merge Harvest: ảnh bìa các cỡ + 2 video xem trước bằng `?demo=` (theo `THIET-KE.md`: nền giấy ấm, 1 vật lớn ở giữa, tên game serif). [máy 2]
- [ ] Bản thử ý tưởng kế tiếp theo điểm (Mini Garden Idle hoặc Bolt Jam) sau khi game trên có kết luận. [nặng]
- [ ] Thứ hai hằng tuần: quét xu hướng → thêm mục tuần vào `XU-HUONG.md`, ≥ 5 ý tưởng mới vào `Y-TUONG.md` (lần tới: 19/10; thử mở thẳng trang New của từng cổng).

## 5. Đóng gói cho mọi cổng

- [ ] `tools/build.py`: xuất thêm `phat-hanh/<cổng>/<game>/` gồm zip đúng chuẩn cổng, `mo-ta.md` tiếng Anh (tên, mô tả ngắn/dài, thể loại, thẻ, hướng dẫn chơi, lấy từ mục `store` mới trong `specs/<game>.json`) và ảnh bìa đúng cỡ cổng. Cho zip và ảnh trong `phat-hanh/` lên git (sửa `.gitignore`: `!phat-hanh/**`), chuyển ảnh bìa gốc từ `dist/<game>/assets` sang `assets-goc/<game>/` có trong git (video để ngoài git).
- [ ] Thêm cổng vào `web/ads.js` + `PORTALS` + `tools/test_ads.js` theo `CONG.md`, mỗi cổng một việc: Playgama Bridge; Yandex Games (kèm tiếng Nga + `LoadingAPI.ready()`); Poki; GamePix. Tra lại tài liệu SDK ngay trước khi viết, ghi nguồn.
- [ ] Viết mục `store` (mô tả tiếng Anh) cho 5 game trong `specs/`.
- [ ] Sau mỗi gói mới: thêm dòng vào CẦN NỘP ở đầu `HUONG-DAN-CHU.md` (game, cổng, đường dẫn zip, link trang nộp) và cập nhật bảng game × cổng trong `THEO-DOI.md`.

## 6. Bản Roblox cho game thắng

- [ ] Chưa có game thắng (chưa có số liệu). Khi có: dựng khung Rojo + Luau đọc `levels/<game>.json`, ghi việc chi tiết ở đây. Tài khoản/khóa Roblox nằm ở CẦN TẠO TÀI KHOẢN.

## 7. Cải tiến bộ khung / công cụ / tài liệu

- [ ] `VAN-HANH.md`: sổ tay tiếp quản (sơ đồ, lệnh chạy, khóa nào ở đâu, lịch tự động, phương án B cho từng cổng, GitHub, Claude, Discord).
- [ ] `CHI-SO.md` (doanh thu, chi phí, số game sống, số cổng, tỷ lệ tự động) + `tools/run_daily.py --weekly` tự điền số game/cổng/tỷ lệ tự động và gửi bảng game × cổng chủ nhật.
- [ ] `ASSETS.md`: kê nguồn + giấy phép mọi hình, âm thanh (hiện tất cả tự vẽ bằng canvas và âm thanh tổng hợp trong mã: xác nhận từng game).
- [ ] `THEO-DOI.md`: đổi mục "Nộp cổng" thành bảng game × cổng (duyệt, lượt chơi, thời gian chơi, quay lại, doanh thu); chủ nhật sinh danh sách CẦN CHÉP SỐ.
- [ ] Chủ nhật: 7 câu tự vấn vào `NHAT-KY-CAI-TIEN.md` (lần đầu 18/10). Đầu tháng: soi 8 vai. Đầu quý: radar + `THU-NGHIEM.md`.
- [ ] `run_daily`: thông báo Discord dạng "🎮 Xong … · Gói chờ nộp N · Việc còn N" (đếm `[ ]` trong `VIEC.md` và CẦN NỘP), nhắc việc chờ chủ 1 lần/ngày.
- [ ] Sửa các câu "chờ số liệu 14 ngày" còn sót trong `HUONG-DAN-CHU.md`, `THEO-DOI.md`.
