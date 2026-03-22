import customtkinter as ctk
import threading
import time
import os
import json
import requests
import resend
from playwright.sync_api import sync_playwright

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

SETTINGS_FILE = "settings.json"

class BerkeleyMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Berkeley CAS Monitor")
        self.geometry("550x700")
        
        self.is_monitoring = False
        self.monitor_thread = None

        self.title_label = ctk.CTkLabel(self, text="Berkeley Status Monitor", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=10)

        self.cred_frame = ctk.CTkFrame(self)
        self.cred_frame.pack(pady=5, padx=20, fill="x")
        
        self.cred_label = ctk.CTkLabel(self.cred_frame, text="1. Berkeley Login", font=ctk.CTkFont(size=14, weight="bold"))
        self.cred_label.pack(pady=5)

        self.email_entry = ctk.CTkEntry(self.cred_frame, placeholder_text="Berkeley Email")
        self.email_entry.pack(pady=5, padx=20, fill="x")

        self.password_entry = ctk.CTkEntry(self.cred_frame, placeholder_text="Berkeley Password", show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")

        self.notif_frame = ctk.CTkFrame(self)
        self.notif_frame.pack(pady=5, padx=20, fill="x")
        
        self.notif_label = ctk.CTkLabel(self.notif_frame, text="2. Notifications (Requires At Least One)", font=ctk.CTkFont(size=14, weight="bold"))
        self.notif_label.pack(pady=5)

        self.discord_entry = ctk.CTkEntry(self.notif_frame, placeholder_text="Discord Webhook URL (Optional)")
        self.discord_entry.pack(pady=5, padx=20, fill="x")
        
        self.resend_key_entry = ctk.CTkEntry(self.notif_frame, placeholder_text="Resend.com API Key (Optional)", show="*")
        self.resend_key_entry.pack(pady=5, padx=20, fill="x")

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10, padx=20, fill="x")

        self.debug_var = ctk.BooleanVar(value=False)
        self.debug_checkbox = ctk.CTkCheckBox(self.action_frame, text="Enable Debug Mode (Show Browser)", variable=self.debug_var)
        self.debug_checkbox.pack(pady=5)

        self.start_button = ctk.CTkButton(self.action_frame, text="Start Monitoring", command=self.toggle_monitoring, fg_color="green", hover_color="darkgreen")
        self.start_button.pack(pady=5, fill="x")

        self.textbox = ctk.CTkTextbox(self, height=150)
        self.textbox.pack(pady=5, padx=20, fill="both", expand=True)
        self.textbox.configure(state="disabled")

        self.load_settings()
        self.log("Ready! I will save your settings automatically when you click Start.")

    def log(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def load_settings(self):
        self.hidden_interval = 1800 # Default to 30 mins
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    if data.get("email"): self.email_entry.insert(0, data["email"])
                    if data.get("password"): self.password_entry.insert(0, data["password"])
                    if data.get("discord_webhook"): self.discord_entry.insert(0, data["discord_webhook"])
                    if data.get("resend_key"): self.resend_key_entry.insert(0, data["resend_key"])
                    if data.get("_developer_interval"): self.hidden_interval = data.get("_developer_interval")
            except Exception as e:
                self.log(f"Failed to load settings: {e}")

    def save_settings(self):
        data = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
            except:
                pass
                
        data["email"] = self.email_entry.get().strip()
        data["password"] = self.password_entry.get().strip()
        data["discord_webhook"] = self.discord_entry.get().strip()
        data["resend_key"] = self.resend_key_entry.get().strip()
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        self.log("Settings saved!")

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.save_settings()
            self.start_monitoring()

    def start_monitoring(self):
        if not self.email_entry.get() or not self.password_entry.get():
            self.log("ERROR: Please enter Berkeley credentials.")
            return
            
        discord = self.discord_entry.get().strip()
        resend_key = self.resend_key_entry.get().strip()
        
        if not discord and not resend_key:
            self.log("ERROR: Please provide either a Discord webhook or a Resend key.")
            return
            
        self.is_monitoring = True
        self.start_button.configure(text="Stop Monitoring", fg_color="red", hover_color="darkred")
        
        self.log("Starting monitoring thread...")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.configure(text="Start Monitoring", fg_color="green", hover_color="darkgreen")
        self.log("Monitor stopping...")

    def send_notifications(self, title, message):
        webhook = self.discord_entry.get().strip()
        if webhook:
            try:
                requests.post(webhook, json={"content": f"**{title}**\n{message}"})
                self.log("Discord notification sent!")
            except Exception as e:
                self.log(f"Discord error: {e}")

        resend_key = self.resend_key_entry.get().strip()
        receiver = self.email_entry.get().strip() 
        
        if resend_key and receiver:
            resend.api_key = resend_key
            try:
                params = {
                    "from": "onboarding@resend.dev",
                    "to": receiver,
                    "subject": title,
                    "text": message
                }
                resend.Emails.send(params)
                self.log("Resend email sent successfully!")
            except Exception as e:
                self.log(f"Resend email failed: {e}")

    def check_page(self):
        URL = "https://auth.berkeley.edu/cas/clientredirect?client_name=Slate&service=https%3A%2F%2Fbcsweb.is.berkeley.edu%2Fpsp%2Fbcsprd%2F%3Fcmd%3Dstart"
        TARGET_TEXT = "Your account hasn't been created yet"

        try:
            with sync_playwright() as p:
                headless_mode = not self.debug_var.get()
                browser = p.chromium.launch(headless=headless_mode)
                
                context = browser.new_context()
                page = context.new_page()
                
                self.log("Loading CAS login url...")
                page.goto(URL)
                
                page.fill("input[name='username'], input[id='username'], input[type='email']", self.email_entry.get())
                page.fill("input[name='password'], input[id='password'], input[type='password']", self.password_entry.get())
                
                self.log("Clicking Login button...")
                page.locator("button.default[type='submit'], button:has-text('Login')").first.click()
                
                page.wait_for_timeout(3000)
                
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except:
                    pass
                
                page.wait_for_timeout(2000)

                if "auth.berkeley.edu/cas" in page.url or "Login" in page.title():
                    self.log("ERROR: Stuck on login page.")
                    context.close()
                    browser.close()
                    return False
                
                content = page.content()
                
                if TARGET_TEXT not in content:
                    self.log("Status CHANGED! Target text not found.")
                    self.send_notifications(
                        "Berkeley Account Status Updated!", 
                        f"@everyone The page updated and no longer shows the pending message!\n\nLink: {URL}"
                    )
                    context.close()
                    browser.close()
                    return True
                else:
                    self.log("Verified: Account still not created.")
                    context.close()
                    browser.close()
                    return False
                    
        except Exception as e:
            self.log(f"Browser error: {e}")
            return False

    def monitor_loop(self):
        check_interval = getattr(self, "hidden_interval", 1800)
        
        while self.is_monitoring:
            try:
                changed = self.check_page()
                if changed:
                    self.log("Monitor turning off permanently to avoid spam.")
                    self.after(0, self.stop_monitoring)
                    break
            except Exception as e:
                self.log(f"Check cycle failed: {e}")

            if not self.is_monitoring:
                break
                
            self.log(f"Sleeping for {max(1, check_interval // 60)} minute(s) before next check...")
            for _ in range(check_interval):
                if not self.is_monitoring:
                    break
                time.sleep(1)

if __name__ == "__main__":
    app = BerkeleyMonitorApp()
    app.mainloop()
