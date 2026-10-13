DỰ ÁN ③ GAME – KẾ HOẠCH V3 (NÂNG CẤP, KHÔNG LÀM LẠI TỪ ĐẦU)
Phạm vi: chỉ game. Kho GitHub game-factory; thư mục máy 2: C:\Users\Administrator\Desktop\GAME\web. Không YouTube, không bot trade. Tiếng Việt, tự làm, trả lời tôi 1 dòng.

0. GIỮ VÀ TẬN DỤNG MỌI THỨ ĐÃ CÓ
- Giữ nguyên: 5 game đã nộp cổng; Car Jam, Boba Sort, Tile Trio, One Line Fill; bộ khung chung, levels/*.json, bộ giải, content-queue, daily.yml, weekly-selftest, bước thứ hai tự chuyển 20 màn/game, báo Discord (⚪/🔴), HUONG-DAN-CHU.md, THEO-DOI.md, nhật ký quyết định.
- Đây là bản nâng cấp: đọc toàn bộ kho, ghi cái đã có vào HIEN-TRANG.md (1 trang), rồi gắn vào cấu trúc dưới. Không xóa, không viết lại cái đang chạy tốt; chỉ sửa chỗ hỏng và mở rộng.
- Lưu nguyên văn yêu cầu này thành KE-HOACH-V3.md. Ghi lên ĐẦU CLAUDE.md: "Kế hoạch hiện hành = KE-HOACH-V3.md. Bỏ mọi 'chờ X ngày' và mọi chia giai đoạn cũ."

1. TẦM NHÌN
Xây "xưởng game" sống 10–20 năm, giá trị hướng tới hàng triệu USD: danh mục nhiều game nhỏ có doanh thu đều + vài game ăn khách được đầu tư sâu; vận hành tự động; tài liệu đủ để bán/chuyển nhượng/cấp phép trong 48 giờ; doanh thu từ nhiều nguồn, không phụ thuộc 1 cổng hay 1 game.

2. CHIẾN LƯỢC 3 TẦNG (PHỄU)
- Tầng 1 – Game web HTML5 (thử ý tưởng nhanh, rẻ): mục tiêu 2 game mới/tuần, mỗi game sống trên ≥ 5 cổng, kiếm tiền quảng cáo.
- Tầng 2 – Game thắng (top 20% theo lượt chơi, thời gian chơi, tỷ lệ quay lại): thêm màn, tính năng, sự kiện mùa, nhiều ngôn ngữ; làm bản Roblox bán vật phẩm bằng Robux; xét thêm Telegram Mini Game, Facebook Instant Games nếu hợp.
- Tầng 3 – Thương hiệu (khi có game Roblox có doanh thu ổn 3 tháng): đề xuất bản di động/Steam, tên thương hiệu xưởng, trang web danh mục game. Chỉ đề xuất kèm số liệu, tôi duyệt.

3. NGHIÊN CỨU Ý TƯỞNG (vai nhà thiết kế game chuyên nghiệp)
- Mỗi thứ hai quét xu hướng, ghi nguồn vào XU-HUONG.md: bảng mới/đang lên trên các cổng trong CONG.md; Roblox Discover/Trending; top game casual/giải đố mới trên App Store, Google Play; kiểu game ngắn đang hot trên TikTok/YouTube Shorts; Google Trends; Reddit r/WebGames, r/incremental_games; mùa vụ/sự kiện sắp tới (làm game theo mùa trước 3–4 tuần).
- Mỗi tuần ≥ 5 ý tưởng vào Y-TUONG.md, chấm 1–5: nhu cầu, độ cạnh tranh (ít là tốt), làm được HTML5 ≤ 3 ngày, móc giữ chân (chơi lại, sưu tầm, thăng cấp, thử thách ngày), hợp quảng cáo thưởng/Robux, làm được bản Roblox. Mỗi ý tưởng: 1 câu mô tả, cơ chế cốt lõi, vì sao người chơi thích, game tham khảo (link).
- Ý tưởng điểm cao nhất → bản thử 1 ngày → Playwright + bộ giải tự chơi: hiểu luật ≤ 10 giây, có cảm giác "muốn thêm ván nữa". Đạt → VIEC.md làm game đủ; không đạt → ghi lý do bỏ.
- Chỉ học cơ chế; cấm sao chép tên, hình, nhân vật, nhạc của game khác.

4. DÂY CHUYỀN SẢN XUẤT (VIEC.md tự lập, tự xếp ưu tiên)
Ưu tiên: (1) lỗi làm game hỏng/không đăng được → (2) game bị cổng từ chối: đọc lý do, sửa, nộp lại hoặc nộp cổng khác → (3) game đang sống: Car Jam thế giới 6 + tự thêm màn, game có số liệu tốt → (4) game mới từ Y-TUONG.md → (5) đóng gói cho mọi cổng → (6) bản Roblox cho game thắng → (7) cải tiến bộ khung/công cụ.
Chuẩn mỗi game: hiểu luật ≤ 10 giây không cần chữ; tải ≤ 5 giây, dung lượng nhỏ; mượt trên điện thoại + máy tính (Playwright, không lỗi console); có móc giữ chân (sao, thăng cấp, sưu tầm, thử thách ngày); âm thanh bật/tắt; lưu tiến trình; tiếng Anh (thêm Việt, Nga, Tây Ban Nha, Bồ Đào Nha khi lên tầng 2); quảng cáo thưởng tự nguyện, quảng cáo giữa ván chỉ ở điểm dừng.
Mỗi game một cơ chế khác (cổng loại game nhân bản). Đồ họa tự tạo (AI vẽ; máy 2 có card GTX 1660 Super chạy AI vẽ cục bộ khi cần) hoặc tài nguyên giấy phép thương mại miễn phí, ghi nguồn + giấy phép vào ASSETS.md.

5. PHÁT HÀNH NHIỀU CỔNG
- CONG.md: mọi cổng tôi đã có tài khoản/đã nộp (đọc THEO-DOI.md, HUONG-DAN-CHU.md, lịch sử git) + đề xuất GameDistribution, Playgama, CrazyGames, GameMonetize, Yandex Games, Poki nếu chưa có. Mỗi cổng: link trang nộp, yêu cầu kỹ thuật, SDK quảng cáo (tra tài liệu mới nhất, ghi nguồn), game đã nộp, kết quả, lý do từ chối. itch.io không bắt buộc.
- Đóng gói sẵn MỌI game cho MỌI cổng vào phat-hanh/<cổng>/<game>/ (zip đúng chuẩn, SDK đúng cổng, ảnh bìa đúng kích thước, mô tả tiếng Anh).
- Nộp: cổng có API/CLI thì tự đẩy; còn lại ghi danh sách "CẦN NỘP" (game, cổng, đường dẫn zip, link trang nộp) ở đầu HUONG-DAN-CHU.md; tôi nộp 1 lần/tuần hoặc nhờ Claude Desktop có Chrome trên máy 2 nộp.

6. NGUỒN TIỀN
- Quảng cáo qua SDK cổng (chính).
- Roblox: game pass, developer product, vật phẩm trang trí; không bán lợi thế kiểu trả tiền mới thắng.
- Cấp phép không độc quyền cho trang web game/nhà tài trợ khi game có số liệu tốt: soạn đề xuất, tôi duyệt.
- Không cờ bạc, không hộp quà may rủi, không link ra ngoài, không thu dữ liệu cá nhân (người chơi Roblox phần lớn là trẻ em).

7. SỐ LIỆU VÀ QUYẾT ĐỊNH
- THEO-DOI.md game × cổng: trạng thái duyệt, lượt chơi, thời gian chơi, tỷ lệ quay lại, doanh thu. Số nào phải lấy từ bảng điều khiển cổng thì gom 1 danh sách "CẦN CHÉP SỐ" mỗi chủ nhật, tôi chép 1 lần.
- Game 30 ngày không có lượt chơi → ngừng đầu tư; top 20% → tầng 2. Cổng 60 ngày không đem lại gì → đề xuất bỏ.
- CHI-SO.md: doanh thu, chi phí (credit Claude, khóa AI, phí), số game sống, số cổng, tỷ lệ tự động.

8. CHẠY TỰ ĐỘNG TRÊN ĐÁM MÂY (máy 2 tắt vẫn chạy)
- Routine của Claude (tài khoản số 2) trên kho game-factory, 3 lượt/ngày 8:00, 14:00, 20:00 giờ Việt Nam, model Sonnet. Tạo bằng lệnh /schedule; không có thì mở claude.ai/code/routines và chỉ tôi đúng các ô cần điền. Nội dung routine: "Vận hành dự án game theo CLAUDE.md và KE-HOACH-V3.md: làm liên tục VIEC.md đến khi hết việc hoặc gần hết thời gian, không hỏi; việc chỉ chủ dự án làm được ghi vào đầu HUONG-DAN-CHU.md; commit + push sau mỗi việc; cuối lượt ghi 1 dòng TRANG-THAI.md."
- Kiểm Claude GitHub App có quyền kho game-factory; thiếu thì mở https://github.com/apps/claude/installations/select_target và nói tôi bấm chọn game-factory → Save.
- Giữ GitHub Actions: daily, weekly-selftest, chuyển màn thứ hai; thêm bao-discord.yml chạy khi push lên main, gửi dòng cuối TRANG-THAI.md qua secret DISCORD_WEBHOOK.
- Việc cần model mạnh (thiết kế bộ khung lớn, lỗi khó) ghi vào VIEC.md kèm nhãn [nặng]; routine bỏ qua, khi tôi mở khung chat thì làm.

9. HỌC VÀ CẢI TIẾN KHÔNG NGỪNG
- Ngày: hỏng gì sửa; ≥ 1 cải tiến nhỏ đo được; việc lặp ≥ 3 lần → script/Actions.
- Thứ hai: nghiên cứu xu hướng + 5 ý tưởng. Chủ nhật: 7 câu tự vấn vào NHAT-KY-CAI-TIEN.md (số nào tốt/xấu vì sao; khoản chi cắt được; việc còn làm tay; đối thủ làm gì mới; người chơi cần gì chưa có; điểm hỏng đơn lẻ và phương án B; cải tiến tuần trước ✅ giữ / ↩ gỡ).
- Tháng: soi 8 vai (người mua lại xưởng, cổng/người kiểm duyệt, đối thủ, luật sư, người chơi, kỹ sư vận hành, kế toán chi phí, nhà đầu tư); cập nhật công cụ/thư viện sau khi sao lưu; xếp hạng cổng theo tiền.
- Quý: radar công nghệ/thị trường (AI tạo hình/âm thanh mới, engine mới, nền tảng mới, chính sách cổng/Roblox); chọn ≤ 1 hướng thử nghiệm có giả thuyết, chỉ số, trần chi phí, hạn 14–30 ngày (THU-NGHIEM.md).
- Không chai lỳ: có cách rẻ hơn, nhanh hơn, tốt hơn thì thử nhỏ rồi thay. Quyết định lớn xem ≥ 3 nguồn/đối thủ, ghi nguồn.
- Bền: mã và dữ liệu trên GitHub, định dạng mở; VAN-HANH.md đủ để người khác tiếp quản; mỗi thành phần quan trọng (cổng, khóa AI, GitHub, Claude) có phương án B ghi sẵn.

10. CÁCH LÀM VIỆC VÀ BÁO CÁO
- Không hỏi xin phép, không giảng giải, không đưa tôi lệnh để chạy, không bảo tôi chờ. Lệnh PowerShell dùng ; không dùng &&.
- Việc chỉ tôi làm được → đầu HUONG-DAN-CHU.md theo 3 mục: CẦN NỘP, CẦN TẠO TÀI KHOẢN, CẦN CHÉP SỐ; mỗi việc 1 dòng có link. Discord nhắc 1 lần/ngày.
- Discord "Máy chủ của net24" kênh #game: mỗi lượt 1 dòng "🎮 Xong … · Gói chờ nộp N · Việc còn N"; lỗi thật 🔴 @here; nền tảng thiếu tài khoản ⚪; chủ nhật bảng game × cổng + ý tưởng tuần + 1 đề xuất. Không gửi vào #youtube, #trade, #dang-tiktok.
- Tiết kiệm credit: model nhẹ cho việc thường; tra cứu giao subagent nhẹ; không đọc lại tệp vừa sửa; lệnh chỉ in lỗi/kết quả.
- Bí mật: không ghi khóa vào tệp/commit; khóa ở GitHub Secrets hoặc .env (có trong .gitignore).

BƯỚC ĐẦU TIÊN NGAY BÂY GIỜ: lưu KE-HOACH-V3.md, viết HIEN-TRANG.md, sửa đầu CLAUDE.md, lập VIEC.md theo mục 4, CONG.md, Y-TUONG.md (5 ý tưởng đầu), thiết lập mục 8 và chạy thử routine 1 lần; sau đó làm liên tục VIEC.md. Xong phần thiết lập trả lời tôi 1 dòng.

Sau lần dán đầu, mỗi khung chỉ gõ: `làm tiếp` · Discord báo 🔴: `làm tiếp, sửa lỗi Discord báo`
