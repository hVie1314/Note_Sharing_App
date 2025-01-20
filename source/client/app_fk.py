import tkinter as tk
from tkinter import ttk, messagebox, font
from utils.api import register, login, logout
from PIL import Image, ImageTk
import os

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Note Sharing App")
        self.root.configure(bg='#ececec')
        self.set_window_position(930, 600)

        # Thêm font Poppins
        self.load_fonts()
        
        # Load image
        self.load_image()
        
        # Style cho ttk widgets với Poppins và màu Bootstrap
        self.style = ttk.Style()
        self.style.configure('Custom.TEntry', 
            padding=10,
            font=('Poppins', 12),
            background='#f8f9fa')
        self.style.configure('Custom.TButton',
            font=('Poppins', 12),
            padding=10)
        self.style.configure('Custom.TCheckbutton',
            background='white',
            font=('Poppins', 10))

        self.current_frame = None
        self.token = None
        self.show_login_page()

    def set_window_position(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def center_frame(self, frame):
        """Căn giữa nội dung trong frame."""
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

    def load_fonts(self):
        # Cấu hình font và màu mặc định
        self.root.option_add("*Font", "Poppins 10")
        self.root.option_add("*Background", "white")
        self.root.option_add("*Foreground", "#212529")

    def load_image(self):
        # Load và resize hình ảnh
        image_path = os.path.join(os.path.dirname(__file__), "images", "1.png")
        self.logo_image = Image.open(image_path)
        self.logo_image = self.logo_image.resize((250, 250))
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

    def show_login_page(self):
        if self.current_frame:
            self.current_frame.destroy()

        # Container chính với shadow
        self.current_frame = tk.Frame(self.root, bg='white',
            highlightbackground='#dee2e6',
            highlightthickness=1,
            relief='raised')
        self.current_frame.pack(pady=50, padx=50)

        # Left Box với brand section
        left_frame = tk.Frame(self.current_frame,
            bg='#103cbe',
            width=400,
            height=500)
        left_frame.pack(side='left', fill='both')

        # Thêm hình ảnh vào trước text
        image_label = tk.Label(
            left_frame,
            image=self.logo_photo,
            bg="#103cbe"
        )
        image_label.pack(pady=(50,20))
        
        tk.Label(left_frame,
            text="Be Verified",
            font=('Courier New', 24, 'bold'),
            fg="white",
            bg="#103cbe").pack(pady=10)

        tk.Label(left_frame,
            text="Join experienced Designers on this platform.",
            font=('Courier New', 10),
            fg="white",
            bg="#103cbe",
            wraplength=250).pack()

        # Right Box với form đăng nhập
        right_frame = tk.Frame(self.current_frame,
            bg='white',
            padx=40,
            pady=40)
        right_frame.pack(side='right', fill='both')

        # Headers 
        tk.Label(right_frame,
            text="Hello, Again",
            font=('Poppins', 24, 'bold'),
            bg="white").pack(anchor='w')
            
        tk.Label(right_frame,
            text="We are happy to have you back.",
            font=('Poppins', 12),
            fg="#6c757d",
            bg="white").pack(anchor='w', pady=(0,20))

        # Input fields with Bootstrap styling
        username_entry = ttk.Entry(right_frame,
            font=('Poppins', 12),
            width=30,
            style='Custom.TEntry')
        username_entry.pack(pady=10)
        username_entry.insert(0, "Username")
        
        password_entry = ttk.Entry(right_frame,
            font=('Poppins', 12),
            width=30,
            show="*",
            style='Custom.TEntry')
        password_entry.pack(pady=10)
        password_entry.insert(0, "Password")

        # Remember me với style mới
        remember_frame = tk.Frame(right_frame, bg='white')
        remember_frame.pack(fill='x', pady=10)
        ttk.Checkbutton(remember_frame,
            text="Remember Me",
            style='Custom.TCheckbutton').pack(side='left')

        def handle_login():
            username = username_entry.get()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            response = login(username, password)
            if response.get("success"):
                self.token = response.get("token")
                self.show_dashboard()
            else:
                messagebox.showerror("Error", response.get("message", "Login failed"))

        # Login button với màu Bootstrap primary
        login_btn = tk.Button(right_frame,
            text="Login",
            command=handle_login,
            bg="#0d6efd",
            fg="white", 
            font=('Poppins', 12, 'bold'),
            width=25,
            pady=10,
            relief='flat')
        login_btn.pack(pady=20)

        # Register link với màu link Bootstrap
        register_link = tk.Label(right_frame,
            text="Don't have account? Sign Up",
            font=('Poppins', 10),
            fg="#0d6efd",
            cursor="hand2",
            bg="white")
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.show_register_page())

    def handle_logout(self):
        try:
            if self.token:
                # Gọi API logout
                logout(self.token)
                self.token = None
                # Quay về trang login
                self.show_login_page()
                messagebox.showinfo("Success", "Đăng xuất thành công!")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi đăng xuất: {str(e)}")
            
    def show_register_page(self):
        if self.current_frame:
            self.current_frame.destroy()

        # Container chính 
        self.current_frame = tk.Frame(self.root, bg='white',
            highlightbackground='#dee2e6',
            highlightthickness=1,
            relief='raised')
        self.current_frame.pack(pady=50, padx=50)

        # Left Box
        left_frame = tk.Frame(self.current_frame,
            bg='#103cbe',
            width=400,
            height=500)
        left_frame.pack(side='left', fill='both')

        # Thêm hình ảnh
        image_label = tk.Label(
            left_frame,
            image=self.logo_photo,
            bg="#103cbe"
        )
        image_label.pack(pady=(50,20))

        # Text bên trái
        tk.Label(left_frame,
            text="Join Us Now",
            font=('Courier New', 24, 'bold'),
            fg="white",
            bg="#103cbe").pack(pady=10)
        
        tk.Label(left_frame,
            text="Create an account to access all features.",
            font=('Courier New', 10),
            fg="white",
            bg="#103cbe",
            wraplength=250).pack()

        # Right Box
        right_frame = tk.Frame(self.current_frame,
            bg='white',
            padx=40,
            pady=40)
        right_frame.pack(side='right', fill='both')

        # Headers
        tk.Label(right_frame,
            text="Sign Up",
            font=('Poppins', 24, 'bold'),
            bg="white").pack(anchor='w')
        
        tk.Label(right_frame,
            text="Create your account",
            font=('Poppins', 12),
            fg="#6c757d",
            bg="white").pack(anchor='w', pady=(0,20))

        # Form fields 
        fields = [
            ("Username", ""),
            ("Password", "*"),
            ("Confirm Password", "*")
        ]

        entries = {}
        for field, show in fields:
            frame = tk.Frame(right_frame, bg='white')
            frame.pack(fill='x', pady=10)
            
            entry = ttk.Entry(frame,
                style='Custom.TEntry',
                show=show,
                width=30)
            entry.insert(0, field)
            entry.pack(fill='x')
            
            # Xóa placeholder khi focus 
            def on_focus_in(event, field=field):
                if event.widget.get() == field:
                    event.widget.delete(0, 'end')
                    if 'password' in field.lower():
                        event.widget.config(show='*')
                        
            def on_focus_out(event, field=field):
                if event.widget.get() == '':
                    event.widget.insert(0, field)
                    if 'password' in field.lower():
                        event.widget.config(show='')
                        
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            entries[field] = entry

        def handle_register():
            username = entries["Username"].get()
            password = entries["Password"].get() 
            confirm_password = entries["Confirm Password"].get()
            
            # Kiểm tra các trường không được để trống
            if username == "Username" or password == "Password" or confirm_password == "Confirm Password":
                messagebox.showerror("Error", "Vui lòng điền đầy đủ thông tin!")
                return
                
            # Kiểm tra mật khẩu xác nhận
            if password != confirm_password:
                messagebox.showerror("Error", "Mật khẩu xác nhận không khớp!")
                return
                
            # Gọi API đăng ký
            response = register(username, password)
            if response.get("success"):
                messagebox.showinfo("Success", "Đăng ký thành công!")
                self.show_login_page()
            else:
                messagebox.showerror("Error", response.get("message", "Đăng ký thất bại!"))

        # Register button
        register_btn = tk.Button(right_frame,
            text="Register",
            command=handle_register,
            bg="#103cbe",
            fg="white", 
            font=('Poppins', 12, 'bold'),
            width=25,
            pady=10,
            relief='flat')
        register_btn.pack(pady=20)

        # Login link
        login_link = tk.Label(right_frame,
            text="Already have an account? Login",
            font=("Poppins", 10),
            fg="#0d6efd",
            cursor="hand2",
            bg="white")
        login_link.pack(pady=10)
        login_link.bind("<Button-1>", lambda e: self.show_login_page())

    def show_dashboard(self):
        # Update dashboard with new style
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root, bg='white')
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Dashboard header
        header_frame = tk.Frame(self.current_frame, bg='white')
        header_frame.pack(fill='x', pady=20)
        
        tk.Label(header_frame, 
                text="Dashboard", 
                font=("Arial", 24, "bold"),
                bg='white').pack(side='left', padx=20)

        # Logout button với style mới
        tk.Button(header_frame,
                 text="Logout",
                 command=self.handle_logout,
                 bg="#103cbe",
                 fg="white",
                 font=("Arial", 12)).pack(side='right', padx=20)

        # ...rest of dashboard code...

if __name__ == "__main__":
    app = App()
    app.root.mainloop()
