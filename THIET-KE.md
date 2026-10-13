# Ngôn ngữ thiết kế của xưởng (chủ dự án chọn 13/10/2026, dùng xuyên suốt)

Bản gốc: `thiet-ke/DESIGN_THINKING_FOR_CODER.md`, `thiet-ke/design-tokens.json`. Tệp này là cách áp dụng vào game. Ba từ: **KHOẢNG TRẮNG – NHỊP ĐIỆU – 1 ĐIỂM NHẤN**. Đẹp là bớt, không phải thêm.

## Token

| Thứ | Giá trị |
|---|---|
| Nền (60%) | `#FFFBF5` giấy ấm, hoặc `#0A0A0B` đêm – mỗi game chọn 1 |
| Card (30%) | `#FFFFFF` (nền sáng) / `#1A1A1A` (nền tối) |
| Nhấn (10%) | `#2B4A3B` rừng hoặc `#FF3B30` đỏ – mỗi game CHỈ 1 màu nhấn |
| Chữ | chính `#1A1A1A`, phụ `#8B7E6F`; viền `#E8E0D5` |
| Bo góc | card 16, khối lớn 24, nút pill 999; vật nằm trong card bo nhỏ hơn 8 |
| Khoảng cách | bội số 8: 8, 16, 24, 32, 48, 80 |
| Bóng | `0 2px 24px rgba(0,0,0,.06)` (lớn, mờ, nhẹ; không bóng đen gắt) |
| Headline | serif, weight 400, 32–56, line-height 0.95: `"Cormorant Garamond","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif` |
| Body | sans 14–15: `Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif` |
| Label | mono 11, CHỮ HOA, giãn 0.08em, màu `#8B7E6F`: `ui-monospace,Menlo,Consolas,monospace` |

Game không tải font từ ngoài (cổng cấm gọi ra ngoài), nên dùng chuỗi font hệ thống ở trên; khi nhúng font thì ghi giấy phép vào `ASSETS.md`.

## Luật

1. Trước mỗi màn hình trả lời 3 câu: 3 giây đầu thấy gì (đúng 1 thứ)? Mắt đi theo chữ Z thế nào? Cái gì xóa được?
2. Tối đa 3 màu chính, 2 font (+ mono cho nhãn), 3 cỡ chữ (nhãn 11–12, thân 14–15, headline 28–56). Headline không bao giờ đậm quá 700; mặc định 400.
3. Chỉ 1 thứ nổi bật mỗi màn: nút hành động chính là thứ duy nhất tô màu nhấn. Nút phụ: nền trắng, viền `#E8E0D5`.
4. Cùng loại thì cùng bo, cùng khoảng cách. Không có số lẻ kiểu 17, 19, 23.
5. Vật thể trong cảnh chơi (xe, cốc, quả) được có màu riêng để phân biệt, nhưng phẳng, ít bóng; khung giao diện quanh nó theo 60-30-10.
6. Thử cuối: thu nhỏ 25%, nhìn xa 2 m vẫn thấy bố cục và đúng 1 điểm nhấn.
7. Khi chỉ đổi giao diện: không đụng luật chơi, bộ giải, SDK quảng cáo, workflow.

## Theo nền tảng

- Cổng web gia đình (Poki, CrazyGames, Playgama…): sạch, 3 màu, nhìn 1 giây hiểu cách chơi → nền giấy ấm + nhấn rừng là mặc định.
- itch.io: nền đêm, chữ ít, ảnh lớn.
- Roblox: mọi thứ to, viền đen 3px, 1 nhân vật trung tâm, headline Fredoka One, nút pill.
- Bảng điều khiển/trang danh mục: nền `#0A0A0B`, card trắng bo 16, số liệu to, trạng thái xanh/đỏ rõ.

## Áp dụng

- Game mới: theo tệp này từ đầu. Mẫu tham chiếu: `web/merge-harvest/index.src.html` (các hằng `C`, `F`, hàm `card`, `pill`, `label`).
- Game cũ: đổi dần khi nâng chất lượng (menu, chọn màn, màn thắng, ảnh bìa); mỗi game một việc trong `VIEC.md`.
