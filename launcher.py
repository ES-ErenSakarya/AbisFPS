import subprocess
import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import zipfile
import shutil
import ssl

class AbisFPSLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Abis-FPS Launcher")
        self.root.geometry("850x500")
        self.root.config(bg="#12161c")
        self.root.resizable(False, False)

        self.process = None
        self.current_state = "CHECKING"  # DOWNLOAD, PLAY

        # --- ÜST BAŞLIK ---
        header_frame = tk.Frame(root, bg="#181d24", height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(header_frame, text="ABIS-FPS : TACTICAL WARFARE", fg="#00d2ff", bg="#181d24", font=("Arial", 14, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=20)

        version_lbl = tk.Label(header_frame, text="ES-ErenSakarya/Abis-FPS", fg="#7a8b9e", bg="#181d24", font=("Arial", 9, "bold"))
        version_lbl.pack(side=tk.RIGHT, padx=20)

        # --- ORTA İÇERİK ---
        content_frame = tk.Frame(root, bg="#12161c")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # SOL TARAF: Görsel / Bilgi Alanı
        left_panel = tk.Frame(content_frame, bg="#181d24", width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_panel.pack_propagate(False)

        banner_lbl = tk.Label(left_panel, text="[ OYUN GÖRSELİ / BANNER ]\nAbis-FPS", fg="#ffffff", bg="#1a222d", font=("Arial", 12, "bold"), justify=tk.CENTER)
        banner_lbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_box = tk.Frame(left_panel, bg="#151b22", height=80)
        info_box.pack(fill=tk.X, padx=10, pady=(0, 10))
        info_box.pack_propagate(False)

        desc_text = tk.Label(info_box, text="Abis-FPS taktiksel nişancı oyununa hoş geldiniz. Eksik dosyalar otomatik olarak denetlenir ve onarılır.", fg="#a0acbe", bg="#151b22", font=("Arial", 9), justify=tk.LEFT, wraplength=460)
        desc_text.pack(anchor="w", padx=10, pady=10)

        # SAĞ TARAF: Tek Buton Kontrol Paneli
        right_panel = tk.Frame(content_frame, bg="#181d24", width=330)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_panel.pack_propagate(False)

        right_title = tk.Label(right_panel, text="OYUN DURUMU", fg="#8a9ba8", bg="#181d24", font=("Arial", 11, "bold"))
        right_title.pack(anchor="w", padx=20, pady=25)

        self.status_desc = tk.Label(right_panel, text="Dosyalar GitHub ile karşılaştırılıyor...", fg="#ffaa00", bg="#181d24", font=("Arial", 10))
        self.status_desc.pack(anchor="w", padx=20, pady=10)

        # TEK ANA BUTON (Dinamik: İNDİR / ONAR / OYNA)
        self.main_btn = tk.Button(right_panel, text="KONTROL EDİLİYOR...", bg="#555555", fg="white", font=("Arial", 12, "bold"), width=22, height=2, relief=tk.FLAT, command=self.on_main_button_click, state=tk.DISABLED)
        self.main_btn.pack(pady=30, padx=20)

        # --- ALT BİLGİ ÇUBUĞU ---
        bottom_frame = tk.Frame(root, bg="#181d24", height=40)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        bottom_frame.pack_propagate(False)

        footer_label = tk.Label(bottom_frame, text="GitHub: ES-ErenSakarya/Abis-FPS", fg="#7a8b9e", bg="#181d24", font=("Arial", 9))
        footer_label.pack(side=tk.LEFT, padx=15)

        # Arka planda dosya kontrolünü başlat
        threading.Thread(target=self.check_game_status, daemon=True).start()

    def set_ui_state(self, state, text, btn_text, btn_color):
        self.current_state = state
        self.status_desc.config(text=text)
        self.main_btn.config(text=btn_text, bg=btn_color, state=tk.NORMAL)

    def get_ssl_context(self):
        # Windows SSL sertifika engellerini aşmak için güvenli olmayan bağlam oluşturur
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def check_game_status(self):
        repo_files = []
        success = False
        
        api_urls = [
            "https://api.github.com/repos/ES-ErenSakarya/Abis-FPS/git/trees/main?recursive=1",
            "https://api.github.com/repos/ES-ErenSakarya/Abis-FPS/git/trees/master?recursive=1"
        ]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        ssl_ctx = self.get_ssl_context()

        for url in api_urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    if "tree" in data:
                        for item in data["tree"]:
                            if item["type"] == "blob":
                                repo_files.append(item["path"])
                        success = True
                        break
            except Exception:
                continue

        # Eğer API'ye ulaşılamazsa temel dosya kontrolü yap (main.py var mı)
        if not success or not repo_files:
            if not os.path.exists("main.py"):
                self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", "Oyun dosyaları eksik.", "İNDİR", "#007bff"))
            else:
                self.root.after(0, lambda: self.set_ui_state("PLAY", "Oyun oynamaya hazır.", "OYNA", "#28a745"))
            return

        missing_files = [f for f in repo_files if not os.path.exists(f)]

        if missing_files:
            self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", f"{len(missing_files)} adet eksik dosya bulundu!", "EKSİK DOSYALARI İNDİR", "#007bff"))
        else:
            self.root.after(0, lambda: self.set_ui_state("PLAY", "Tüm dosyalar tam ve güncel.", "OYNA", "#28a745"))

    def on_main_button_click(self):
        if self.current_state == "DOWNLOAD":
            self.download_game()
        elif self.current_state == "PLAY":
            self.start_game()

    def download_game(self):
        self.main_btn.config(state=tk.DISABLED, bg="#555555")
        self.status_desc.config(text="Dosyalar indiriliyor ve onarılıyor...")
        
        def run_download():
            zip_path = "repo.zip"
            extract_dir = "temp_extracted"
            success = False
            last_error = ""
            
            repo_zip_urls = [
                "https://codeload.github.com/ES-ErenSakarya/Abis-FPS/zip/refs/heads/main",
                "https://codeload.github.com/ES-ErenSakarya/Abis-FPS/zip/refs/heads/master"
            ]

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            ssl_ctx = self.get_ssl_context()

            try:
                for url in repo_zip_urls:
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as response, open(zip_path, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)
                        success = True
                        break
                    except Exception as e:
                        last_error = str(e)
                        continue
                
                if not success:
                    raise Exception(f"İndirme başarısız oldu. Hata: {last_error}")

                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                os.makedirs(extract_dir)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                subfolders = os.listdir(extract_dir)
                if subfolders:
                    source_dir = os.path.join(extract_dir, subfolders[0])
                    
                    for item in os.listdir(source_dir):
                        s = os.path.join(source_dir, item)
                        d = os.path.join(".", item)
                        if os.path.exists(d):
                            if os.path.isdir(d):
                                shutil.rmtree(d)
                            else:
                                os.remove(d)
                        shutil.move(s, d)
                
                shutil.rmtree(extract_dir)
                if os.path.exists(zip_path):
                    os.remove(zip_path)

                self.root.after(0, lambda: self.set_ui_state("PLAY", "Onarım tamamlandı!", "OYNA", "#28a745"))
                messagebox.showinfo("Başarılı", "Eksik dosyalar GitHub'dan başarıyla indirildi ve onarıldı!")
            except Exception as e:
                self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", "İndirme hatası oluştu.", "TEKRAR DENE", "#007bff"))
                messagebox.showerror("Hata", f"İndirme başarısız: {e}")

        threading.Thread(target=run_download, daemon=True).start()

    def start_game(self):
        if self.process and self.process.poll() is None:
            self.status_desc.config(text="Oyun zaten çalışıyor!")
            return

        self.status_desc.config(text="Oyun başlatılıyor...")
        self.main_btn.config(state=tk.DISABLED, bg="#555555")

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
                self.root.after(0, lambda: self.set_ui_state("PLAY", "Oyun kapatıldı.", "OYNA", "#28a745"))

        threading.Thread(target=run_main, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AbisFPSLauncher(root)
    root.mainloop()