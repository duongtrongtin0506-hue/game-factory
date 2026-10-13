# Hiện trạng xưởng game (13/10/2026) – cái đã có trước KE-HOACH-V3

## Game (5 game web HTML5, mỗi game 1 tệp canvas, 28–66 KB, tiếng Anh)

| Game | Cơ chế | Màn | Bộ giải / dự trữ | Tự thêm màn | Ảnh bìa + video | Đã nộp |
|---|---|---|---|---|---|---|
| Tap Arcade | 9 mini game phản xạ | 45 chặng | chỉ kiểm định dạng | không | có (bản cũ, `upload*/`) | GameMonetize 09/10 chờ duyệt; CrazyGames từ chối 11/10 |
| Boba Sort | xếp màu | 120 | A* / 40 | thứ hai +20 | có | CrazyGames từ chối 11/10 |
| Car Jam Escape (bản 2) | trượt khối | 100 | BFS / 40 | chưa (cần thế giới 6, chữ "ALL 100 LEVELS") | có, bản 2 | bản 1 bị CrazyGames từ chối 11/10; bản 2 chưa nộp |
| Tile Trio | ghép ba ô | 120 | DFS / 40 | thứ hai +20 | có | CrazyGames từ chối 11/10 |
| One Line Fill | vẽ một nét | 120 | DFS / 40 | thứ hai +20 | CHƯA có | chưa nộp |

`web/pop-the-balloon` là bản thử, không đăng. Lý do CrazyGames từ chối cả 4: "overall quality… does not yet meet the expectations", không nêu lỗi kỹ thuật.

## Bộ khung và công cụ (giữ nguyên, chỉ mở rộng)

- Nguồn `web/<game>/index.src.html` + màn `levels/<game>.json` + `web/ads.js` → `tools/build.py` → `dist/<game>/<cổng>/index.html` + zip (cổng: gamemonetize, crazygames, gamedistribution, none).
- Bộ giải + sinh màn + hàng dự trữ: `tools/carjam.py`, `bobasort.py`, `tiletrio.py`, `oneline.py`; `taparcade.py` kiểm định dạng. `specs/<game>.json` ghi luật, `portal_ids`, mục an toàn.
- Kiểm thử: `tools/smoke_test.py` (Playwright: điện thoại dọc/ngang, máy tính, lỗi console, tải ≤ 5 giây; đo được 0,7–1,1 giây), `tools/test_ads.js` (SDK giả).
- `tools/run_daily.py`: kiểm màn → (thứ hai) chuyển 20 màn/game → bổ sung dự trữ → build → kiểm web → đăng itch.io nếu có trang → ghi `TRANG-THAI.md`, `metrics/history.json` → Discord (✅/🔴/⚪) + healthchecks.
- GitHub Actions: `daily.yml` 06:00 giờ VN (✅ 11, 12, 13/10), `weekly-selftest.yml` chủ nhật 20:00 + khi sửa `tools/`. Mới 13/10: `bao-discord.yml`.
- Khóa ở GitHub Secrets: `DISCORD_WEBHOOK`, `HC_PING`, `BUTLER_API_KEY`, `ITCH_USER`. Chưa có: Roblox.

## Tài khoản cổng

GameMonetize (có, 1 game chờ duyệt) · CrazyGames (có, 4 game bị từ chối) · GameDistribution (đăng ký 09/10, chờ thư) · itch.io (có khóa, chưa có trang game). Chưa có: Playgama, Yandex Games, Poki, GamePix, Roblox. Chi tiết: `CONG.md`.

## Tài liệu

`CLAUDE.md` (bộ nhớ + nhật ký quyết định) · `THEO-DOI.md` (kiểm kê, nộp cổng) · `NGHIEN-CUU.md` (yêu cầu cổng có nguồn, 11–12/10) · `HUONG-DAN-CHU.md` (việc chủ phải bấm) · `TRANG-THAI.md` (máy ghi).

## Chỗ hỏng / thiếu so với V3 (đã thành việc trong `VIEC.md`)

- Chưa game nào lên sóng → chưa có lượt chơi, doanh thu, số liệu.
- Chỉ 3 cổng có SDK trong `web/ads.js`; chưa có Playgama, Yandex, Poki, GamePix; chưa thử SDK thật cổng nào ngoài GameMonetize (Verify).
- Chưa có `phat-hanh/<cổng>/<game>/` (gói kèm ảnh bìa đúng cỡ + mô tả); One Line Fill chưa có ảnh bìa/video; ảnh bìa nằm ở `dist/` nên không lên git (máy đám mây không có).
- Chất lượng chung bị CrazyGames chê: mới nâng Car Jam (bản 2); 4 game kia chưa.
- Móc giữ chân: chưa game nào có thử thách ngày; chỉ Car Jam có xu + gara.
- Chưa có: `CHI-SO.md`, `VAN-HANH.md`, `ASSETS.md`, `NHAT-KY-CAI-TIEN.md`, `THU-NGHIEM.md`, bản Roblox, đa ngôn ngữ.
