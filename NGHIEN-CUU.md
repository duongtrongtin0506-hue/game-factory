# Nghiên cứu cổng game và nền tảng

Tra ngày 2026-10-11 bằng model nhẹ, chỉ ghi điều đọc được trên trang có nguồn. "Chưa xác minh" = không mở được trang gốc, phải tra lại trước khi dựa vào.

## CrazyGames
- Tối đa 250 MB, 1.500 tệp; tải ban đầu tối đa 50 MB (20 MB để lên trang chủ di động); tới lúc chơi được tối đa 20 giây; chỉ dùng đường dẫn tương đối. Nguồn: https://docs.crazygames.com/requirements/technical
- Phải chạy trên Chrome và Edge; hỗ trợ chuột, bàn phím, và cảm ứng nếu nhận di động; game máy tính nên nằm ngang. Nguồn: như trên
- PEGI 12; tiếng Anh bắt buộc; không tự làm nút toàn màn hình; không quảng bá chéo, không link cửa hàng ứng dụng trong game; chữ và hình đọc được ở devicePixelRatio 1. Nguồn: https://docs.crazygames.com/requirements/gameplay/
- Full Launch: bắt buộc SDK đầy đủ; người chơi mới vào chơi ngay hoặc sau tối đa 1 lần bấm. Nguồn: như trên
- Basic Launch: SDK không bắt buộc, không được chạy quảng cáo, chưa có tiền. Trang không nêu điều kiện lên Full Launch. Nguồn: https://docs.crazygames.com/requirements/intro/
- SDK v3 (tra lại 2026-10-12): nạp https://sdk.crazygames.com/crazygames-sdk-v3.js rồi `await window.CrazyGames.SDK.init()`. Nguồn: https://docs.crazygames.com/sdk/intro/
- Quảng cáo: `SDK.ad.requestAd('midgame' | 'rewarded', {adStarted, adFinished, adError})`; lỗi có dạng `{code, message}`, mã: `adsDisabledBasicLaunch`, `unfilled`, `adblock`, `adCooldown`, `other`. Basic Launch tắt quảng cáo (trả `adsDisabledBasicLaunch`). Khoảng cách midgame thường 3 phút, rewarded và preroll cũng tính vào. Nguồn: https://docs.crazygames.com/sdk/video-ads/
- `SDK.game.gameplayStart()`, `gameplayStop()`, `loadingStart()`, `loadingStop()`, `happytime()`. Nguồn: https://docs.crazygames.com/sdk/game/
- Trang chất lượng chỉ có hướng dẫn chung (tên/hình gây hiểu nhầm, nút dụ bấm quảng cáo, hướng dẫn đầu game không rõ), không liệt kê lý do từ chối. Nguồn: https://docs.crazygames.com/requirements/quality/ . Lý do cụ thể 4 game bị từ chối: chưa xác minh.

## GameMonetize
- Chia 45% doanh thu; trả qua PayPal hoặc USDT (ERC20); "Net 30". Nguồn: https://gamemonetize.com/developers
- SDK (tra 2026-10-12): `window.SDK_OPTIONS = {gameId, onEvent}`; sự kiện `SDK_READY`, `SDK_GAME_PAUSE` (quảng cáo sẵn sàng: dừng, tắt tiếng), `SDK_GAME_START` (xong: chơi tiếp); gọi `sdk.showBanner()`. Nguồn: https://gamemonetize.com/sdk . Tệp nạp https://api.gamemonetize.com/sdk.js . Nguồn: https://github.com/MonetizeGame/GameMonetize.com-SDK
- Dạng quảng cáo thưởng riêng: không trang nào nêu, chưa xác minh; `web/ads.js` dùng `showBanner()` cho cả hai loại. Ngưỡng rút tối thiểu: chưa xác minh trên trang công khai.

## GameDistribution
- `GD_OPTIONS`: `gameId` (bắt buộc), `onEvent`; nạp https://html5.api.gamedistribution.com/main.min.js một lần. Nguồn: https://github.com/GameDistribution/GD-HTML5/wiki/SDK-Implementation (trang tự ghi một phần đã cũ)
- Sự kiện: SDK_READY, SDK_ERROR, SDK_GAME_PAUSE (dừng và tắt tiếng), SDK_GAME_START (chơi tiếp), SDK_REWARDED_WATCH_COMPLETE. `gdsdk.showAd()` gọi từ thao tác của người chơi; `showBanner()` đã bỏ. Nguồn: như trên
- Quảng cáo thưởng (tra 2026-10-12): `gdsdk.showAd('rewarded')` trả Promise; nên `preloadAd('rewarded')` trước nhưng không bắt buộc; chỉ thưởng khi có `SDK_REWARDED_WATCH_COMPLETE`, `.catch` = không thưởng. Nguồn: https://github.com/GameDistribution/GD-HTML5/wiki/Rewarded-Ads . Tên sự kiện khi người chơi bỏ ngang, và `showAd()` thường có trả Promise không: chưa xác minh.
- Yêu cầu với nhà phát triển và tiêu chí chất lượng: chưa xác minh (trang chính không đọc được).

## itch.io
- `butler push <thư mục hoặc zip> user/game:kenh`; tên project viết thường. Sau lần đẩy đầu phải vào Edit game, đặt loại trang là HTML và đánh dấu kênh đó chơi trong trình duyệt. Nguồn: https://itch.io/docs/butler/pushing
- Đăng nhập butler trong CI bằng biến `BUTLER_API_KEY`. Nguồn: https://itch.io/docs/butler/login.html . Bản Linux tải ở https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default (tệp zip). Nguồn: https://itch.io/docs/butler/installing.html
- Đẩy vào trang game chưa tồn tại bị từ chối `itch.io API error (400): /wharf/builds: invalid game` (thử thật 2026-10-12): phải tạo trang trước. Kênh tên `html5` không tự gắn nhãn chơi trong trình duyệt; phải tích tay trên trang Edit game.
- itch.io có cho quảng cáo không, kiếm tiền thế nào: chưa xác minh.

## Roblox
- Đăng place: `POST https://apis.roblox.com/universes/v1/{universeId}/places/{placeId}/versions?versionType=Published`, header `x-api-key`, thân là tệp thô (`application/octet-stream` cho .rbxl, `application/xml` cho .rbxlx), trả về `versionNumber`. Khóa cần quyền universe-places Write cho đúng experience. Nguồn: https://create.roblox.com/docs/cloud/guides/usage-place-publishing
- Không cập nhật qua API được: EditableImage, EditableMesh, PartOperation, SurfaceAppearance, BaseWrap. Nguồn: như trên
- Vật phẩm ngẫu nhiên trả tiền phải công bố mọi kết quả và tỉ lệ. Nguồn: https://create.roblox.com/docs/en-us/production/monetization/paid-random-items . Dự án này không bán vật phẩm ngẫu nhiên.
- `rojo build -o game.rbxl` và giới hạn số lần gọi API: chưa xác minh trên trang chính thức.

## Game cùng thể loại (trượt xe / unblock)
- CrazyGames: Parking Panic https://crazygames.com/game/parking-panic ; Parking Jam (Famobi) https://www.crazygames.com/vn/game/parking-jam-dqq (về sau có rào chắn, chỗ hẹp).
- itch.io: Unblock Gridlock https://analogcasual.itch.io/unblockgridlock (hơn 9.000 màn, 4 mức khó); Parking Swipe https://17studio.itch.io/parking-swipe (3D Unity, hàng trăm màn).
- Roblox: không tìm thấy experience cùng thể loại.
- Khác biệt thấy được trên trang của họ so với Car Jam Escape: nhiều màn hơn hẳn, có chọn mức khó, có chướng ngại vật, đồ họa 3D hoặc do họa sĩ vẽ. Chưa đủ 5 game mỗi nền tảng và chưa xem được bảng xếp hạng hay nhiệm vụ ngày của họ: cần tra thêm.
