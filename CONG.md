# Cổng phát hành

Tra 13/10/2026 (kèm `NGHIEN-CUU.md` 11–12/10). Chỉ ghi điều đọc được trên trang có nguồn; "chưa xác minh" = phải tra lại trước khi dựa vào. Trước khi viết SDK cho cổng nào thì mở lại tài liệu cổng đó.

## Bảng tổng

| Cổng | Tài khoản | Đăng ký / nộp | Trong `web/ads.js` | Game đã nộp → kết quả | Chia tiền · rút | Tự đẩy được? | Ưu tiên |
|---|---|---|---|---|---|---|---|
| GameMonetize | có | https://gamemonetize.com/account/login.php | có (qua Verify) | Tap Arcade bản 5 trò 09/10 → chờ duyệt | 45% · PayPal/USDT, Net 30; ngưỡng chưa xác minh | không | 1 |
| CrazyGames | có | https://developer.crazygames.com/ | có | Tap Arcade, Boba Sort, Car Jam bản 1, Tile Trio 11/10 → cả 4 bị từ chối ("overall quality") | tỉ lệ không nêu · ngưỡng 100 EUR qua Tipalti, nhận khai cá nhân | không | 1 (Car Jam bản 2) |
| GameDistribution | đăng ký 09/10, chờ thư | https://developer.gamedistribution.com/ | có (chưa thử thật) | chưa | chưa xác minh (nguồn thứ cấp: 33%, 100 EUR) | không | 2 |
| Playgama | CHƯA | https://developer.playgama.com/ | có từ 13/10 (mới thử SDK giả) | chưa; 6 gói sẵn ở `phat-hanh/playgama/` | 50% (trên Playgama/iframe), 70–90% site đối tác · ngưỡng 100 USD, chuyển khoản | một phần: MCP tải bản lên sandbox, nộp duyệt vẫn bấm tay | 1 (một SDK ra nhiều cổng) |
| Yandex Games | CHƯA | bảng điều khiển trong https://yandex.com/dev/games/doc/en/ | CHƯA | chưa | tỉ lệ không nêu · ngưỡng 150 USD; cá nhân ở VN: chưa xác minh | không | 3 (cần tiếng Nga; có thể đi qua Playgama) |
| Poki | CHƯA | https://app.poki.dev/signin/ | CHƯA | chưa | 50/50, lượt trực tiếp 100% | không | KHÔNG nộp lúc này: mặc định đòi độc quyền web 5 năm, trái mục tiêu ≥ 5 cổng/game |
| GamePix | CHƯA | chưa xác minh (docs.gamepix.com không đọc được) | CHƯA | chưa | chưa xác minh | chưa xác minh | 3, tra lại |
| itch.io | có khóa, chưa có trang | https://itch.io/game/new | cổng `none` | chưa | không có quảng cáo cổng | có (butler, đã nằm trong `daily`) | không bắt buộc |
| Y8, Lagged, Newgrounds, Kongregate | CHƯA | chưa xác minh | – | – | – | – | tra lại tháng sau |

Khả năng cá nhân ở Việt Nam nhận tiền: chưa cổng nào ghi rõ (CrazyGames nhận khai cá nhân qua Tipalti; Playgama "tùy quốc gia"). Hỏi cổng khi game đầu tiên được duyệt.

## Chi tiết từng cổng

### GameMonetize
- Gói: zip có `index.html` ở gốc. Mỗi game cần GameId riêng (tạo game trên cổng mới có) → điền `portal_ids.gamemonetize` trong `specs/<game>.json`.
- SDK: nạp `https://api.gamemonetize.com/sdk.js`; `window.SDK_OPTIONS = {gameId, onEvent}`; sự kiện `SDK_READY`, `SDK_GAME_PAUSE` (dừng + tắt tiếng), `SDK_GAME_START`; gọi `sdk.showBanner()`. Không có quảng cáo thưởng riêng (chưa xác minh). Nguồn: https://github.com/MonetizeGame/GameMonetize.com-SDK · https://gamemonetize.com/developers

### CrazyGames
- Kỹ thuật: ≤ 250 MB, ≤ 1.500 tệp, tải đầu ≤ 50 MB (≤ 20 MB cho trang chủ di động), đường dẫn tương đối, tiếng Anh, PEGI 12, không link ngoài, không tự làm nút toàn màn hình. Nguồn: https://docs.crazygames.com/requirements/technical/
- Basic Launch: 7–21 ngày, quảng cáo tắt; kết thúc khi sống ≥ 7 ngày và đủ 500 lượt chơi hoặc hết 21 ngày; xét thời gian chơi trung bình, tỉ lệ vào chơi, giữ chân → đạt thì được mời Full Launch (bật tiền). Nguồn: https://docs.crazygames.com/
- SDK v3: `https://sdk.crazygames.com/crazygames-sdk-v3.js`, `await CrazyGames.SDK.init()`, `SDK.ad.requestAd('midgame'|'rewarded', {adStarted, adFinished, adError})`, `SDK.game.gameplayStart()/gameplayStop()/happytime()`. Nguồn: https://docs.crazygames.com/sdk/video-ads/
- Chất lượng: vào chơi nhanh, hướng dẫn bằng hình, mục tiêu rõ, hình/tiếng đồng đều, không dùng Escape/Ctrl+W làm phím game, hỗ trợ bàn phím AZERTY. Nguồn: https://docs.crazygames.com/requirements/quality/ → Car Jam đang dùng Esc để thoát: bỏ ở bản crazygames.
- Lý do từ chối 11/10: "The overall quality of the game does not yet meet the expectations of our platform". Bài bị từ chối không tải bản mới được, phải tạo bài nộp mới; ảnh bìa và video bị xóa mỗi lần đổi bản.
- Ảnh đã làm: bìa 1920x1080, 800x1200, 800x800 (+ bản lớn), video ngang 1920x1080 và dọc 1080x1620.

### GameDistribution
- SDK: nạp `https://html5.api.gamedistribution.com/main.min.js` một lần; `window.GD_OPTIONS = {gameId, onEvent}`; `SDK_GAME_PAUSE`/`SDK_GAME_START`/`SDK_REWARDED_WATCH_COMPLETE`; `gdsdk.showAd()` từ thao tác người chơi; `gdsdk.preloadAd('rewarded')` rồi `gdsdk.showAd('rewarded')`; phải bật cờ rewarded cho game trên trang nhà phát triển. Nguồn: https://github.com/GameDistribution/GD-HTML5/wiki/SDK-Implementation · https://github.com/GameDistribution/GD-HTML5/wiki/Rewarded-Ads
- Cỡ tệp, ảnh, tiêu chí duyệt: chưa xác minh.

### Playgama (Bridge)
- Gói: zip có `index.html` ở gốc, ≤ 300 MB, tên tệp chỉ ký tự Latin, kèm `playgama-bridge-config.json` cạnh `index.html`. Ảnh: 800x800, 1080x1920, 1920x1080 (PNG/JPEG ≤ 10 MB). Nguồn: https://wiki.playgama.com/playgama/submitting-a-game.md · https://wiki.playgama.com/playgama/mcp.md
- SDK: `https://bridge.playgama.com/v2/stable/playgama-bridge.js`; `bridge.initialize()` trước mọi lời gọi; `bridge.platform.sendMessage('game_ready')` khi chơi được; đọc `bridge.platform.language`; lưu tiến trình qua bridge storage (không dùng thẳng `localStorage`); nghe `PAUSE_STATE_CHANGED`, `AUDIO_STATE_CHANGED`. Giữa ván: `bridge.advertisement.showInterstitial()` (trạng thái loading/opened/closed/failed, cách nhau mặc định 60 giây). Thưởng: `bridge.advertisement.showRewarded()` và chỉ thưởng khi trạng thái `rewarded`. Nguồn: https://wiki.playgama.com/playgama/bridge-sdk/setup.md · https://wiki.playgama.com/playgama/bridge-sdk/api.md
- Duyệt 3–5 ngày làm việc; lên cổng đối tác tới 2 tuần. Cổng đối tác Yandex/VK đòi tiếng Nga; chưa có tiếng Nga thì bỏ chọn các cổng đó ở mục Distribution. Nguồn: https://wiki.playgama.com/playgama/faq/game-moderation.md · https://wiki.playgama.com/playgama/game-requirements/platform-specific-requirements.md
- Tiền: https://wiki.playgama.com/playgama/faq/payments-and-statistics.md
- Đã làm 13/10 trong `web/ads.js` (cổng `playgama`): nạp bridge, `initialize()`, `game_ready`, quảng cáo giữa ván `showInterstitial('level_completed')`, quảng cáo thưởng `showRewarded('reward')` chỉ thưởng khi trạng thái `rewarded`, tạm dừng theo `PAUSE_STATE_CHANGED`, và chép mọi lần ghi `localStorage` của khóa lưu game sang `bridge.storage` (máy mới thì khôi phục từ bridge rồi tải lại trang 1 lần). `tools/build.py` đặt `playgama-bridge-config.json` cạnh `index.html` trong zip.
- CHƯA làm / chưa xác minh: đọc `platform.language` (game chỉ có tiếng Anh); `AUDIO_STATE_CHANGED` (game đang tắt tiếng theo cờ tạm dừng); cấu trúc đầy đủ của tệp config (trang https://wiki.playgama.com/playgama/bridge-sdk/config.md chỉ nêu ví dụ, không nói trường nào bắt buộc); chưa chạy với SDK thật: phải dùng nút Test Game trên trang nhà phát triển sau khi có tài khoản.
- Nguồn 13/10: https://wiki.playgama.com/playgama/bridge-sdk/api/advertisement/interstitial.md · https://wiki.playgama.com/playgama/bridge-sdk/api/advertisement/rewarded.md · https://wiki.playgama.com/playgama/bridge-sdk/api/storage.md · https://wiki.playgama.com/playgama/bridge-sdk/api/platform.md

### Yandex Games
- Kỹ thuật: ≤ 100 MB giải nén, `index.html` ở gốc, tên tệp không dấu cách/chữ Nga; quảng cáo chỉ qua SDK; bắt buộc gọi `LoadingAPI.ready()`; tự nhận ngôn ngữ qua SDK; không đòi đăng nhập. Nguồn: https://yandex.com/dev/games/doc/en/concepts/requirements
- Ảnh: icon 512x512, bìa 800x470, ≥ 2 ảnh chụp mỗi nền tảng (cạnh dài 1280–2560), video ngang 16:9 MP4 ≤ 28 giây. Nguồn: https://yandex.com/dev/games/doc/en/console/add-new-game/draft.md
- SDK: `const ysdk = await YaGames.init()`; `ysdk.adv.showFullscreenAdv({callbacks:{onOpen,onClose,onError}})`; `ysdk.adv.showRewardedVideo({callbacks:{onOpen,onRewarded,onClose,onError}})`; `ysdk.features.LoadingAPI?.ready()`; `ysdk.features.GameplayAPI?.start()/stop()`. Đường dẫn thẻ script: chưa xác minh. Nguồn: https://yandex.com/dev/games/doc/en/sdk/sdk-adv.md · https://yandex.com/dev/games/doc/en/sdk/sdk-game-events.md
- Rút tiền: https://yandex.com/dev/games/doc/en/console/adv-monetization.md

### Poki
- SDK: `https://game-cdn.poki.com/scripts/v2/poki-sdk.js`; `PokiSDK.init()`, `gameLoadingFinished()`, `gameplayStart()/gameplayStop()`, `commercialBreak()`, `rewardedBreak()`. Nguồn: https://developers.poki.com/guide/sdk-html5
- Độc quyền web mặc định 5 năm; có dạng không độc quyền trả phí giấy phép một lần. Nguồn: https://developers.poki.com/guide/revenue-deal-types → chỉ xét cho một game riêng làm cho Poki, đề xuất kèm số liệu để chủ duyệt.

## Quy tắc chung mọi cổng (đã có trong `web/ads.js`)

Tắt tiếng + tạm dừng khi quảng cáo mở; chỉ thưởng khi cổng báo xem xong; quảng cáo giữa ván chỉ ở điểm dừng; không link ra ngoài.

## Thứ tự làm

1. Car Jam bản 2 → CrazyGames (bài nộp mới) và GameMonetize.
2. Playgama: gói đã có; chờ chủ tạo tài khoản → Test Game → Submit.
3. GameDistribution ngay khi tài khoản được kích hoạt.
4. Tiếng Nga + cổng `yandex` cho game đầu tiên có số liệu tốt.
5. Cổng 60 ngày không đem lại gì → đề xuất bỏ (mục 7 kế hoạch).
