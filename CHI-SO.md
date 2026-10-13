# Chỉ số xưởng game

Cập nhật tay mỗi chủ nhật (số từ bảng điều khiển cổng do chủ chép vào mục CẦN CHÉP SỐ); số game, số gói, tỷ lệ tự động đếm từ kho.

## 13/10/2026

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| Doanh thu tháng 10 | 0 | chưa game nào lên sóng |
| Game trong kho | 6 | 6 game đủ (Merge Harvest xong 13/10) |
| Game đang sống trên cổng | 0 | Tap Arcade bản 5 trò chờ duyệt GameMonetize từ 09/10 |
| Cổng có tài khoản | 3 + itch.io | CrazyGames, GameMonetize, GameDistribution (chờ kích hoạt) |
| Gói nộp sẵn sàng | 18 | 6 game × 3 cổng; 12 gói còn thiếu mã game của cổng |
| Màn chơi | 525 | Car Jam 120, Boba Sort 120, Tile Trio 120, One Line Fill 120, Tap Arcade 45 chặng |
| Lần chạy `daily` đạt | 3/3 | 11–13/10 |

## Chi phí

| Khoản | Tháng 10 | Ghi chú |
|---|---|---|
| Claude (khung chat + routine) | chưa đo | gói thuê bao của chủ; routine chưa chạy. Cần chủ cho biết giá gói để tính |
| GitHub Actions | 0 | trong 2.000 phút miễn phí; mỗi ngày ~5 phút (≈ 150 phút/tháng) + các lần chạy khi sửa `tools/` |
| Khóa AI vẽ hình, âm thanh | 0 | không dùng |
| Phí cổng, tên miền, máy chủ | 0 | không có |

## Tỷ lệ tự động

| Khâu | Tự động? |
|---|---|
| Sinh màn, kiểm màn, thêm màn hằng tuần | có |
| Build, kiểm thử trình duyệt, đo tải | có |
| Ảnh bìa, video, mô tả, đóng gói theo cổng | có (`tools/quay.py`, `tools/build.py`) |
| Báo cáo ngày, tuần | có |
| Nộp lên cổng, xem kết quả duyệt | KHÔNG (chủ bấm; itch.io thì có) |
| Chép số liệu từ cổng | KHÔNG |
| Làm game mới, nâng chất lượng | bán tự động (Claude làm, routine chưa chạy) |

7/10 khâu tự động. Hai khâu tay còn lại là điểm nghẽn tới tiền: xem đề xuất ở `NHAT-KY-CAI-TIEN.md` mỗi chủ nhật.

## Ngưỡng quyết định (mục 7 kế hoạch)

- Game 30 ngày không có lượt chơi → ngừng đầu tư. Top 20% → tầng 2 (thêm màn, ngôn ngữ, bản Roblox).
- Cổng 60 ngày không đem lại gì → đề xuất bỏ.
