import tkinter as tk
from tkinter import messagebox
from utils.api import register, login, logout

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Note Sharing App")
        self.set_window_position(800, 600)  # Kích thước lớn hơn

        self.current_frame = None
        self.token = None  # Lưu token sau khi đăng nhập
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

    def show_login_page(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.center_frame(self.current_frame)

        tk.Label(self.current_frame, text="Login", font=("Arial", 18)).grid(row=1, column=1, pady=20)

        tk.Label(self.current_frame, text="Username", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        username_entry = tk.Entry(self.current_frame, font=("Arial", 12), width=30)
        username_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.current_frame, text="Password", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        password_entry = tk.Entry(self.current_frame, font=("Arial", 12), show="*", width=30)
        password_entry.grid(row=3, column=1, padx=10, pady=5)

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

        tk.Button(self.current_frame, text="Login", command=handle_login, font=("Arial", 12), width=20).grid(row=4, column=1, pady=20)

        # Link to Register
        register_link = tk.Label(self.current_frame, text="Don't have an account?", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
        register_link.grid(row=5, column=1, pady=5)
        register_link.bind("<Button-1>", lambda e: self.show_register_page())

    def show_register_page(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.center_frame(self.current_frame)

        tk.Label(self.current_frame, text="Register", font=("Arial", 18)).grid(row=1, column=1, pady=20)

        tk.Label(self.current_frame, text="Username", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        username_entry = tk.Entry(self.current_frame, font=("Arial", 12), width=30)
        username_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.current_frame, text="Password", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        password_entry = tk.Entry(self.current_frame, font=("Arial", 12), show="*", width=30)
        password_entry.grid(row=3, column=1, padx=10, pady=5)

        def handle_register():
            username = username_entry.get()
            password = password_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            response = register(username, password)
            if response.get("success"):
                messagebox.showinfo("Success", "Registration successful, please login")
                self.show_login_page()
            else:
                messagebox.showerror("Error", response.get("message", "Registration failed"))

        tk.Button(self.current_frame, text="Register", command=handle_register, font=("Arial", 12), width=20).grid(row=4, column=1, pady=20)

        # Link to Login
        login_link = tk.Label(self.current_frame, text="Have an account?", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
        login_link.grid(row=5, column=1, pady=5)
        login_link.bind("<Button-1>", lambda e: self.show_login_page())

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.current_frame, text="Dashboard", font=("Arial", 18)).grid(row=0, columnspan=2, pady=20)

        def handle_logout():
            if self.token:
                response = logout(self.token)
                if response.get("success"):
                    self.token = None
                    self.show_login_page()
                else:
                    messagebox.showerror("Error", response.get("message", "Logout failed"))

        tk.Button(self.current_frame, text="Logout", command=handle_logout, font=("Arial", 12), width=20).grid(row=1, columnspan=2, pady=20)

if __name__ == "__main__":
    app = App()
    app.root.mainloop()
