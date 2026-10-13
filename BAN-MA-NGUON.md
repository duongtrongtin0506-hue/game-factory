# Bán mã nguồn game (mũi doanh thu thứ hai, mở 14/10/2026)

Chủ dặn 14/10: ngoài quảng cáo trên cổng, bán thêm mã nguồn game. Tệp này ghi số liệu đã xem tận nơi, kế hoạch và trạng thái. Chỗ nào ghi "chưa xác minh" thì phải mở trang đó xem lại trước khi dựa vào.

## Số liệu đã xem (14/10/2026)

| Chợ | Xem được gì | Nguồn |
|---|---|---|
| Codester | Mục "Construct 3 Games & Templates" có 486 sản phẩm (mô tả mục: dự án xuất ra HTML5 và di động, dễ đổi hình). 40 giá đầu trang xếp theo bán chạy: thấp nhất 19 USD, cao nhất 299 USD; 26/40 sản phẩm giá 19–29 USD; nhóm 89–299 USD là gói nhiều game. Người bán giữ 70% mỗi đơn, tự đặt giá, KHÔNG đòi độc quyền | https://www.codester.com/categories/213/construct-3-games-templates?sort=sales · https://www.codester.com/info/seller |
| Codester | Không có mục riêng cho game HTML5 viết tay (tìm "html5 game" ra 0 kết quả); game HTML5 đang nằm trong mục Construct 3. Sản phẩm của mình là JavaScript thuần: phải hỏi/đọc quy định xem đăng vào mục nào. Chưa xác minh: quy định về sản phẩm làm bằng AI, phí rút tiền, ngưỡng rút | – |
| SellAnyCode | Trang chủ ghi 7.125 sản phẩm; có game HTML5 giá 25 EUR ("Velocity Dash - Cyber Action Runner HTML5 Game Source"). Trang tìm kiếm lỗi 522 lúc xem: chưa xác minh phí và điều khoản | https://www.sellanycode.com/ |
| CodeCanyon (Envato) | Không đọc được: trang chặn bằng kiểm tra chống bot. Chưa xác minh giá, phí, quy định AI | https://codecanyon.net/category/html5/games |
| html5gamedevs.com | Một tin rao lẻ không ghi ngày: giấy phép ĐỘC QUYỀN một game HTML5 giá rao 350 USD. Là giá rao, không có bằng chứng bán được | https://www.html5gamedevs.com/tags/sale/ |
| itch.io | Đã có tài khoản `trong-tin.itch.io`; đặt giá cho tệp tải về được. Chưa xác minh mức phí hiện tại | https://itch.io/game/new |

Rút ra: giá thực tế của MỘT game nhỏ không độc quyền trên chợ là khoảng 19–29 USD mỗi lượt mua (người bán nhận 70%, tức 13–20 USD); thu nhập đến từ số lượt mua và từ gói nhiều game (89–299 USD). Con số "cả trăm đô một game" chỉ thấy ở gói nhiều game hoặc giá rao độc quyền.

## Bán cái gì

Không bán nguyên bản game đang nộp cổng (One Line Fill, Sprout Merge đang chờ duyệt/In Review: cổng đòi nội dung nguyên bản; người mua đăng lại sẽ thành bản trùng).

| Sản phẩm | Vì sao | Giá dự kiến | Trạng thái |
|---|---|---|---|
| Tap Arcade (9 trò, 45 chặng) | Bị từ chối ở cả CrazyGames và GameMonetize, không còn kế hoạch nộp cổng; nhiều trò trong một gói nên hợp người mua cần nội dung | 29 USD | chưa đóng gói |
| "Puzzle Level Kit": bộ sinh màn + bộ giải (`tools/carjam.py`, `bobasort.py`, `tiletrio.py`, `oneline.py`) kèm một game mẫu đổi hình | Cái khác biệt thật của xưởng là bộ giải bảo đảm màn giải được; trên chợ đa số là game đơn không có công cụ sinh màn | 49 USD | chưa đóng gói; chốt game mẫu sau khi có kết quả duyệt |
| "Portal Ads Layer": `web/ads.js` (CrazyGames, GameDistribution, Playgama, GameMonetize) + `tools/test_ads.js` + hướng dẫn | Đã được GameDistribution và công cụ QA của CrazyGames xác nhận chạy đúng | 19 USD hoặc tặng kèm | chưa đóng gói |
| Gói tất cả | Nhóm giá 89–299 USD trên chợ đều là gói | 89 USD | sau khi có 3 sản phẩm lẻ |

Mỗi gói bán phải có: mã nguồn đọc được (không nén), `README.md` tiếng Anh (chạy thử, đổi hình/màu/chữ, thêm màn, gắn quảng cáo từng cổng), `LICENSE.txt` nêu người mua được làm gì, bản chạy thử trực tuyến (trang itch.io), 5 ảnh chụp, 1 video. Ghi rõ trong mô tả: mã do AI hỗ trợ viết (khai thật, như đã khai ở itch.io và Playgama).

## Việc phải có chủ

- Tạo tài khoản người bán Codester (https://www.codester.com/info/seller → Start selling) và khai cách nhận tiền: máy không tự tạo tài khoản, không điền thông tin thanh toán.
- Quyết giá cuối nếu khác bảng trên.

## Rủi ro

- Người mua đổi hình rồi đăng lên cùng cổng với mình: chấp nhận với Tap Arcade (mình không nộp nữa); không bán game đang sống trên cổng.
- Chợ có thể từ chối sản phẩm làm bằng AI (GameMonetize đã từ chối game vì lý do này): đọc quy định từng chợ trước khi đăng.
- Doanh thu chưa có số liệu nào: sau 30 ngày đăng mà 0 lượt mua thì dừng làm gói mới, ghi vào `NHAT-KY-CAI-TIEN.md`.
