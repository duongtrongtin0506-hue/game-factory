# TƯ DUY NGÔN NGỮ THIẾT KẾ - DÀNH CHO AI CODER (Claude Code)

ĐỌC KỸ FILE NÀY TRƯỚC KHI CODE GIAO DIỆN. Mày code mạnh nhưng gu xấu, nên phải học tư duy này.

## 1. ĐẸP LÀ GÌ? (Không phải màu mè)

Đẹp = KHOẢNG TRẮNG + NHỊP ĐIỆU + 1 ĐIỂM NHẤN

- Khoảng trắng: Để thở. Padding 24px-48px-80px, đừng nhét sát nhau như xe buýt
- Nhịp điệu: Lặp lại. Bo góc 16px thì TẤT CẢ card đều 16px, không cái 16 cái 8
- 1 điểm nhấn: 1 trang chỉ có 1 thứ nổi bật. Đừng cho 5 nút đỏ, 3 màu neon

Xấu = SỢ TRỐNG + THAM MÀU + CHỮ NHỎ

---

## 2. 3 CÂU HỎI TRƯỚC KHI CODE 1 MÀN HÌNH

Hỏi 3 câu này, trả lời xong mới được code:

Q1: Người dùng nhìn 3 giây đầu thấy gì? (Phải là 1 thứ duy nhất: headline hoặc ảnh hero)
Q2: Mắt họ đi từ đâu đến đâu? (Z-pattern: trái trên -> phải trên -> trái dưới -> phải dưới)
Q3: Cái gì có thể XÓA mà không mất thông tin? (Xóa hết viền thừa, icon thừa, chữ thừa)

Nếu màn hình có >3 màu chính -> XÓA. >2 font -> XÓA. >4 cỡ chữ -> XÓA.

---

## 3. CÔNG THỨC TRIỆU ĐÔ (Áp dụng cho mọi thứ: Web, Roblox, Dashboard)

### Màu: 60-30-10
- 60% nền: #FFFBF5 (giấy ấm) hoặc #0A0A0B (đêm) - CHỌN 1
- 30% card: #FFFFFF hoặc #1A1A1A
- 10% nhấn: #2B4A3B (rừng) hoặc #FF3B30 (đỏ) - CHỈ 1 MÀU NHẤN

Đừng bao giờ dùng lime neon #E4FF7A làm nền lớn. Đó là màu của cảnh báo, không phải luxury.

### Bo góc: Càng đắt càng bo lớn
- Rẻ tiền: bo 4px
- Trung bình: bo 8px
- Triệu đô: bo 16px card, 24px hero, 999px nút
- Quy tắc: Ảnh và card chứa nó phải cùng bo, chênh 8px. VD: card bo 16, ảnh trong bo 8

### Chữ: 2 font là đủ
- Headline: Serif (Cormorant, Instrument) weight 400, size 32-56, line-height 0.95
- Body: Sans (Inter, Satoshi) weight 400-500, size 14-15
- Label: Mono 11px uppercase letter-spacing 0.08em color #8B7E6F
- ĐỪNG BAO GIỜ dùng >700 weight cho headline. Đắt tiền thì mỏng, rẻ tiền mới in đậm.

### Bóng: Mềm, không đen
- Xấu: box-shadow 0 4px 10px black
- Đẹp: box-shadow 0 2px 24px rgba(0,0,0,0.06) - bóng lớn, mờ, nhẹ

---

## 4. TƯ DUY THEO NỀN TẢNG (Mày đang làm Roblox, không phải web)

- **Roblox:** Trẻ con, nhìn từ xa. Mọi thứ phải to, viền đen 3px, 1 nhân vật trung tâm. Đừng làm UI nhỏ xíu như web admin.
- **itch.io:** Người lớn indie, thích nghệ. Nền tối, chữ ít, ảnh lớn, có chất.
- **Poki:** Gia đình, mẹ và con. Sạch, 3 màu, nhìn 1 giây hiểu cách chơi.
- **Dashboard Factory:** Mày làm cho chính mày nhìn. Nền tối, card sáng, số liệu to, trạng thái màu xanh/đỏ rõ.

---

## 5. QUY TẮC BẤT DI BẤT DỊCH KHI SỬA GIAO DIỆN

- CHỈ sửa CSS / class / màu / bo / padding
- KHÔNG sửa logic, API, GitHub Actions, Open Cloud, gameplay
- Nếu thấy 2 màu gần giống nhau (#E8E0D5 và #D6CFC2) -> GỘP thành 1
- Nếu thấy padding 17px, 19px, 23px -> SỬA thành 16, 24, 32 (bội số 8)
- Nếu thấy 5 cỡ chữ khác nhau -> GỘP thành 3: 12 label, 14 body, 28-32 headline

---

## 6. TEST CUỐI: NHÌN TỪ XA 2M

Thu nhỏ màn hình còn 25%, đứng xa 2m:
- Còn thấy rõ bố cục không? Nếu không -> thiếu khoảng trắng
- Còn thấy 1 điểm nhấn không? Nếu không -> tham màu
- Có thấy xấu không? Nếu có -> xóa bớt.

ĐẸP = BỚT, KHÔNG PHẢI THÊM.

---
HẾT. Nhớ 3 từ: KHOẢNG TRẮNG - NHỊP ĐIỆU - 1 ĐIỂM NHẤN.
Code theo tư duy này, gu tự đẹp.
