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

Tên game: Car Jam Escape, Boba Sort, Tile Trio, One Line Fill, Tap Arcade, Sprout Merge. 13/10: tìm trên web thấy "Merge Harvest" trùng "Farm: Merge Harvest" (đang có trên Playgama) nên đổi thành Sprout Merge (một lượt tìm không thấy game trùng tên chính xác; chưa phải tra nhãn hiệu). 5 tên còn lại chưa tra (việc trong `VIEC.md`).

Quy tắc khi thêm tài nguyên ngoài (hình AI vẽ, font nhúng, âm thanh tải về): thêm 1 dòng vào bảng trên gồm tệp, nguồn (link), giấy phép, ngày lấy; chỉ dùng giấy phép cho phép thương mại; không dùng tên, hình, nhân vật, nhạc của game khác.
