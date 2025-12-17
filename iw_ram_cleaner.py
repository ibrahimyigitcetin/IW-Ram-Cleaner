import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import psutil  # type: ignore


# ====================== AYARLAR ======================
CRITICAL_PROCESSES = {
    "svchost.exe", "csrss.exe", "winlogon.exe",
    "lsass.exe", "smss.exe", "services.exe", "explorer.exe",
    "wininit.exe", "dwm.exe", "taskhostw.exe", "system", "registry"
}

MY_PID = os.getpid()
INFO_UPDATE_INTERVAL = 1000  # ms

# Renk paleti - Retro Night Club Edition
BG = "#0a0a0a"           # Derin siyah
BG_LAYER1 = "#1a1a1a"    # Katman 1
BG_LAYER2 = "#252525"    # Katman 2
FG = "#E0E0E0"
CYAN = "#00BFFF"         # Neon mavi
PINK = "#FF1493"         # Neon pembe
PURPLE = "#9D00FF"       # Neon mor
BAR_BG = "#2A2A2A"
RED = "#FF0055"          # Neon kırmızı
GRAY = "#707070"
GREEN = "#00FF7F"        # Neon yeşil
BORDER = "#FF1493"       # Pembe border


# ====================== YARDIMCI FONKSİYONLAR ======================
def safe_terminate(pid: int) -> bool:
    """Güvenli bir şekilde süreci sonlandırır."""
    try:
        p = psutil.Process(pid)
        p.terminate()
        _, alive = psutil.wait_procs([p], timeout=3)
        if alive:
            # Eğer hala yaşıyorsa, zorla kapat
            for proc in alive:
                try:
                    proc.kill()
                except:
                    pass
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
        return False


def get_all_processes():
    """Tüm süreçleri topla ve bellek kullanımına göre sırala."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            info = proc.info
            pid = info['pid']
            name = info['name'] or "[Bilinmeyen]"

            # Kendi sürecimizi işaretle
            if pid == MY_PID:
                name += " (Bu Uygulama - Koruma Aktif)"

            mem = info['memory_info']
            rss_mb = mem.rss / (1024 ** 2)
            vms_mb = mem.vms / (1024 ** 2)

            # Kritik süreç kontrolü
            is_critical = any(crit.lower() == name.lower() for crit in CRITICAL_PROCESSES)

            # Etikete kritik sistemler için uyarı simgesi ekle
            display_name = f"🚨 {name}" if is_critical else name

            processes.append((
                pid, 
                display_name, 
                f"{rss_mb:.1f}", 
                f"{vms_mb:.1f}", 
                "critical" if is_critical else "normal"
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # RSS'ye göre azalan sırada sırala
    processes.sort(key=lambda x: float(x[2]), reverse=True)
    return processes


def format_bytes(bytes_value):
    """Byte değerini okunabilir formata çevirir."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


# ====================== TOOLTIP SINIFI ======================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tip, text=self.text, background="#333333", 
            foreground=FG, relief="solid", borderwidth=1, 
            font=("Segoe UI", 9), padx=7, pady=4, justify="left"
        )
        label.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ====================== ANA UYGULAMA ======================
class RamCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IW Ram Cleaner")
        self.root.geometry("1100x750")
        self.root.minsize(1100, 750)
        self.root.configure(bg=BG)

        self.full_process_list = []
        self.last_net_io = psutil.net_io_counters()
        self.sort_column = "RSS (MB)"
        self.sort_reverse = True

        self.setup_styles()
        self.create_widgets()
        self.start_updates()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        # Genel Stil
        style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))

        # Treeview Stilleri
        style.configure(
            "Treeview", 
            background=BG_LAYER1, 
            foreground=FG, 
            fieldbackground=BG_LAYER1, 
            rowheight=26,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading", 
            background=BG_LAYER2, 
            foreground=PINK, 
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            borderwidth=0
        )
        style.map(
            "Treeview", 
            background=[("selected", PINK)], 
            foreground=[("selected", BG)]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", PURPLE)]
        )

        # Progressbar renkleri
        for color_name, color_value in [("Pink", PINK), ("Cyan", CYAN), 
                                         ("Yellow", "#FFD700"), ("Red", RED), 
                                         ("Green", GREEN)]:
            style.configure(
                f"{color_name}.Horizontal.TProgressbar", 
                background=color_value, 
                troughcolor=BAR_BG, 
                thickness=14
            )

        # Buton Stili
        style.configure(
            "TButton", 
            foreground=BG, 
            background=CYAN, 
            font=("Segoe UI", 11, "bold"), 
            borderwidth=0, 
            relief="flat",
            padding=10
        )
        style.map(
            "TButton", 
            background=[("active", PINK), ("!disabled", CYAN)], 
            foreground=[("active", BG)]
        )

    def create_widgets(self):
        # === ÜST KISIM - Başlık ve Göstergeler ===
        top_frame = tk.Frame(self.root, bg=BG)
        top_frame.pack(padx=20, pady=(15, 10), fill="x")

        # Başlık Container (Katmanlı tasarım)
        header_container = tk.Frame(top_frame, bg=BG_LAYER1, relief="flat", bd=2, highlightthickness=2, highlightbackground=BORDER)
        header_container.pack(fill="x", pady=(0, 10))

        # Başlık
        tk.Label(
            header_container, text="IW RAM CLEANER", 
            font=("Segoe UI", 22, "bold"), fg=PINK, bg=BG_LAYER1
        ).pack(pady=(8, 2))
        tk.Label(
            header_container, text="Retro Night Club Edition", 
            font=("Segoe UI", 9), fg=CYAN, bg=BG_LAYER1
        ).pack(pady=(0, 8))

        # RAM Bilgi Container
        info_container = tk.Frame(top_frame, bg=BG_LAYER2, relief="flat", bd=1, highlightthickness=1, highlightbackground=PURPLE)
        info_container.pack(fill="x", pady=(0, 10))
        
        self.ram_info_label = tk.Label(
            info_container, text="", font=("Consolas", 9), fg=GRAY, bg=BG_LAYER2
        )
        self.ram_info_label.pack(pady=6, padx=10)

        # Göstergeler Frame 
        gauges_outer = tk.Frame(top_frame, bg=BG_LAYER1, relief="flat", highlightthickness=2, highlightbackground=BORDER)
        gauges_outer.pack(fill="x", pady=(0, 10))
        
        gauges_frame = tk.Frame(gauges_outer, bg=BG_LAYER1)
        gauges_frame.pack(fill="x", padx=8, pady=8)

        gauges_frame.grid_columnconfigure(0, weight=1, minsize=100)
        gauges_frame.grid_columnconfigure(1, weight=4)

        # CPU
        self.cpu_label, self.cpu_bar = self.create_gauge(gauges_frame, "CPU", 0, "Pink")
        # RAM
        self.ram_label, self.ram_bar = self.create_gauge(gauges_frame, "RAM", 1, "Cyan")
        # Disk
        self.disk_label, self.disk_bar = self.create_gauge(gauges_frame, "Disk", 2, "Yellow")
        # Ağ
        self.create_net_gauge(gauges_frame, 3)

        # === KONTROL PANELİ (Arama + İstatistik) ===
        control_outer = tk.Frame(self.root, bg=BG_LAYER2, relief="flat", highlightthickness=1, highlightbackground=PURPLE)
        control_outer.pack(padx=20, pady=(0, 8), fill="x")
        
        control_frame = tk.Frame(control_outer, bg=BG_LAYER2)
        control_frame.pack(fill="x", padx=10, pady=6)

        # Sol taraf - Arama
        search_left = tk.Frame(control_frame, bg=BG_LAYER2)
        search_left.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            search_left, text="🔍 Arama:", fg=CYAN, bg=BG_LAYER2, 
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry_frame = tk.Frame(search_left, bg=PURPLE, bd=1)
        search_entry_frame.pack(side="left", fill="x", expand=True)
        
        self.search_entry = tk.Entry(
            search_entry_frame, textvariable=self.search_var, fg=CYAN, bg=BG_LAYER1,
            insertbackground=PINK, relief="flat", font=("Segoe UI", 9), bd=0
        )
        self.search_entry.pack(fill="both", expand=True, padx=1, pady=1, ipady=3)
        self.search_var.trace_add("write", self.apply_filter)

        # Sağ taraf - İstatistik
        self.stats_label = tk.Label(
            control_frame, text="Süreç Sayısı: 0", fg=GREEN, bg=BG_LAYER2, 
            font=("Segoe UI", 9, "bold")
        )
        self.stats_label.pack(side="right", padx=(10, 0))

        # === TREEVIEW CONTAINER ===
        tree_outer = tk.Frame(self.root, bg=BG_LAYER1, relief="flat", highlightthickness=2, highlightbackground=BORDER)
        tree_outer.pack(padx=20, pady=(0, 8), fill="both", expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg=BG_LAYER1)
        tree_frame.pack(fill="both", expand=True, padx=6, pady=6)

        columns = ("PID", "Uygulama Adı", "RSS (MB)", "VMS (MB)")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="extended"
        )
        
        # Sütun yapılandırması
        for col in columns:
            is_numeric = col in ["RSS (MB)", "VMS (MB)"]
            self.tree.heading(
                col, text=col, 
                command=lambda c=col, n=is_numeric: self.sort_treeview(c, n)
            )
        
        self.tree.column("PID", width=70, anchor="center")
        self.tree.column("Uygulama Adı", width=400, anchor="w")
        self.tree.column("RSS (MB)", width=110, anchor="e")
        self.tree.column("VMS (MB)", width=110, anchor="e")

        # Tag yapılandırması
        self.tree.tag_configure("critical", foreground=RED, background="#1a1a1a", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("normal", foreground=FG)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === BUTON PANELİ ===
        btn_outer = tk.Frame(self.root, bg=BG_LAYER2, relief="flat", highlightthickness=1, highlightbackground=PURPLE)
        btn_outer.pack(padx=20, pady=(0, 15), fill="x")
        
        btn_frame = tk.Frame(btn_outer, bg=BG_LAYER2)
        btn_frame.pack(pady=8)

        # Kill Butonu
        kill_container = tk.Frame(btn_frame, bg=PINK, relief="flat")
        kill_container.pack(side="left", padx=10)
        
        self.btn_kill = tk.Button(
            kill_container, text="💥 RAM SERBEST BIRAK / SONLANDIR",
            command=self.terminate_selected, bg=BG_LAYER1, fg=PINK,
            font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
            activebackground=PINK, activeforeground=BG, cursor="hand2"
        )
        self.btn_kill.pack(padx=2, pady=2, ipadx=12, ipady=6)

        # Yenile Butonu
        refresh_container = tk.Frame(btn_frame, bg=CYAN, relief="flat")
        refresh_container.pack(side="left", padx=10)
        
        self.btn_refresh = tk.Button(
            refresh_container, text="🔄 YENİLE (F5)",
            command=self.refresh_all, bg=BG_LAYER1, fg=CYAN,
            font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
            activebackground=CYAN, activeforeground=BG, cursor="hand2"
        )
        self.btn_refresh.pack(padx=2, pady=2, ipadx=12, ipady=6)

        # Tooltip'ler
        ToolTip(
            self.btn_kill, 
            "Seçili süreçleri güvenli bir şekilde sonlandırır\n"
            "Kritik sistem süreçleri korunur"
        )
        ToolTip(self.btn_refresh, "Tüm listeyi ve göstergeleri yeniler (F5)")

        # Kısayollar
        self.root.bind_all("<F5>", lambda e: self.refresh_all())
        self.root.bind_all("<Delete>", lambda e: self.terminate_selected())
        self.root.bind_all("<Control-f>", lambda e: self.search_entry.focus())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_gauge(self, parent, name, row, color_style):
        """Gauge (gösterge) oluşturur."""
        label = tk.Label(
            parent, text=f"{name}: 0.0%", font=("Segoe UI", 9, "bold"), 
            fg=FG, bg=BG_LAYER1, anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", padx=12, pady=4)

        bar = ttk.Progressbar(
            parent, style=f"{color_style}.Horizontal.TProgressbar", mode="determinate"
        )
        bar.grid(row=row, column=1, sticky="ew", padx=12, pady=4)

        return label, bar

    def create_net_gauge(self, parent, row):
        """Ağ göstergesini oluşturur."""
        net_frame = tk.Frame(parent, bg=BG_LAYER1)
        net_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=4)
        
        for i in range(4):
            net_frame.grid_columnconfigure(i, weight=1)

        tk.Label(
            net_frame, text="Ağ Hızı:", font=("Segoe UI", 9, "bold"), 
            fg=FG, bg=BG_LAYER1, anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        # İndirme
        self.net_recv_label = tk.Label(
            net_frame, text="↓ 0 KB/s", font=("Consolas", 8), 
            fg=CYAN, bg=BG_LAYER1, anchor="w"
        )
        self.net_recv_label.grid(row=0, column=1, sticky="w", padx=3)
        
        self.net_recv_bar = ttk.Progressbar(
            net_frame, style="Cyan.Horizontal.TProgressbar", mode="determinate"
        )
        self.net_recv_bar.grid(row=1, column=1, sticky="ew", pady=(2, 0), padx=3)

        # Yükleme
        self.net_sent_label = tk.Label(
            net_frame, text="↑ 0 KB/s", font=("Consolas", 8), 
            fg=PINK, bg=BG_LAYER1, anchor="w"
        )
        self.net_sent_label.grid(row=0, column=3, sticky="w", padx=3)
        
        self.net_sent_bar = ttk.Progressbar(
            net_frame, style="Pink.Horizontal.TProgressbar", mode="determinate"
        )
        self.net_sent_bar.grid(row=1, column=3, sticky="ew", pady=(2, 0), padx=3)

    def sort_treeview(self, col, numeric):
        """Treeview sütunlarına göre sıralama yapar."""
        # Mevcut sıralama ile aynı sütun mı?
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = True

        # Verileri çek ve sırala
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        if numeric:
            data.sort(key=lambda x: float(x[0]), reverse=self.sort_reverse)
        else:
            data.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)

        # Sıralanmış veriyi geri yerleştir
        for index, (val, k) in enumerate(data):
            self.tree.move(k, "", index)

    def refresh_process_list(self):
        """Süreç listesini yeniler."""
        self.full_process_list = get_all_processes()
        self.apply_filter()

    def apply_filter(self, *args):
        """Arama filtresini uygular."""
        search_term = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        count = 0
        for item in self.full_process_list:
            pid, name, rss, vms, tag = item
            if search_term in str(pid) or search_term in name.lower():
                self.tree.insert("", "end", values=(pid, name, rss, vms), tags=(tag,))
                count += 1

        # İstatistiği güncelle
        total = len(self.full_process_list)
        if search_term:
            self.stats_label.config(
                text=f"Gösterilen: {count} / {total} süreç"
            )
        else:
            self.stats_label.config(text=f"Toplam Süreç: {total}")

    def update_gauges(self):
        """Göstergeleri günceller."""
        # CPU
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_bar['value'] = cpu
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")
        
        if cpu > 85:
            self.cpu_bar.config(style="Red.Horizontal.TProgressbar")
        elif cpu > 60:
            self.cpu_bar.config(style="Yellow.Horizontal.TProgressbar")
        else:
            self.cpu_bar.config(style="Pink.Horizontal.TProgressbar")

        # RAM
        mem = psutil.virtual_memory()
        self.ram_bar['value'] = mem.percent
        self.ram_label.config(text=f"RAM: {mem.percent:.1f}%")
        
        if mem.percent > 85:
            self.ram_bar.config(style="Red.Horizontal.TProgressbar")
        else:
            self.ram_bar.config(style="Cyan.Horizontal.TProgressbar")
        
        # RAM bilgi etiketi
        self.ram_info_label.config(
            text=f"📊 Toplam: {format_bytes(mem.total)}  |  "
                 f"Kullanılan: {format_bytes(mem.used)}  |  "
                 f"Boşta: {format_bytes(mem.available)}"
        )

        # Disk
        disk = psutil.disk_usage('/').percent
        self.disk_bar['value'] = disk
        self.disk_label.config(text=f"Disk: {disk:.1f}%")
        
        if disk > 90:
            self.disk_bar.config(style="Red.Horizontal.TProgressbar")
        else:
            self.disk_bar.config(style="Yellow.Horizontal.TProgressbar")

        # Ağ hızı
        current = psutil.net_io_counters()
        elapsed = INFO_UPDATE_INTERVAL / 1000.0

        sent_kbps = (current.bytes_sent - self.last_net_io.bytes_sent) / 1024 / elapsed
        recv_kbps = (current.bytes_recv - self.last_net_io.bytes_recv) / 1024 / elapsed

        self.last_net_io = current

        # Ağ etiketlerini güncelle
        self.net_recv_label.config(text=f"↓ {recv_kbps:.0f} KB/s")
        self.net_sent_label.config(text=f"↑ {sent_kbps:.0f} KB/s")

        # Progressbar güncellemesi (Max 10 MB/s = 10240 KB/s)
        max_net = 10240
        self.net_recv_bar['value'] = min(recv_kbps / max_net * 100, 100)
        self.net_sent_bar['value'] = min(sent_kbps / max_net * 100, 100)

        self.root.after(INFO_UPDATE_INTERVAL, self.update_gauges)

    def terminate_selected(self):
        """Seçili süreçleri sonlandırır."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Sonlandırmak için en az bir süreç seçin.")
            return

        targets = []
        for item in selected:
            tags = self.tree.item(item, "tags")
            values = self.tree.item(item, "values")
            pid = int(values[0])
            name = values[1]

            if "critical" in tags:
                messagebox.showinfo(
                    "Koruma", 
                    f"Kritik sistem süreci sonlandırılamaz:\n{name.replace('🚨 ', '')}"
                )
                continue
            
            if pid == MY_PID:
                messagebox.showwarning("Güvenlik", "Kendi sürecini sonlandıramazsın!")
                continue
            
            targets.append((pid, name))

        if not targets:
            return

        # Onay
        msg = f"Seçili {len(targets)} süreç sonlandırılsın mı?\n\n"
        msg += "Bu işlem RAM'i serbest bırakır ancak kaydedilmemiş\n"
        msg += "verileriniz kaybolabilir!"
        
        if not messagebox.askyesno("⚠️ Onay", msg):
            return

        # Sonlandırma işlemi
        killed = 0
        failed = []
        
        for pid, name in targets:
            if safe_terminate(pid):
                killed += 1
            else:
                failed.append(name)

        # Sonuç mesajı
        result_msg = f"✅ {killed}/{len(targets)} süreç başarıyla sonlandırıldı.\n"
        if failed:
            result_msg += f"\n❌ Sonlandırılamayan süreçler:\n"
            result_msg += "\n".join(f"• {name}" for name in failed[:5])
            if len(failed) > 5:
                result_msg += f"\n... ve {len(failed)-5} tane daha"
        
        messagebox.showinfo("Sonuç", result_msg)
        self.refresh_all()

    def refresh_all(self):
        """Tüm listeyi yeniler."""
        self.refresh_process_list()

    def start_updates(self):
        """Güncellemeleri başlatır."""
        self.refresh_process_list()
        self.update_gauges()

    def on_closing(self):
        """Uygulama kapanırken çağrılır."""
        if messagebox.askokcancel("Çıkış", "Uygulamayı kapatmak istiyor musunuz?"):
            self.root.destroy()

    def on_search(self, *args):
        """Arama değiştiğinde çağrılır."""
        self.apply_filter()


if __name__ == "__main__":
    root = tk.Tk()
    app = RamCleanerApp(root)
    root.mainloop()

