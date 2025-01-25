# Note Sharing App

## Giới thiệu
Note Sharing App là một ứng dụng cho phép người dùng đăng ký, đăng nhập, tải lên và chia sẻ các ghi chú dưới dạng file. Ứng dụng sử dụng mã hóa AES để đảm bảo tính bảo mật của các file khi tải lên và tải xuống. Người dùng có thể tạo các URL chia sẻ với thời hạn để chia sẻ ghi chú với người dùng khác.

## Danh sách thành viên
- 22120400 – Trần Anh Tú.
- 22120407 – Hoàng Ngọc Tuệ
- 22120427 – Nguyễn Mạnh Văn.
- 22120429 – Hoàng Quốc Việt.

## Yêu cầu hệ thống
- Python 3.8+
- PostgreSQL

## Cài đặt
### 1. Clone repository
```python
git clone https://github.com/hVie1314/Note_Sharing_App.git
cd Note_Sharing_App/source
```
### 2.Tạo virtual environment và cài đặt các gói cần thiết
```python
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3.Khởi tạo cơ sở dữ liệu và chạy server
```python
python server/run.py
```
### 4.Chạy client
```python
python client/app.py
```
