import subprocess
import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import shutil
import ssl

class AbisFPSLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Abis-FPS : Tactical Warfare Launcher")
        self.root.geometry("850x520")
        self.root.config(bg="#0f131a")
        self.root.resizable(False, False)

        self.process = None
        self.current_state = "CHECKING"
        self.repo_files = []
        self.active_branch = "main"
        self.missing_files = []

        # --- ÜST BAŞLIK (HEADER) ---
        header_frame = tk.Frame(root, bg="#161c24", height=65)
        header_frame.pack(fill=tk.X, padx=12, pady=12)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(header_frame, text="ABIS-FPS", fg="#00f0ff", bg="#161c24", font=("Segoe UI", 16, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=20)

        sub_title = tk.Label(header_frame, text="// TACTICAL WARFARE", fg="#64748b", bg="#161c24", font=("Segoe UI", 10, "bold"))
        sub_title.pack(side=tk.LEFT, padx=0)

        version_lbl = tk.Label(header_frame, text="v1.0.0", fg="#94a3b8", bg="#161c24", font=("Segoe UI", 9, "bold"))
        version_lbl.pack(side=tk.RIGHT, padx=20)

        # --- ORTA İÇERİK ALANI ---
        content_frame = tk.Frame(root, bg="#0f131a")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=0)

        # SOL TARAF: Görsel / Banner Kartı
        left_panel = tk.Frame(content_frame, bg="#161c24", width=490)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 6), pady=(0, 12))
        left_panel.pack_propagate(False)

        # Oyun Banner Alanı (Şık Tasarım)
        banner_inner = tk.Frame(left_panel, bg="#11161d")
        banner_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        banner_lbl = tk.Label(banner_inner, text="ABIS-FPS\n\n[ SAVAŞ ALANI GÖRSELİ ]", fg="#38bdf8", bg="#11161d", font=("Segoe UI", 14, "bold"), justify=tk.CENTER)
        banner_lbl.pack(expand=True)

        # Alt Bilgi Kutusu
        info_box = tk.Frame(left_panel, bg="#161c24", height=50)
        info_box.pack(fill=tk.X, padx=12, pady=(0, 12))
        info_box.pack_propagate(False)

        desc_text = tk.Label(info_box, text="Sistem bütünlüğü ve dosya onarımı aktif.", fg="#94a3b8", bg="#161c24", font=("Segoe UI", 9))
        desc_text.pack(anchor="w", padx=5, pady=15)

        # SAĞ TARAF: Kontrol Paneli ve Dinamik Buton
        right_panel = tk.Frame(content_frame, bg="#161c24", width=324)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0), pady=(0, 12))
        right_panel.pack_propagate(False)

        right_title = tk.Label(right_panel, text="OYUN DURUMU", fg="#cbd5e1", bg="#161c24", font=("Segoe UI", 11, "bold"))
        right_title.pack(anchor="w", padx=24, pady=30)

        self.status_desc = tk.Label(right_panel, text="Bağlantı kontrol ediliyor...", fg="#f59e0b", bg="#161c24", font=("Segoe UI", 10))
        self.status_desc.pack(anchor="w", padx=24, pady=10)

        # TEK ANA BUTON (Dinamik ve Modern)
        self.main_btn = tk.Button(right_panel, text="KONTROL EDİLİYOR...", bg="#334155", fg="#ffffff", font=("Segoe UI", 12, "bold"), width=20, height=2, relief=tk.FLAT, cursor="hand2", command=self.on_main_button_click, state=tk.DISABLED)
        self.main_btn.pack(pady=40, padx=24)
        
        # Buton Hover Efektleri için binding
        self.main_btn.bind("<Enter>", self.on_btn_enter)
        self.main_btn.bind("<Leave>", self.on_btn_leave)

        # --- ALT BİLGİ ÇUBUĞU ---
        bottom_frame = tk.Frame(root, bg="#0f131a", height=35)
        bottom_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        bottom_frame.pack_propagate(False)

        footer_label = tk.Label(bottom_frame, text="GitHub: ES-ErenSakarya/AbisFPS", fg="#64748b", bg="#0f131a", font=("Segoe UI", 8, "bold"))
        footer_label.pack(side=tk.LEFT, padx=5)

        # Arka planda kontrolü başlat
        threading.Thread(target=self.check_game_status, daemon=True).start()

    def on_btn_enter(self, e):
        if self.main_btn['state'] == tk.NORMAL:
            self.main_btn.config(bg=self.btn_hover_color)

    def on_btn_leave(self, e):
        if self.main_btn['state'] == tk.NORMAL:
            self.main_btn.config(bg=self.btn_normal_color)

    def set_ui_state(self, state, text, btn_text, btn_color):
        self.current_state = state
        self.status_desc.config(text=text)
        self.main_btn.config(text=btn_text, bg=btn_color, state=tk.NORMAL)
        self.btn_normal_color = btn_color
        # Hover için hafif açık tonu hesapla
        self.btn_hover_color = "#2563eb" if "008" in btn_color or "256" in btn_color or btn_color == "#00b4d8" else "#16a34a"

    def get_ssl_context(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def check_game_status(self):
        success = False
        branches = ["main", "master"]
        headers = {'User-Agent': 'Mozilla/5.0'}
        ssl_ctx = self.get_ssl_context()

        for branch in branches:
            url = f"https://api.github.com/repos/ES-ErenSakarya/AbisFPS/git/trees/{branch}?recursive=1"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    if "tree" in data:
                        self.repo_files = []
                        for item in data["tree"]:
                            if item["type"] == "blob":
                                self.repo_files.append(item["path"])
                        self.active_branch = branch
                        success = True
                        break
            except Exception:
                continue

        if not success or not self.repo_files:
            self.missing_files = ["main.py"]
            self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", "Eksik dosyalar tespit edildi.", "EKSİK DOSYALARI İNDİR", "#00b4d8"))
            return

        self.missing_files = [f for f in self.repo_files if not os.path.exists(f)]

        if self.missing_files:
            self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", f"{len(self.missing_files)} adet dosya güncellenecek.", "EKSİK DOSYALARI İNDİR", "#00b4d8"))
        else:
            self.root.after(0, lambda: self.set_ui_state("PLAY", "Oyun oynamaya hazır.", "OYNA", "#10b981"))

    def on_main_button_click(self):
        if self.current_state == "DOWNLOAD":
            self.download_missing_files()
        elif self.current_state == "PLAY":
            self.start_game()

    def download_missing_files(self):
        self.main_btn.config(state=tk.DISABLED, bg="#334155")
        self.status_desc.config(text="Dosyalar indiriliyor...")
        
        def run_download():
            headers = {'User-Agent': 'Mozilla/5.0'}
            ssl_ctx = self.get_ssl_context()
            
            try:
                files_to_download = self.missing_files if self.missing_files else ["main.py"]

                for file_path in files_to_download:
                    success_file = False
                    branches_to_try = [self.active_branch, "main", "master"]
                    unique_branches = []
                    for b in branches_to_try:
                        if b not in unique_branches:
                            unique_branches.append(b)

                    last_err = None
                    for branch in unique_branches:
                        raw_url = f"https://raw.githubusercontent.com/ES-ErenSakarya/AbisFPS/{branch}/{file_path}"
                        try:
                            dir_name = os.path.dirname(file_path)
                            if dir_name and not os.path.exists(dir_name):
                                os.makedirs(dir_name, exist_ok=True)

                            req = urllib.request.Request(raw_url, headers=headers)
                            with urllib.request.urlopen(req, context=ssl_ctx, timeout=10) as response, open(file_path, 'wb') as out_file:
                                shutil.copyfileobj(response, out_file)
                            success_file = True
                            break
                        except Exception as e:
                            last_err = e
                            continue
                    
                    if not success_file:
                        raise Exception(f"{file_path} indirilemedi: {last_err}")

                self.root.after(0, lambda: self.set_ui_state("PLAY", "Güncelleme tamamlandı!", "OYNA", "#10b981"))
                messagebox.showinfo("Başarılı", "Tüm oyun dosyaları başarıyla güncellendi!")
            except Exception as e:
                err_msg = str(e)
                self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", "İndirme hatası oluştu.", "TEKRAR DENE", "#00b4d8"))
                messagebox.showerror("Hata", f"İndirme başarısız: {err_msg}")

        threading.Thread(target=run_download, daemon=True).start()

    def start_game(self):
        if self.process and self.process.poll() is None:
            self.status_desc.config(text="Oyun zaten çalışıyor!")
            return

        self.status_desc.config(text="Oyun başlatılıyor...")
        self.main_btn.config(state=tk.DISABLED, bg="#334155")

        def run_main():
            try:
                self.process = subprocess.Popen(
                    [sys.executable, "-u", "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                self.process.wait()
            except Exception as e:
                print(f"Hata: {e}")
            finally:
                self.root.after(0, lambda: self.set_ui_state("PLAY", "Oyun kapatıldı.", "OYNA", "#10b981"))

        threading.Thread(target=run_main, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AbisFPSLauncher(root)
    root.mainloop()