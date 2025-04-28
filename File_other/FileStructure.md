
## **CẤU TRÚC THƯ MỤC VÀ FILE TRONG DỰ ÁN PAC-MAN**

### Thư mục assets: Thư mục này chứa tất cả các tài nguyên cần thiết cho game

**1. sound:** Chứa các file âm thanh
- **munch.wav:** Âm thanh khi Pac-Man ăn dot nhỏ
- **powerup.wav:** Âm thanh khi ăn power pellet
- **ghost_eaten.wav:** Âm thanh khi ăn ghost
- **death.wav:** Âm thanh khi mất mạng
- **backgroud.mp3:** Nhạc nền game

**2. player_images:** Chứa hình ảnh cho Pac-Man
- 1.png: Miệng mở 20% - Frame bắt đầu
- 2.png:  Miệng mở 45% - Frame trung gian
- 3.png:  Miệng mở 90% - Frame mở rộng nhất  
- 4.png:  Miệng mở 45% - Frame trung gian (Ngược lại)

_**Chi tiết frame animation:**_
- **Chu trình**: 1 → 2 → 3 → 4 → 1 (lặp lại)
- **Hướng**: Xoay theo hướng di chuyển (0°, 90°, 180°, 270°)

_**Cách sử dụng:**_
- Load các frame theo thứ tự
- Chuyển frame mỗi 0.1s (hoặc tùy FPS)
- Xoay sprite theo hướng di chuyển
- Dừng animation khi Pac-Man đứng yên
 
**3. ghost_images:** Chứa hình ảnh cho các ghost
- red.png: Blinky (ghost hồng)
- pink.png: Pinky (ghost hồng)
- blue.png: Inky (ghost xanh)
- orange.png: Clyde (ghost cam)
- powerup.png: ghost khi bị làm chậm
- dead.png: ghost khi bị ăn


### Thư mục game: Chứa source code
**1. constants.py:** Định nghĩa các hằng số dùng chung cho toàn bộ game
- Màu sắc(RGB value)
- Kích thước màn hình
- Tốc độ game (FPS)
- Đường dẫn đến các thư mục assets
- Các hướng di chuyển (lên, xuống, trái, phải)

**2. assets_manager.py:** Class quản lý tải và lưu trữ tất cả assets
**Có phương thức load_assets() để tải:**
- Hình ảnh player và ghost
- Âm thanh
- Font chữ
- Cung cấp interface để các module khác truy cập assets

**3. board.py:** Đại diện cho bản đồ của game
**Xử lý:**
- Vẽ mê cung, các chấm điểm
- Animation nhấm nháy của power pellet
- Kiểm tra vị trí các bức tường

**Animation là gì?**

Animation (hoạt hình) là quá trình tạo ra chuyển động bằng cách hiển thị liên tiếp một loạt hình ảnh tĩnh (frames). Khi các hình ảnh này được hiển thị nhanh chóng theo thứ tự, mắt người sẽ cảm nhận chúng như một chuyển động mượt mà.

**4. player.py:** Class điều khiển nhân vật PacMan
**Xử lý:**
- Di chuyển và animation 
- Kiểm tra hướng di chuyển hợp lệ
- Xử lý khi đi ra khỏi màn hình

**5. ghosts.py:** Class đại diện cho các ghost

**Mỗi ghost có Al riêng:**
- Blinky (đỏ): Đuổi thẳng
- Pinky (hồng): Đuổi phía trước
- Inky (xanh): Đuổi theo vector
- Clyde (Cam): Hành vi ngẫu nhiên

**Xử lý trạng thái**
- Bình thường
- Bị làm chậm (Khi Pac-Man ăn Power pellet)
- Bị ăn (Trở về chuồng)

**6. game_controller.py:** Class điều khiển luồng game chính

**Xử lý:**
- Điểm số, mạng, level
- Trạng thái game (đang chơi, gameover, chiến thắng)
- Power up và thời gian
- Va chạm và xử lý sự kiện
- Hiển thị HUD và thông báo 

**HUD (Heads-Up Display) là gì?**

HUD là giao diện hiển thị thông tin trong game mà không làm gián đoạn trải nghiệm của người chơi. Nó thường hiển thị các thông tin quan trọng như:
- Thanh máu (HP), năng lượng (MP, stamina).
- Điểm số, thời gian, mini-map.
- Vũ khí, đạn, tài nguyên.
- Nhiệm vụ hiện tại.

**7. init.py:** File rỗng để biến thư mục game thành Python package
Cho phép import các module từ package này

**8. menu.py:** 

**a. Main menu:**
- Play game: Bắt đầu game mới
- Options: Cài đặt game
- High scores: xem điểm cao
- Quit: thoát game

**b. Options menu:**
- Điều chỉnh âm thanh
- Điều chỉnh nhạc nền
- Chọn độ khó
- Quay lại menu chính

**c. Pause Menu:**
- Resume: Tiếp tục game
- Restart: Chơi lại
- Main Menu: Về menu chính
- Quit: Thoát game

**Xử lý:**
- Vẽ giao diện menu
- Xử lý input từ người chơi
- Chuyển đổi giữa các menu
- Animation và hiệu ứng menu
- Lưu/đọc cài đặt game

### file main.py: File chính khởi chạy game
Chứa hàm main() với vòng lặp game chính

**Công việc chính:**
- Khởi tạo pygame và màn hình
- Tạo các đối tượng game (assets, board, player, ghosts, controller)

**Vòng lặp game**
- Xử lý sự kiện
- Cập nhật trạng thái game
- Vẽ các thành phần lên màn hình
- Dọn dẹp khi thoát game


Phần mềm sài:
Capcut, printest, unscreen, figma


  