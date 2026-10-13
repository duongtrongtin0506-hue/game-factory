# Theo dõi game

Cập nhật: 2026-10-13. Trạng thái duyệt là lần kiểm tra gần nhất, chưa xem lại sau ngày ghi.

## Kiểm kê

| Game | Thể loại | Số màn | Chạy được | Bộ giải kiểm màn |
|---|---|---|---|---|
| Tap Arcade | Arcade, 9 mini game | 45 (Journey) | Có | Không áp dụng (chơi vô tận) |
| Boba Sort | Xếp màu | 100 | Có | Có, 100/100 giải được |
| Car Jam Escape | Trượt khối | 100 (+40 dự trữ) | Có | Có: `tools/carjam.py` và bộ giải trong game cho cùng số bước ở 100/100 màn |
| Tile Trio | Ghép ba ô | 100 (+40 dự trữ) | Có | Có: `tools/tiletrio.py` giải được 100/100 (2026-10-12); độ khó đo bằng tỉ lệ thua của người chơi chỉ nhìn trước mắt |
| One Line Fill | Vẽ một nét | 100 (+40 dự trữ) | Có | Có: `tools/oneline.py` giải được 100/100 (2026-10-12); màn 27 trùng màn 26 đã thay, không còn màn trùng |

Cả 5 game qua `tools/smoke_test.py` (màn hình điện thoại dọc và ngang, không lỗi console) ngày 2026-10-11.
itch.io: có tài khoản và khóa (2026-10-12), chưa có trang game nào. Roblox: chưa có tài khoản.

## Chuẩn giai đoạn 2 (đo 2026-10-12, `tools/smoke_test.py`)

Tải đo trên bản không quảng cáo, giả lập máy yếu (CPU chậm 4 lần) và mạng chậm (1,6 Mbit/s, trễ 150 ms), tính đến lúc có hình. Chưa tính thời gian SDK của cổng tự tải.

| Game | Tải (giới hạn 5 giây) | Hiểu luật trong 10 giây | Điện thoại dọc / ngang / máy tính 1280x720 |
|---|---|---|---|
| Tap Arcade | 1,1 giây | Màn giới thiệu trước mỗi trò | Không lỗi |
| Boba Sort | 0,7 giây | Mũi tên chỉ cốc ở màn 1 | Không lỗi |
| Car Jam Escape | 0,9 giây | Ngón tay kéo mẫu ở màn 1 | Không lỗi |
| Tile Trio | 0,9 giây | Mũi tên chỉ quân ở màn 1 | Không lỗi |
| One Line Fill | 0,7 giây | Chấm mờ chạy trước ở màn 1 | Không lỗi |

"Hiểu luật trong 10 giây" mới xét theo việc game có hướng dẫn ở màn đầu, chưa đo trên người chơi thật.

## Bảng game × cổng (cập nhật 2026-10-13)

Ô ghi: trạng thái · lượt chơi · thời gian chơi · quay lại · doanh thu (chưa có số thì bỏ trống). "gói" = đã có `phat-hanh/<cổng>/<game>/`, chờ chủ nộp.

| Game | CrazyGames | GameMonetize | GameDistribution | Playgama | Yandex |
|---|---|---|---|---|---|
| Car Jam Escape (giao diện mới, 120 màn) | bản 1 từ chối 11/10 · gói bản mới | tạm dừng cổng | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |
| Boba Sort (giao diện mới) | từ chối 11/10 · gói bản mới | tạm dừng cổng | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |
| Tile Trio (giao diện mới) | từ chối 11/10 · gói bản mới | tạm dừng cổng | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |
| One Line Fill (giao diện mới) | NỘP 13/10, chờ duyệt (https://developer.crazygames.com/games/32ccf42a-82c6-4ee2-8076-a8d117e15517) | tạm dừng cổng | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |
| Tap Arcade (giao diện mới) | từ chối 11/10 · gói bản mới | bản 5 trò nộp 09/10 → BỊ TỪ CHỐI (xem 13/10) | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |
| Sprout Merge (thư mục `merge-harvest`, game đủ 13/10) | gói, chưa nộp | tạm dừng cổng | gói, chờ tài khoản | gói, chờ tài khoản | chưa có SDK |

Lượt chơi, doanh thu: chưa có, chưa game nào lên sóng.

## Nộp cổng (lịch sử đến 2026-10-11)

| Game | Cổng | Ngày | Trạng thái | SDK đúng cổng |
|---|---|---|---|---|
| Tap Arcade (bản 5 trò) | GameMonetize | 2026-10-09 | BỊ TỪ CHỐI, trạng thái BANNED (xem 2026-10-13) | Có, đã qua Verify |
| Tap Arcade (bản Journey) | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Boba Sort | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Car Jam Escape | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Tile Trio | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| One Line Fill | CrazyGames | 2026-10-13 | Chờ duyệt (Awaiting review) | Có, QA của cổng nhận Gameplay Start + Data |
| (tài khoản) | GameDistribution | 2026-10-09 | Đã gửi đăng ký, chờ thư | Chưa viết |

Ghi chú:
- Bốn game còn lại chưa lên GameMonetize: mỗi game cần một GameId riêng (hằng `GAME_ID` đang để trống).
- CrazyGames giai đoạn Basic Launch chưa chia tiền quảng cáo.
- 2026-10-11: cả 4 game gửi CrazyGames bị từ chối trong ngày, cùng một câu: "The overall quality of the game does not yet meet the expectations of our platform". Không nêu lỗi kỹ thuật. Không gửi lại bản cũ; chỉ gửi lại sau khi nâng chất lượng rõ rệt một game.
- CrazyGames xóa ảnh bìa và video mỗi khi tải bản game mới; phải tải lại.
- 2026-10-13, GameMonetize từ chối Tap Arcade bản 5 trò: game không đạt chuẩn chất lượng "regardless of whether it was made with AI or not"; cổng ghi không nhận game làm bằng AI nữa và nộp lặp lại bản kém có thể bị khóa tài khoản. Tạm dừng cổng này (không lấy GameId cho 5 game còn lại) cho tới khi có game được cổng khác duyệt.
- 2026-10-13, One Line Fill nộp CrazyGames do khung chat tự làm bằng Chrome của chủ; cách làm ghi ở `CONG.md`.

## Car Jam Escape bản 2 (nhánh `car-jam-v2`, 2026-10-11)

Làm lại sau khi bị CrazyGames chê chất lượng. Màn chơi giữ nguyên (100 màn đã kiểm bằng BFS).
- Hình: 5 thế giới (mỗi 20 màn một cảnh), bãi xe có lề, đường ra và thanh chắn mở khi thắng; xe có 6 kiểu (thể thao, sedan, taxi, cảnh sát, tải, buýt).
- Hiệu ứng: xe trượt về ô, bụi, rung khi chạm, pháo giấy, sao nổ từng cái, chuyển cảnh mờ, nút sáng khi rê chuột.
- Âm thanh: nhạc nền tổng hợp (nút tắt riêng), thêm tiếng sao, xu, mua, nổ máy.
- Hướng dẫn: ngón tay kéo mẫu ở màn 1, lời nhắc ở màn 2 và 3.
- Tiến trình: xu thưởng theo sao, gara 6 mẫu xe mua bằng xu, gợi ý mua bằng 30 xu trước khi phải xem quảng cáo.
- Phím tắt máy tính: Z hoàn tác, R chơi lại, H gợi ý, Esc thoát.
- Đã thử trên máy: menu, chọn màn, gara, chơi hết màn 1 bằng kéo thả, màn thắng; ngang và dọc; không lỗi console.

Ảnh bìa (6 cỡ) và 2 video xem trước mới đã làm ngày 2026-10-11, nằm ở `dist/car-jam/assets`; sinh lại bằng `?demo=cover&w=&h=` và `?demo=<tên>&w=&h=` cùng máy chủ nhận khung hình. Nhánh đã gộp vào `main`.

Trang game bị từ chối trên CrazyGames (xem 2026-10-11) không có nút tải bản mới, chỉ có Preview và Remove game. Gửi lại phải tạo một bài nộp mới. Chưa tạo: chờ chủ dự án chơi thử bản 2 trước.

## Số liệu

Chưa có: chưa game nào lên sóng.
