DEMO
<h1 align="center">[ĐỒ ÁN TRÍ TUỆ NHÂN TẠO]</h1>
<h1 align="center">TRÒ CHƠI PACMAN</h1>

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
* **Bước 1:** Tạo môi trường ảo
  ````bash
  python -m venv venv
  ````
* **Bước 2:** Kích hoạt môi trường ảo
  * _**Trên Windows:**_
   ````bash
  venv\Scripts\activate
  ````
* _**Trên macOS và Linux:**_
  ````bash
  source venv/bin/activate
  ````
* **Bước 3:** Cài đặt các thư viện cần thiết
  ````bash
  pip install -r requirements.txt
  ````
_3. HƯỚNG DẪN CHƠI_

**1. Bắt đầu trò chơi**

Chọn khu vực chơi: Khi khởi động trò chơi, bạn sẽ được yêu cầu nhập địa điểm mong muốn trên bản đồ Google Maps để làm sân chơi. Bạn có thể chọn bất kỳ khu vực nào trên thế giới bằng cách nhập tên địa điểm hoặc tọa độ cụ thể.​

**2. Điều khiển Pac-Man**

Di chuyển: Sử dụng các phím mũi tên trên bàn phím để điều khiển Pac-Man di chuyển lên, xuống, trái hoặc phải trên bản đồ.​

**3. Mục tiêu của trò chơi**

Thu thập vật phẩm: Di chuyển Pac-Man qua các con đường trên bản đồ để thu thập các vật phẩm (thường được hiển thị dưới dạng chấm nhỏ hoặc biểu tượng khác). Mỗi vật phẩm thu thập sẽ tăng điểm số của bạn.​

Tránh Ghosts: Các Ghosts sẽ di chuyển trên bản đồ và cố gắng bắt Pac-Man. Bạn cần né tránh chúng để không bị mất mạng.​

**4. Tính năng đặc biệt**

Power Pellets: Trong một số khu vực, sẽ có các Power Pellets đặc biệt. Khi Pac-Man ăn những vật phẩm này, Ghosts sẽ chuyển sang trạng thái "yếu" trong một khoảng thời gian ngắn, cho phép Pac-Man ăn chúng để ghi thêm điểm.​


**5. Kết thúc trò chơi**

Mất mạng: Nếu Pac-Man bị một Ghost bắt, bạn sẽ mất một mạng. Trò chơi kết thúc khi bạn hết số mạng cho phép.​

Hoàn thành màn chơi: Trò chơi có thể có nhiều màn chơi khác nhau dựa trên các khu vực bản đồ khác nhau. Hoàn thành một màn chơi bằng cách thu thập tất cả các vật phẩm và tránh các Ghosts.​

**6. Lưu ý**

Chiến lược chơi: Hãy quan sát kỹ đường đi của các Ghosts và lên kế hoạch di chuyển hợp lý để thu thập vật phẩm một cách an toàn. Sử dụng Power Pellets một cách chiến lược để tối đa hóa điểm số.​

Khám phá bản đồ: Vì trò chơi sử dụng bản đồ thực tế từ Google Maps, bạn có thể khám phá và chơi ở nhiều địa điểm khác nhau trên thế giới, mang lại trải nghiệm mới mẻ mỗi lần chơi.
***

THÔNG TIN LIÊN HỆ

Nếu bạn có bất kỳ câu hỏi hoặc cần hỗ trợ thêm về dự án, vui lòng liên hệ:

Tên: Nguyễn Đức Toàn

Email: ndtoande@gmail.com

Số điện thoại: + 84 825893064

GitHub: https://github.com/DUCTOANDE

Chúng tôi rất mong nhận được phản hồi và đóng góp từ bạn để cải thiện dự án này.