import customtkinter as ctk
import threading
import os
import sys
from PIL import Image
from monitor_agent import MonitoringAgent
import time

# Configuration
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class MonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup Window
        self.title("Employee Monitor")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Initialize Agent
        self.agent = MonitoringAgent()
        self.is_monitoring = False
        
        # Load Images (optional, placeholder for now)
        # self.logo_image = ctk.CTkImage(Image.open("logo.png"), size=(26, 26))

        # Create Frames
        self.login_frame = ctk.CTkFrame(self)
        self.main_frame = ctk.CTkFrame(self)
        
        # Initialize UI
        self.show_login_screen()
        
        # Check for existing env vars to pre-fill
        if self.agent.email:
            self.email_entry.insert(0, self.agent.email)
        if self.agent.password:
            self.password_entry.insert(0, self.agent.password)

    def show_login_screen(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Clear frame
        for widget in self.login_frame.winfo_children():
            widget.destroy()
            
        # Header
        label = ctk.CTkLabel(self.login_frame, text="Welcome Back", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(40, 10))
        
        sublabel = ctk.CTkLabel(self.login_frame, text="Sign in to start monitoring", font=ctk.CTkFont(size=14))
        sublabel.pack(pady=(0, 30))
        
        # Inputs
        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Email Address", width=300)
        self.email_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=300)
        self.password_entry.pack(pady=10)
        
        # Login Button
        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", width=300, command=self.handle_login)
        self.login_btn.pack(pady=30)
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.status_label.pack(pady=10)

    def show_main_screen(self, employee_name):
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Clear frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Header
        welcome = ctk.CTkLabel(self.main_frame, text=f"Hi, {employee_name}", font=ctk.CTkFont(size=20, weight="bold"))
        welcome.pack(pady=(30, 5))
        
        role_label = ctk.CTkLabel(self.main_frame, text="Employee Monitoring Active", text_color="gray")
        role_label.pack(pady=(0, 40))
        
        # Status Indicator
        self.indicator = ctk.CTkLabel(self.main_frame, text="● Offline", font=ctk.CTkFont(size=16), text_color="gray")
        self.indicator.pack(pady=20)
        
        # Timer Label
        self.timer_label = ctk.CTkLabel(self.main_frame, text="00:00:00", font=ctk.CTkFont(size=40, weight="bold"))
        self.timer_label.pack(pady=10)
        
        # Control Button
        self.action_btn = ctk.CTkButton(self.main_frame, text="Start Monitoring", width=200, height=50,
                                      fg_color="green", hover_color="darkgreen",
                                      font=ctk.CTkFont(size=16, weight="bold"),
                                      command=self.toggle_monitoring)
        self.action_btn.pack(pady=40)
        
        # Logout
        logout_btn = ctk.CTkButton(self.main_frame, text="Logout", fg_color="transparent", border_width=1, 
                                 text_color=("gray10", "#DCE4EE"), command=self.logout)
        logout_btn.pack(side="bottom", pady=20)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            self.status_label.configure(text="Please enter email and password")
            return
            
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update()
        
        # Update agent credentials
        self.agent.email = email
        self.agent.password = password
        
        # Attempt login
        # We need to modify agent.login to return the name or user object if possible, 
        # but for now we'll assume it returns True/False and we can fetch profile
        if self.agent.login():
            # Get employee name (hacky way since agent.login prints it but doesn't return it easily)
            # We will fetch profile
            try:
                import requests
                res = requests.get(f"{self.agent.api_url}/employees/me", headers=self.agent.get_headers())
                if res.status_code == 200:
                    name = res.json().get('name', 'Employee')
                    self.show_main_screen(name)
                else:
                    self.show_main_screen("Employee")
            except:
                self.show_main_screen("Employee")
        else:
            self.status_label.configure(text="Invalid credentials or server error")
            self.login_btn.configure(state="normal", text="Login")

    def toggle_monitoring(self):
        if not self.is_monitoring:
            # START
            self.action_btn.configure(state="disabled")
            if self.agent.start_session():
                self.is_monitoring = True
                self.agent.running = True
                
                # Start threads
                self.agent.screenshot_thread = threading.Thread(target=self.agent.screenshot_loop, daemon=True)
                self.agent.activity_thread = threading.Thread(target=self.agent.activity_loop, daemon=True)
                self.agent.screenshot_thread.start()
                self.agent.activity_thread.start()
                
                # Update UI
                self.action_btn.configure(text="Stop Monitoring", fg_color="red", hover_color="darkred", state="normal")
                self.indicator.configure(text="● Monitoring Active", text_color="green")
                self.start_timer()
            else:
                self.action_btn.configure(state="normal")
                # Show error
        else:
            # STOP
            self.action_btn.configure(state="disabled")
            if self.agent.stop_session():
                self.is_monitoring = False
                self.agent.running = False
                
                # Update UI
                self.action_btn.configure(text="Start Monitoring", fg_color="green", hover_color="darkgreen", state="normal")
                self.indicator.configure(text="● Offline", text_color="gray")
                self.stop_timer()
            else:
                self.action_btn.configure(state="normal")

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.is_monitoring:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.configure(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            self.after(1000, self.update_timer)

    def stop_timer(self):
        pass

    def logout(self):
        if self.is_monitoring:
            self.toggle_monitoring()
        self.agent.access_token = None
        self.show_login_screen()

if __name__ == "__main__":
    app = MonitorApp()
    app.mainloop()
