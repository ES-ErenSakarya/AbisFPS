import subprocess
import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox

# GitHub Reponuz
REPO_URL = "https://github.com/ES-ErenSakarya/Abis-FPS.git"

class AbisFPSLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Abis-FPS Launcher")
        self.root.geometry("850x500")
        self.root.config(bg="#12161c")
        self.root.resizable(False, False)

        self.process = None
        self.current_state = "CHECKING"  # DOWNLOAD, UPDATE, PLAY

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

        desc_text = tk.Label(info_box, text="Abis-FPS taktiksel nişancı oyununa hoş geldiniz. Tüm dosyalar ve güncellemeler GitHub reposundan yönetilir.", fg="#a0acbe", bg="#151b22", font=("Arial", 9), justify=tk.LEFT, wraplength=460)
        desc_text.pack(anchor="w", padx=10, pady=10)

        # SAĞ TARAF: Tek Buton Kontrol Paneli
        right_panel = tk.Frame(content_frame, bg="#181d24", width=330)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        right_panel.pack_propagate(False)

        right_title = tk.Label(right_panel, text="OYUN DURUMU", fg="#8a9ba8", bg="#181d24", font=("Arial", 11, "bold"))
        right_title.pack(anchor="w", padx=20, pady=25)

        self.status_desc = tk.Label(right_panel, text="Dosyalar kontrol ediliyor...", fg="#ffaa00", bg="#181d24", font=("Arial", 10))
        self.status_desc.pack(anchor="w", padx=20, pady=10)

        # TEK ANA BUTON (Dinamik: İNDİR / GÜNCELLE / OYNA)
        self.main_btn = tk.Button(right_panel, text="KONTROL EDİLİYOR...", bg="#555555", fg="white", font=("Arial", 12, "bold"), width=22, height=2, relief=tk.FLAT, command=self.on_main_button_click, state=tk.DISABLED)
        self.main_btn.pack(pady=30, padx=20)

        # --- ALT BİLGİ ÇUBUĞU ---
        bottom_frame = tk.Frame(root, bg="#181d24", height=40)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        bottom_frame.pack_propagate(False)

        footer_label = tk.Label(bottom_frame, text="GitHub: ES-ErenSakarya/Abis-FPS", fg="#7a8b9e", bg="#181d24", font=("Arial", 9))
        footer_label.pack(side=tk.LEFT, padx=15)

        # Arka planda GitHub durum kontrolünü başlat
        threading.Thread(target=self.check_game_status, daemon=True).start()

    def set_ui_state(self, state, text, btn_text, btn_color):
        self.current_state = state
        self.status_desc.config(text=text)
        self.main_btn.config(text=btn_text, bg=btn_color, state=tk.NORMAL)

    def check_game_status(self):
        # Eğer .git klasörü veya main.py yoksa indirilmesi gerekiyor
        if not os.path.exists(".git") or not os.path.exists("main.py"):
            self.set_ui_state("DOWNLOAD", "Oyun dosyaları bilgisayarda yok.", "İNDİR", "#007bff")
        else:
            try:
                subprocess.run(["git", "fetch"], capture_output=True, text=True, check=True)
                res = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True, check=True)
                if "Your branch is behind" in res.stdout:
                    self.set_ui_state("UPDATE", "Yeni bir güncelleme mevcut!", "GÜNCELLE", "#ff6600")
                else:
                    self.set_ui_state("PLAY", "Oyun güncel ve oynamaya hazır.", "OYNA", "#28a745")
            except Exception:
                self.set_ui_state("PLAY", "Dosyalar hazır.", "OYNA", "#28a745")

    def on_main_button_click(self):
        if self.current_state == "DOWNLOAD":
            self.download_game()
        elif self.current_state == "UPDATE":
            self.update_game()
        elif self.current_state == "PLAY":
            self.start_game()

    def download_game(self):
        self.main_btn.config(state=tk.DISABLED, bg="#555555")
        self.status_desc.config(text="Oyun indiriliyor...")
        
        def run_download():
            try:
                if not os.path.exists(".git"):
                    subprocess.run(["git", "init"], check=True)
                    subprocess.run(["git", "remote", "add", "origin", REPO_URL], capture_output=True)
                
                # main veya master branch'ini kontrol ederek çek
                try:
                    subprocess.run(["git", "pull", "origin", "main"], check=True)
                except subprocess.CalledProcessError:
                    subprocess.run(["git", "pull", "origin", "master"], check=True)

                self.root.after(0, lambda: self.set_ui_state("PLAY", "İndirme tamamlandı!", "OYNA", "#28a745"))
                messagebox.showinfo("Başarılı", "Oyun GitHub'dan başarıyla indirildi!")
            except Exception as e:
                self.root.after(0, lambda: self.set_ui_state("DOWNLOAD", "İndirme hatası oluştu.", "İNDİR", "#007bff"))
                messagebox.showerror("Hata", f"İndirme başarısız: {e}")

        threading.Thread(target=run_download, daemon=True).start()

    def update_game(self):
        self.main_btn.config(state=tk.DISABLED, bg="#555555")
        self.status_desc.config(text="Güncelleniyor...")

        def run_update():
            try:
                try:
                    subprocess.run(["git", "pull", "origin", "main"], check=True)
                except subprocess.CalledProcessError:
                    subprocess.run(["git", "pull", "origin", "master"], check=True)

                self.root.after(0, lambda: self.set_ui_state("PLAY", "Güncelleme tamamlandı!", "OYNA", "#28a745"))
                messagebox.showinfo("Başarılı", "Oyun en son sürüme güncellendi!")
            except Exception as e:
                self.root.after(0, lambda: self.set_ui_state("UPDATE", "Güncelleme hatası.", "GÜNCELLE", "#ff6600"))
                messagebox.showerror("Hata", f"Güncelleme başarısız: {e}")

        threading.Thread(target=run_update, daemon=True).start()

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