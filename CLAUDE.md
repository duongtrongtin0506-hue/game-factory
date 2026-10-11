# game-factory

Kho GitHub riêng tư: `duongtrongtin0506-hue/game-factory` (nhánh `main`).
Thư mục trên máy: `C:\Users\Administrator\Desktop\GAME\web`.

## Mục tiêu

Làm game HTML5 nhỏ, nhiều màn, đăng lên các cổng game chia doanh thu quảng cáo.
Mục tiêu gần: có đồng doanh thu đầu tiên. Chủ dự án không trả trước cho bên thứ ba nào.

## Sơ đồ

| Đường dẫn | Nội dung |
|---|---|
| `tap-arcade/index.html` | 9 mini game, chế độ Journey 45 màn |
| `boba-sort/index.html` | Xếp trân châu, 100 màn |
| `car-jam/index.src.html` + `car-jam/tools/levels.txt` | Trượt xe, 100 màn; `build.ps1` ghép thành `car-jam/index.html` |
| `car-jam/tools/gen-levels.js` | Sinh và giải màn Car Jam (BFS) |
| `tile-trio/index.html` | Ghép ba ô, 100 màn |
| `one-line/index.html` | Vẽ một nét, 100 màn |
| `pop-the-balloon/` | Bản thử đầu tiên, không đăng |
| `build.ps1` | Đóng gói mỗi game cho từng cổng vào `dist/` (không commit) |
| `THEO-DOI.md` | Trạng thái nộp và duyệt từng game |
| `HUONG-DAN-CHU.md` | Việc chủ dự án phải tự bấm |

Mỗi game là một tệp HTML duy nhất, vẽ bằng canvas, không có ảnh hay âm thanh ngoài.
Cổng quảng cáo chọn bằng hằng `PORTAL` trong tệp (`gamemonetize` / `crazygames` / `none`); `build.ps1` đổi hằng này.
Chạy thử trên máy: mở `index.html`, hoặc phục vụ thư mục qua `http://127.0.0.1` để dùng `?level=N`, `?play=`, `?demo=`.

## Quy tắc

- Không làm game thứ 6 khi chưa có số liệu 14 ngày của 5 game hiện có.
- Không sửa hay nộp lại bản đang chờ duyệt; sửa ở nhánh riêng.
- Mọi màn mới phải được bộ giải xác nhận giải được.
- Không cờ bạc, không hộp quà may rủi, không link ra ngoài, không thu dữ liệu cá nhân.
- Không ghi mật khẩu hay khóa vào tệp. Bước đồng ý điều khoản và nhập mật khẩu do chủ dự án làm.

## Việc dở

Xem `THEO-DOI.md` (trạng thái) và `HUONG-DAN-CHU.md` (việc cần chủ dự án).

Hoãn đến khi có game được duyệt: tự động hóa bằng GitHub Actions, báo Discord, healthchecks,
tạo màn bằng Gemini, bản Roblox, itch.io.
