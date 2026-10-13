# Tài nguyên và giấy phép

Kiểm 13/10/2026 bằng cách tìm trong mọi `web/*/index.src.html` và `web/ads.js` các dấu hiệu tệp ngoài (`new Image`, `<img`, `.png`, `.jpg`, `.mp3`, `.ogg`, `new Audio`, `@font-face`, đường dẫn `http`): chỉ có 3 đường dẫn SDK quảng cáo của cổng trong `web/ads.js`.

| Thứ | Nguồn | Giấy phép |
|---|---|---|
| Hình trong 6 game (xe, cốc, hạt, quân bài, vật phẩm, biểu tượng) | vẽ bằng lệnh canvas trong mã nguồn của xưởng | của xưởng, toàn quyền |
| Âm thanh, nhạc nền | tổng hợp bằng Web Audio trong mã (không có tệp âm thanh) | của xưởng, toàn quyền |
| Chữ | font hệ thống của máy người chơi (chuỗi font trong `THIET-KE.md`); không nhúng, không tải font | không phân phối font nên không cần giấy phép |
| Ảnh bìa, video xem trước (`assets-goc/<game>/`) | `tools/quay.py` chụp từ chính game | của xưởng, toàn quyền |
| SDK quảng cáo (GameMonetize, GameDistribution, CrazyGames) | tải từ máy chủ của cổng lúc chạy, không chép vào kho | theo điều khoản từng cổng |
| Thư viện bên thứ ba trong game | không có | - |
| Công cụ dựng (không nằm trong game): Python, Playwright, Node, ffmpeg | cài trên máy dựng | mã nguồn mở, không phân phối kèm game |

## Tên game (tra 13/10/2026, mỗi tên một lượt tìm trên web; chưa phải tra nhãn hiệu)

| Tên | Thấy gì | Mức trùng | Đề xuất |
|---|---|---|---|
| Sprout Merge | không thấy game trùng tên chính xác (tên cũ "Merge Harvest" trùng "Farm: Merge Harvest" trên Playgama nên đã đổi) | thấp | giữ |
| Tap Arcade | không thấy trùng chính xác; gần nhất "TapCade: Mini Arcade" (Android) https://peerlist.io/raviujjwal/project/tapcade-mini-arcade | thấp | giữ |
| One Line Fill | không thấy trùng chính xác; cùng thể loại có "Fill - One-Line Puzzle" https://apps.apple.com/app/id1091456207 và "Fill One Line" | thấp | giữ |
| Car Jam Escape | một trang web game bên thứ ba dùng đúng tên này https://jeuxweb-france24.onrender.com/car-jam-escape.html ; nhiều app tên gần giống ("Car Jam Vehicle Escape", "Car Jam: Escape Traffic Puzzle") | vừa | cân nhắc đổi trước bài nộp mới |
| Boba Sort | trùng chính xác với một game itch.io (thể loại khác) https://ishaanm.itch.io/boba-sort ; App Store có "Boba Sort Cafe", "Boba Sort Puzzle: Bubble Tea" cùng thể loại | vừa–cao | nên đổi |
| Tile Trio | trùng chính xác với app "Tile Trio" cùng thể loại ghép ba trên App Store https://apps.apple.com/app/id6446942289 | cao | nên đổi trước khi nộp lại |

Game đã nộp không tự đổi tên; chủ chọn ở đầu `HUONG-DAN-CHU.md`. Đổi tên = sửa `<title>`, chữ ở menu và ảnh bìa trong `web/<game>/index.src.html`, mục `name` + `store.title` trong `specs/<game>.json`, rồi `python tools/build.py` và `python tools/quay.py <game>`.

Quy tắc khi thêm tài nguyên ngoài (hình AI vẽ, font nhúng, âm thanh tải về): thêm 1 dòng vào bảng trên gồm tệp, nguồn (link), giấy phép, ngày lấy; chỉ dùng giấy phép cho phép thương mại; không dùng tên, hình, nhân vật, nhạc của game khác.
