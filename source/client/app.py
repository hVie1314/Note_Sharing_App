import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from utils.api import register, login, logout, upload_file, get_users, get_user_notes, delete_note, download_note, create_share_url
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
        self.username = None
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
            text="Note Sharing App",
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
        
        # Form fields
        fields = [
            ("Username", ""),
            ("Password", "*")
        ]

        entries = {}

        for field, show in fields:
            frame = tk.Frame(right_frame, bg='white')
            frame.pack(fill='x', pady=10)

            entry = ttk.Entry(
                frame,
                style='Custom.TEntry',
                show='',  # Ban đầu không có `show`
                width=30
            )
            entry.insert(0, field)  # Placeholder mặc định
            entry.pack(fill='x', padx=5)

            # Xóa placeholder khi focus
            def on_focus_in(event, field=field, show=show):
                if event.widget.get() == field:
                    event.widget.delete(0, 'end')
                    if show == "*":
                        event.widget.config(show='*')  # Ẩn ký tự nhập nếu là mật khẩu

            # Đặt lại placeholder khi mất focus
            def on_focus_out(event, field=field, show=show):
                if event.widget.get() == '':
                    event.widget.insert(0, field)
                    event.widget.config(show='')  # Xóa `show` nếu ô trống

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            entries[field] = entry

        def handle_login():
            username = entries["Username"].get()
            password = entries["Password"].get() 
            
            # Kiểm tra các trường không được để trống
            if username == "Username" or password == "Password":
                messagebox.showerror("Error", "Please fill in all the required information!")
                return
                
            # Gọi API đăng nhập
            response = login(username, password)
            if response.get("success"):
                self.token = response.get("token")
                self.username = username
                self.show_dashboard()
                self.load_notes()
            else:
                messagebox.showerror("Error", response.get("message", "Login failed"))

        # Remember me với style mới
        remember_frame = tk.Frame(right_frame, bg='white')
        remember_frame.pack(fill='x', pady=10)
        ttk.Checkbutton(remember_frame,
            text="Remember Me",
            style='Custom.TCheckbutton').pack(side='left')
        
        # Login button với màu Bootstrap primary
        login_btn = tk.Button(right_frame,
            text="Login",
            command=handle_login,
            bg="#103cbe", 
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
        except Exception as e:
            messagebox.showerror("Error", f"Error when logout: {str(e)}")
            
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

            entry = ttk.Entry(
                frame,
                style='Custom.TEntry',
                show='',  # Ban đầu không có `show`
                width=30
            )
            entry.insert(0, field)  # Placeholder mặc định
            entry.pack(fill='x', padx=5)

            # Xóa placeholder khi focus
            def on_focus_in(event, field=field, show=show):
                if event.widget.get() == field:
                    event.widget.delete(0, 'end')
                    if show == "*":
                        event.widget.config(show='*')  # Ẩn ký tự nhập nếu là mật khẩu

            # Đặt lại placeholder khi mất focus
            def on_focus_out(event, field=field, show=show):
                if event.widget.get() == '':
                    event.widget.insert(0, field)
                    event.widget.config(show='')  # Xóa `show` nếu ô trống

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            entries[field] = entry

        def handle_register():
            username = entries["Username"].get()
            password = entries["Password"].get() 
            confirm_password = entries["Confirm Password"].get()
            
            # Kiểm tra các trường không được để trống
            if username == "Username" or password == "Password" or confirm_password == "Confirm Password":
                messagebox.showerror("Error", "Please fill in all the required information!")
                return
                
            # Kiểm tra mật khẩu xác nhận
            if password != confirm_password:
                messagebox.showerror("Error", "Password confirmation does not match!")
                return
                
            # Gọi API đăng ký
            response = register(username, password)
            if response.get("success"):
                messagebox.showinfo("Success", "Register successfully!")
                self.show_login_page()
            else:
                messagebox.showerror("Error", response.get("message", "Fail to register!"))

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

    def handle_upload(self):
        try:
            file_path = filedialog.askopenfilename()
            if file_path:
                # Tạo dialog để nhập password
                password_dialog = tk.Toplevel(self.root)
                password_dialog.title("Enter Password")
                password_dialog.geometry("300x150")

                # Password entry
                tk.Label(password_dialog, 
                    text="Enter password to encrypt file:",
                    font=('Poppins', 10)).pack(pady=10)
                    
                password_entry = tk.Entry(password_dialog, show="*")
                password_entry.pack(pady=10)
                
                def submit():
                    password = password_entry.get()
                    if password:
                        # Upload với password
                        print("Uploading with password...")
                        response = upload_file(self.token, self.username, file_path, password)
                        print(f"Upload response: {response}")
                        
                        # Check success flag trong response
                        if response and (response.get("success") or "message" in response):
                            messagebox.showinfo("Success", "File uploaded successfully")
                            password_dialog.destroy()
                            self.load_notes()  # Refresh notes list
                        else:
                            error_msg = response.get("error", "Upload failed")
                            messagebox.showerror("Error", error_msg)
                            password_dialog.destroy()
                    
                # Upload button
                tk.Button(password_dialog,
                    text="Upload",
                    command=submit,
                    bg='#103cbe',
                    fg='white',
                    font=('Poppins', 10)).pack(pady=10)
                    
        except Exception as e:
            print(f"Upload error: {str(e)}")  # Debug log
            messagebox.showerror("Error", f"Upload failed: {str(e)}")
        
    # Hàm gửi tin nhắn
    def send_message(self):
        try:
            if not hasattr(self, 'selected_user'):
                messagebox.showwarning("Warning", "Please select a user to chat with")
                return
                
            message = self.message_entry.get().strip()
            if not message:
                return
                
            # TODO: Implement send message API call
            print(f"Sending message to {self.selected_user}: {message}")
            
            # Clear input after sending
            self.message_entry.delete(0, tk.END)
            
            # Add message to chat area (temporary)
            self.add_message_to_chat(self.username, message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def add_message_to_chat(self, sender, message):
        message_frame = tk.Frame(self.messages_frame, bg='white')
        message_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            message_frame,
            text=f"{sender}: {message}",
            font=('Poppins', 10),
            bg='white',
            anchor='w',
            wraplength=350
        ).pack(fill='x')

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()

        # Frame chính
        self.current_frame = tk.Frame(self.root, bg='#f0f2f5')  # Background màu xám nhạt
        self.current_frame.pack(fill="both", expand=True)

        # Taskbar
        taskbar = tk.Frame(self.current_frame, bg='#103cbe', height=50)
        taskbar.pack(fill='x')
        
        # Dashboard label
        tk.Label(taskbar, text="Dashboard", font=('Poppins', 14, 'bold'),
            bg='#103cbe', fg='white').pack(side='left', padx=20)
        
        # User info frame
        right_frame = tk.Frame(taskbar, bg='#103cbe')
        right_frame.pack(side='right', padx=20)
        tk.Label(right_frame, text=self.username, font=('Poppins', 12),
            bg='#103cbe', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(right_frame, text="Logout", font=('Poppins', 10),
            bg='white', fg='#103cbe', command=self.handle_logout).pack(side='left')

        # Container cho 3 phần chính
        content = tk.Frame(self.current_frame, bg='#f0f2f5')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        content.grid_columnconfigure(0, weight=2)  # Users list
        content.grid_columnconfigure(1, weight=3)  # Chat area 
        content.grid_columnconfigure(2, weight=2) # Chat area rộng gấp 2

        # Set chiều cao cố định cho container
        window_height = self.root.winfo_height()
        frame_height = window_height - 120  # Trừ đi chiều cao của taskbar và padding

        # 1. Users List với border và chiều cao cố định
        users_frame = tk.Frame(content, bg='white', width=300, height=frame_height,
            highlightbackground='#dee2e6',
            highlightthickness=1,
            relief='ridge',
            bd=0)
        users_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        users_frame.grid_propagate(False)  # Giữ kích thước cố định
        users_frame.pack_propagate(False)  # Ngăn co giãn theo nội dung

        # 2. Chat Area với border và chiều cao cố định
        chat_frame = tk.Frame(content, bg='white', width=500, height=frame_height,
            highlightbackground='#dee2e6',
            highlightthickness=1,
            relief='ridge',
            bd=0)
        chat_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        chat_frame.grid_propagate(False)

        # 3. Notes List với border và chiều cao cố định
        notes_frame = tk.Frame(content, bg='white', width=300, height=frame_height,
            highlightbackground='#dee2e6',
            highlightthickness=1,
            relief='ridge',
            bd=0)
        notes_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
        notes_frame.grid_propagate(False)
        notes_frame.pack_propagate(False)

        # Setup scrollable content
        self.setup_users_list(users_frame)
        self.setup_chat_area(chat_frame)
        self.setup_notes_list(notes_frame)
        self.load_notes()
        
    def setup_users_list(self, frame):
        # Header
        header = tk.Label(frame, text="Chat", font=('Poppins', 14, 'bold'),
            bg='white')
        header.pack(pady=10)

        # Scrollable container
        canvas = tk.Canvas(frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        users_list_frame = tk.Frame(canvas, bg='white')

        # Configure scrolling
        users_list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=users_list_frame, anchor="nw")

        # Get và hiển thị users
        response = get_users(self.token)
        if response.get("success"):
            users = response.get("users", [])
            for user in users:
                if user['username'] != self.username:
                    user_frame = tk.Frame(users_list_frame, bg='white', cursor='hand2')
                    user_frame.pack(fill='x', pady=2)
                    
                    # User label với hover effect
                    user_label = tk.Label(
                        user_frame,
                        text=user['username'],
                        font=('Poppins', 12),
                        bg='white',
                        anchor='w',
                        padx=20,
                        pady=10
                    )
                    user_label.pack(fill='x')
                    
                    # Bind click event
                    user_frame.bind('<Button-1>', 
                        lambda e, u=user['username']: self.select_user(u))
                    user_label.bind('<Button-1>', 
                        lambda e, u=user['username']: self.select_user(u))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_chat_area(self, frame):
        # Header
        header = tk.Frame(frame, bg='white', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Label cho tên user
        self.chat_user_label = tk.Label(
            header,
            text="Select a user to chat",
            font=('Poppins', 14, 'bold'),
            bg='white'
        )
        self.chat_user_label.pack(side='left', padx=20, pady=15)
        
        # Divider line dưới header
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(fill='x')
        
        # Messages area with scroll
        messages_canvas = tk.Canvas(frame, bg='white')
        messages_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=messages_canvas.yview)
        self.messages_frame = tk.Frame(messages_canvas, bg='white')

        self.messages_frame.bind(
            "<Configure>",
            lambda e: messages_canvas.configure(scrollregion=messages_canvas.bbox("all"))
        )

        messages_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", width=messages_canvas.winfo_reqwidth())
        messages_canvas.configure(yscrollcommand=messages_scrollbar.set)

        # Input area
        input_frame = tk.Frame(frame, bg='white', height=60)
        input_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        input_frame.pack_propagate(False)

        self.message_entry = tk.Entry(input_frame, 
            font=('Poppins', 12),
            bg='#f0f2f5')
        self.message_entry.pack(side='left', fill='both', expand=True, padx=(0, 10), pady=10)

        send_btn = tk.Button(input_frame,
            text="Send",
            bg='#103cbe',
            fg='white',
            font=('Poppins', 10),
            command=self.send_message)
        send_btn.pack(side='right', pady=10)

        # Pack messages area
        messages_canvas.pack(side="left", fill="both", expand=True)
        messages_scrollbar.pack(side="right", fill="y")

    def setup_notes_list(self, frame):
        # Header
        header = tk.Frame(frame, bg='white', height=50)
        header.pack(fill='x')
        tk.Label(header,
            text="My Notes",
            font=('Poppins', 14, 'bold'),
            bg='white').pack(pady=10)
        
        # Upload button
        upload_btn = tk.Button(frame,
            text="Upload Note",
            bg='#103cbe',
            fg='white',
            font=('Poppins', 10),
            width=20,
            command=self.handle_upload)
        upload_btn.pack(pady=10)
        
        # Notes list with scroll
        notes_canvas = tk.Canvas(frame, bg='white')
        notes_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=notes_canvas.yview)
        self.notes_frame = tk.Frame(notes_canvas, bg='white')

        self.notes_frame.bind(
            "<Configure>",
            lambda e: notes_canvas.configure(scrollregion=notes_canvas.bbox("all"))
        )

        notes_canvas.create_window((0, 0), window=self.notes_frame, anchor="nw")
        notes_canvas.configure(yscrollcommand=notes_scrollbar.set)

        # Load và hiển thị notes
        response = get_user_notes(self.token)
        if response.get("success"):
            notes = response.get("notes", [])
            for note in notes:
                note_frame = tk.Frame(self.notes_frame, bg='white')
                note_frame.pack(fill='x', pady=5, padx=10)
                
                # Note name
                tk.Label(note_frame,
                    text=note['filename'],
                    font=('Poppins', 11),
                    bg='white',
                    anchor='w').pack(side='left', fill='x', expand=True)
                    
                # Download button
                tk.Button(note_frame,
                    text="↓",
                    font=('Poppins', 11),
                    bg='#28a745',
                    fg='white',
                    command=lambda n=note: self.handle_download_note(n)).pack(side='right', padx=5)
                    
                # Delete button
                tk.Button(note_frame,
                    text="×",
                    font=('Poppins', 11),
                    bg='#dc3545',
                    fg='white',
                    command=lambda id=note['id']: self.handle_delete_note(id)).pack(side='right')

        notes_canvas.pack(side="left", fill="both", expand=True)
        notes_scrollbar.pack(side="right", fill="y")

    def select_user(self, username):
        try:
            # Cập nhật user được chọn
            self.selected_user = username
            
            # Cập nhật header của khung chat
            self.chat_user_label.configure(
                text=username,
                bg='#f8f9fa'
            )
            
            # Xóa tin nhắn cũ
            for widget in self.messages_frame.winfo_children():
                widget.destroy()
                
            # TODO: Load tin nhắn cũ
            # response = get_chat_messages(self.token, username)
            # if response.get("success"):
            #     messages = response.get("messages", [])
            #     for msg in messages:
            #         self.add_message_to_chat(msg["sender"], msg["content"])
                    
            # Hiện khung nhập tin nhắn
            self.message_entry.delete(0, tk.END)
            self.message_entry.focus()
            
        except Exception as e:
            print(f"Error selecting user: {str(e)}")

    def handle_delete_note(self, note_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            response = delete_note(self.token, note_id)
            if response.get("success"):
                messagebox.showinfo("Success", "Note deleted successfully")
                self.load_notes()  # Refresh list
            else:
                messagebox.showerror("Error", response.get("error", "Failed to delete note"))

    def handle_download_note(self, note):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(note['filename'])[1],
                initialfile=note['filename']
            )
            if file_path:
                response = download_note(self.token, note['id'], file_path)
                if response.get("success"):
                    messagebox.showinfo("Success", "Note downloaded successfully")
                else:
                    messagebox.showerror("Error", response.get("error", "Failed to download note"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download note: {str(e)}")

    def load_notes(self):
        try:
            # Xóa notes cũ
            for widget in self.notes_frame.winfo_children():
                widget.destroy()
                
            response = get_user_notes(self.token)
            if response.get("success"):
                notes = response.get("notes", [])
                for note in notes:
                    note_frame = tk.Frame(self.notes_frame, bg='white')
                    note_frame.pack(fill='x', pady=5, padx=10)
                    
                    # Note name
                    tk.Label(note_frame,
                        text=note['filename'],
                        font=('Poppins', 11),
                        bg='white',
                        anchor='w').pack(side='left', fill='x', expand=True)
                    
                    buttons_frame = tk.Frame(note_frame, bg='white')
                    buttons_frame.pack(side='right')
                    
                    # Share URL button 
                    tk.Button(buttons_frame,
                        text="🔗",
                        font=('Poppins', 11),
                        bg='#0d6efd',
                        fg='white',
                        command=lambda n=note: self.create_share_url(n)).pack(side='right', padx=2)
                    
                    # Download button
                    tk.Button(buttons_frame,
                        text="↓",
                        font=('Poppins', 11),
                        bg='#28a745',
                        fg='white',
                        command=lambda n=note: self.handle_download_note(n)).pack(side='right', padx=2)
                    
                    # Delete button
                    tk.Button(buttons_frame,
                        text="×",
                        font=('Poppins', 11),
                        bg='#dc3545',
                        fg='white',
                        command=lambda id=note['id']: self.handle_delete_note(id)).pack(side='right', padx=2)
                        
        except Exception as e:
            print(f"Error loading notes: {str(e)}")

    def create_share_url(self, note):
        try:
            # Tạo dialog chọn user
            select_user_dialog = tk.Toplevel(self.root)
            select_user_dialog.title("Select User")
            select_user_dialog.geometry("400x300")
            
            # Label hướng dẫn
            tk.Label(select_user_dialog,
                text="Chọn user để chia sẻ:",
                font=('Poppins', 10)).pack(pady=10)
            
            # Frame chứa danh sách users
            users_frame = tk.Frame(select_user_dialog)
            users_frame.pack(fill='both', expand=True, padx=10)
            
            # Lấy danh sách users
            response = get_users(self.token)
            selected_user = tk.StringVar()
            
            if response.get("success"):
                users = response.get("users", [])
                for user in users:
                    if user['username'] != self.username:  # Không hiển thị user hiện tại
                        tk.Radiobutton(users_frame,
                            text=user['username'],
                            variable=selected_user,
                            value=user['username'],
                            font=('Poppins', 10)).pack(anchor='w', pady=5)
            
            def next_step():
                user = selected_user.get()
                if not user:
                    messagebox.showwarning("Warning", "Vui lòng chọn user")
                    return
                    
                # Đóng dialog chọn user
                select_user_dialog.destroy()
                
                # Mở dialog nhập thời hạn
                expiry_dialog = tk.Toplevel(self.root)
                expiry_dialog.title("Set Expiry Date")
                expiry_dialog.geometry("400x200")
                
                tk.Label(expiry_dialog,
                    text=f"Nhập số ngày URL có hiệu lực cho user {user}:",
                    font=('Poppins', 10)).pack(pady=10)
                
                days_entry = tk.Entry(expiry_dialog)
                days_entry.pack(pady=10)
                
                def submit():
                    try:
                        days = int(days_entry.get())
                        if days <= 0:
                            messagebox.showerror("Error", "Số ngày phải lớn hơn 0")
                            return
                            
                        response = create_share_url(self.token, note['id'], days)
                        if response.get("success"):
                            url = response.get("url")
                            self.root.clipboard_clear()
                            self.root.clipboard_append(url)
                            messagebox.showinfo("Success", 
                                f"Share URL đã được tạo và copy vào clipboard!\nURL có hiệu lực trong {days} ngày\nĐã chia sẻ cho user: {user}\nURL: {url}")
                            expiry_dialog.destroy()
                        else:
                            messagebox.showerror("Error", 
                                response.get("error", "Không thể tạo share URL"))
                            expiry_dialog.destroy()
                            
                    except ValueError:
                        messagebox.showerror("Error", "Vui lòng nhập số ngày hợp lệ")
                
                tk.Button(expiry_dialog,
                    text="Tạo URL",
                    command=submit,
                    bg='#0d6efd',
                    fg='white',
                    font=('Poppins', 10)).pack(pady=10)
                    
            # Button next
            tk.Button(select_user_dialog,
                text="Tiếp tục",
                command=next_step,
                bg='#0d6efd',
                fg='white',
                font=('Poppins', 10)).pack(pady=20)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
if __name__ == "__main__":
    app = App()
    app.root.mainloop()
