# Theo dõi game

Cập nhật: 2026-10-11. Trạng thái duyệt là lần kiểm tra gần nhất, chưa xem lại sau ngày ghi.

## Kiểm kê

| Game | Thể loại | Số màn | Chạy được | Bộ giải kiểm màn |
|---|---|---|---|---|
| Tap Arcade | Arcade, 9 mini game | 45 (Journey) | Có | Không áp dụng (chơi vô tận) |
| Boba Sort | Xếp màu | 100 | Có | Có, 100/100 giải được |
| Car Jam Escape | Trượt khối | 100 (+40 dự trữ) | Có | Có: `tools/carjam.py` và bộ giải trong game cho cùng số bước ở 100/100 màn |
| Tile Trio | Ghép ba ô | 100 (+40 dự trữ) | Có | Có: `tools/tiletrio.py` giải được 100/100 (2026-10-12); độ khó đo bằng tỉ lệ thua của người chơi chỉ nhìn trước mắt |
| One Line Fill | Vẽ một nét | 100 | Có | Lời giải có sẵn hợp lệ 100/100; có 2 màn trùng nhau |

Cả 5 game qua `tools/smoke_test.py` (màn hình điện thoại dọc và ngang, không lỗi console) ngày 2026-10-11.
itch.io: có tài khoản và khóa (2026-10-12), chưa có trang game nào. Roblox: chưa có tài khoản.

## Nộp cổng

| Game | Cổng | Ngày | Trạng thái | SDK đúng cổng |
|---|---|---|---|---|
| Tap Arcade (bản 5 trò) | GameMonetize | 2026-10-09 | Đang chờ duyệt (xem lần cuối 2026-10-09) | Có, đã qua Verify |
| Tap Arcade (bản Journey) | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Boba Sort | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Car Jam Escape | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| Tile Trio | CrazyGames | 2026-10-11 | BỊ TỪ CHỐI 2026-10-11 | Có |
| One Line Fill | Chưa nộp | - | Chưa có ảnh bìa, video | Có sẵn trong mã |
| (tài khoản) | GameDistribution | 2026-10-09 | Đã gửi đăng ký, chờ thư | Chưa viết |

Ghi chú:
- Bốn game còn lại chưa lên GameMonetize: mỗi game cần một GameId riêng (hằng `GAME_ID` đang để trống).
- CrazyGames giai đoạn Basic Launch chưa chia tiền quảng cáo.
- 2026-10-11: cả 4 game gửi CrazyGames bị từ chối trong ngày, cùng một câu: "The overall quality of the game does not yet meet the expectations of our platform". Không nêu lỗi kỹ thuật. Không gửi lại bản cũ; chỉ gửi lại sau khi nâng chất lượng rõ rệt một game.
- CrazyGames xóa ảnh bìa và video mỗi khi tải bản game mới; phải tải lại.

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
