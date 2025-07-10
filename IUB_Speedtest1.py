import customtkinter as ctk
from speedtest import Speedtest
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import json
from datetime import datetime
from PIL import Image
from customtkinter import CTkImage
import requests

# Appearance Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

speed_log = []

class IUBApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IUB – Internet Speed PRO")
        self.iconbitmap(r"D:\\Python work\\logo.png")  # Make sure the icon is .ico format
        self.geometry("900x850")
        self.configure(fg_color="black")

        # Fonts
        self.font_big = ("Arial Black", 36)
        self.font_mid = ("Arial", 18)
        self.font_small = ("Arial", 12)

        # University Logo
        try:
            logo_path = r"D:\\Python work\\logo.png"
            logo_image = CTkImage(Image.open(logo_path), size=(80, 80))
            self.logo = ctk.CTkLabel(self, text="", image=logo_image, fg_color="black")
            self.logo.pack(pady=(5, 0))
        except Exception as e:
            print("[Logo Error]", e)

        # Header
        ctk.CTkLabel(self, text="IUB", font=self.font_big, text_color="#0530A6").pack(pady=(5, 5))
        self.status = ctk.CTkLabel(self, text="Your Internet speed is:", font=self.font_mid, text_color="white")
        self.status.pack(pady=(0, 5))

        # Speed Display
        speed_frame = ctk.CTkFrame(self, fg_color="black")
        speed_frame.pack(pady=(0, 5))
        self.speed_label = ctk.CTkLabel(speed_frame, text="0.0", font=("Arial", 34, "bold"), text_color="white")
        self.speed_label.pack()
        self.unit_label = ctk.CTkLabel(speed_frame, text="Mbps", font=self.font_small, text_color="gray")
        self.unit_label.pack()

        # Details
        details_frame = ctk.CTkFrame(self, fg_color="black")
        details_frame.pack(fill="x", padx=10, pady=5)

        self.download = ctk.CTkLabel(details_frame, text="⬇️ Download: -- Mbps", font=self.font_small)
        self.download.pack(pady=2)
        self.upload = ctk.CTkLabel(details_frame, text="⬆️ Upload: -- Mbps", font=self.font_small)
        self.upload.pack(pady=2)
        self.latency = ctk.CTkLabel(details_frame, text="Latency: -- ms", font=self.font_small)
        self.latency.pack(pady=2)
        self.ip_info = ctk.CTkLabel(details_frame, text="IP: --", font=self.font_small)
        self.ip_info.pack(pady=2)
        self.location_info = ctk.CTkLabel(details_frame, text="Location: --", font=self.font_small)
        self.location_info.pack(pady=2)
        self.client_info = ctk.CTkLabel(details_frame, text="Client: --", font=self.font_small)
        self.client_info.pack(pady=2)

        # Start Test Button
        self.test_button = ctk.CTkButton(self, text="⟳ Start Speed Test", fg_color="#0530A6", hover_color="darkred",
                                         text_color="white", font=self.font_mid, command=self.run_speedtest_thread)
        self.test_button.pack(pady=20)

        # Graph Frame
        graph_frame = ctk.CTkFrame(self, fg_color='black')
        graph_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def run_speedtest_thread(self):
        threading.Thread(target=self.run_speedtest, daemon=True).start()

    def run_speedtest(self):
        try:
            self.speed_label.configure(text="...")
            self.status.configure(text="Testing...", text_color="yellow")
            st = Speedtest()
            st.get_best_server()
            d = round(st.download()/1_000_000, 2)
            u = round(st.upload()/1_000_000, 2)
            ping = int(st.results.ping)
            now = datetime.now().strftime("%H:%M:%S")

            self.speed_label.configure(text=str(d))
            self.download.configure(text=f"⬇️ Download: {d} Mbps")
            self.upload.configure(text=f"⬆️ Upload: {u} Mbps")
            self.latency.configure(text=f"Latency: {ping} ms")
            self.status.configure(text="✅ Test Complete", text_color="green")

            # IP Info
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                ip_data = requests.get("https://ipinfo.io/json", headers=headers).json()
                ip = ip_data.get("ip", "--")
                city = ip_data.get("city", "--")
                country = ip_data.get("country", "--")
                org = ip_data.get("org", "--")

                self.ip_info.configure(text=f"IP: {ip}")
                self.location_info.configure(text=f"Location: {city}, {country} - {org}")
                self.client_info.configure(text=f"Client: {city}, {country}")
            except:
                self.ip_info.configure(text="IP: 192.168.1.10")
                self.location_info.configure(text="Location: Lahore, PK")
                self.client_info.configure(text="Client: Bahawalpur, PK")
            # Logging
            record = {"time": now, "download": d, "upload": u, "latency": ping}
            speed_log.append(record)
            pd.DataFrame(speed_log).to_csv("speed_results.csv", index=False)
            with open("speed_results.json", "w") as f:
                json.dump(speed_log, f, indent=4)

            self.update_graph()
        except Exception as e:
            self.status.configure(text=f"❌ Error: {str(e)}", text_color="red")

    def update_graph(self):
        self.ax.clear()
        self.ax.set_facecolor("black")
        self.fig.patch.set_facecolor("black")

        times = [r['time'] for r in speed_log]
        downloads = [r['download'] for r in speed_log]
        uploads = [r['upload'] for r in speed_log]

        self.ax.plot(times, downloads, label="⬇️ Download", color="#1E90FF", linewidth=2, marker='o')
        self.ax.plot(times, uploads, label="⬆️ Upload", color="#00FF7F", linewidth=2, marker='s')

        self.ax.set_title("📶 Internet Speed Over Time", color="white")
        self.ax.set_xlabel("Time", color="white")
        self.ax.set_ylabel("Mbps", color="white")
        self.ax.legend(facecolor="black", labelcolor="white")
        self.ax.grid(color="#333333")
        self.fig.autofmt_xdate()
        self.canvas.draw()

if __name__ == "__main__":
    app = IUBApp()
    app.mainloop()

