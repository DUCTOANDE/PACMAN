DEMO2
<h1 align="center">[ĐỒ ÁN TRÍ TUỆ NHÂN TẠO]</h1>
<h1 align="center">TRÒ CHƠI PACMAN SỬ DỤNG BẢN ĐỒ GOOGLE MAPS</h1>

**1. GIỚI THIỆU**
- Dự án này là một trò chơi được thiết kế dựa trên trò chơi Pac-Man, trong đó Pac-Man di chuyển trên một bản đồ thật từ Google Maps. Người chơi có thể chọn bất kỳ khu vực nào trên Google Maps để làm sân chơi và điều khiển Pac-Man né tránh các Ghosts được điều khiển bằng Al.

**2. NGUỒN GỐC CỦA Pac-Man**

- Pac-Man là một trò chơi arcade được phát triển bởi công ty Namco và phát hành vào năm 1980. Tác giả của trò chơi, Toru Iwatani, đã thiết kế Pac-Man với mục tiêu tạo ra một trò chơi thu hút cả nam và nữ, thay vì các trò chơi bắn súng phổ biến vào thời điểm đó. Trò chơi nhanh chóng trở thành một biểu tượng trong văn hóa đại chúng, với lối chơi đơn giản nhưng gây nghiện. Pac-Man được coi là một trong những trò chơi điện tử có ảnh hưởng nhất mọi thời đại.

**3. TÍNH NĂNG CHÍNH**

* Tích hợp Google Maps API: Sử dụng dữ liệu bản đồ thực tế để tạo môi trường chơi game.
* AI cho Ghosts: Áp dụng thuật toán A* hoặc BFS để điều khiển Ghosts.
* Điều khiển Pac-Man: Sử dụng bàn phím để điều khiển Pac-Man di chuyển trên bản đồ.
* Hệ thống điểm số: Tính điểm khi Pac-Man thu thập các vật phẩm.
* Tùy chỉnh khu vực chơi: Người chơi có thể nhập địa điểm mong muốn trên bản đồ.

**4. CÔNG NGHỆ SỬ DỤNG**
* Ngôn ngữ lập trình: Python
* Thư viện chính:
  * **pygame** để xây dựng giao diện game.
  * **Google Maps API** để hiển thị bản đồ.
  * **requests** để lấy dữ liệu bản đồ.
  * **numpy** để xử lý ma trận bản đồ.
  * **pathfinding** để tìm đường đi cho Ghosts.

***
**CÁCH CÀI ĐẶT VÀ CHẠY GAME**

_1. CÀI ĐẶT MÔI TRƯỜNG_
* **Bước 1:** Tạo môi trường ảo: 
`python -m venv venv`
* **Bước 2:** Kích hoạt môi trường ảo: 
  * _**Trên Windows:**_
`venv\Scripts\activate`
* _**Trên macOS và Linux:**_
`source venv/bin/activate`
* **Bước 3:** Cài đặt các thư viện cần thiết:
`pip install -r requirements.txt`
