import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import psutil  # type: ignore


# ====================== AYARLAR ======================
CRITICAL_PROCESSES = {
    "svchost.exe", "csrss.exe", "winlogon.exe",
    "lsass.exe", "smss.exe", "services.exe", "explorer.exe",
    "wininit.exe", "dwm.exe", "taskhostw.exe"
}

MY_PID = os.getpid()
INFO_UPDATE_INTERVAL = 1000  # ms

# Renk paleti
BG = "#1A1A1A"
FG = "white"
CYAN = "#00FFFF"
PINK = "#FF00FF"
BAR_BG = "#2D2D2D"
GRAY = "#888888"


# ====================== YARDIMCI FONKSİYONLAR ======================
def safe_terminate(pid: int) -> bool:
    """Güvenli bir şekilde süreci sonlandırır."""
    try:
        p = psutil.Process(pid)
        p.terminate()
        _, alive = psutil.wait_procs([p], timeout=3)
        return len(alive) == 0
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def get_all_processes():
    """Tüm süreçleri topla ve bellek kullanımına göre sırala."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
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

            # Kritik süreç kontrolü (büyük/küçük harf duyarsız)
            is_critical = any(crit.lower() in name.lower() for crit in CRITICAL_PROCESSES)

            processes.append((pid, name, f"{rss_mb:.1f}", f"{vms_mb:.1f}", "critical" if is_critical else "normal"))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # RSS'ye göre azalan sırada sırala
    processes.sort(key=lambda x: float(x[2]), reverse=True)
    return processes


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

        label = tk.Label(self.tip, text=self.text, background="#FFFFE0", relief="solid",
                         borderwidth=1, font=("Segoe UI", 9), padx=7, pady=4, justify="left")
        label.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ====================== ANA UYGULAMA ======================
class RamCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IW Ram Cleaner - Gelişmiş Kaynak İzleyici")
        self.root.geometry("860x740")
        self.root.minsize(780, 680)
        self.root.configure(bg=BG)

        self.full_process_list = []
        self.last_net_io = psutil.net_io_counters()

        self.setup_styles()
        self.create_widgets()
        self.start_updates()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure(".", background=BG, foreground=FG, font=("Consolas", 10))
        style.configure("Treeview", background=BG, foreground=CYAN, fieldbackground=BG, rowheight=28)
        style.configure("Treeview.Heading", background=BG, foreground=PINK, font=("Consolas", 11, "bold"))
        style.map("Treeview", background=[("selected", PINK)], foreground=[("selected", BG)])

        # Progressbar renkleri
        style.configure("Pink.Horizontal.TProgressbar", background=PINK, troughcolor=BAR_BG)
        style.configure("Cyan.Horizontal.TProgressbar", background=CYAN, troughcolor=BAR_BG)
        style.configure("Yellow.Horizontal.TProgressbar", background="yellow", troughcolor=BAR_BG)

    def create_widgets(self):
        # === ÜST KISIM - Başlık ve Göstergeler ===
        top_frame = tk.Frame(self.root, bg=BG)
        top_frame.pack(padx=20, pady=(15, 10), fill="x")

        tk.Label(top_frame, text="IW RAM CLEANER", font=("Consolas", 20, "bold"), fg=PINK, bg=BG).pack()
        tk.Label(top_frame, text="Night Club Edition", font=("Consolas", 10), fg=CYAN, bg=BG).pack()

        self.ram_info_label = tk.Label(top_frame, text="", font=("Consolas", 10), fg=FG, bg=BG)
        self.ram_info_label.pack(pady=(8, 12))

        gauges_frame = tk.Frame(top_frame, bg=BG)
        gauges_frame.pack(fill="x", pady=8)

        # CPU
        self.cpu_label, self.cpu_bar = self.create_gauge(gauges_frame, "CPU: 0.0%", "Pink")
        # RAM
        self.ram_label, self.ram_bar = self.create_gauge(gauges_frame, "RAM: 0.0%", "Cyan")
        # Disk
        self.disk_label, self.disk_bar = self.create_gauge(gauges_frame, "Disk: 0.0%", "Yellow")
        # Ağ
        net_frame = tk.Frame(gauges_frame, bg=BG)
        net_frame.pack(fill="x", pady=4)
        self.net_label = tk.Label(net_frame, text="Ağ: ↓0 KB/s ↑0 KB/s", font=("Consolas", 10, "bold"), fg=FG, bg=BG, anchor="w")
        self.net_label.pack(side="left", fill="x", expand=True, padx=(15, 5))
        self.net_sent_bar = ttk.Progressbar(net_frame, style="Pink.Horizontal.TProgressbar", length=120)
        self.net_sent_bar.pack(side="left", padx=5)
        self.net_recv_bar = ttk.Progressbar(net_frame, style="Cyan.Horizontal.TProgressbar", length=120)
        self.net_recv_bar.pack(side="left", padx=5)

        # === ARAMA VE LİSTE ===
        search_frame = tk.Frame(self.root, bg=BG)
        search_frame.pack(padx=20, pady=8, fill="x")
        tk.Label(search_frame, text="Arama:", fg=CYAN, bg=BG, font=("Consolas", 10, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, fg=PINK, bg=BAR_BG,
                                     insertbackground=PINK, relief="solid", font=("Consolas", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.search_var.trace_add("write", self.on_search)

        # Treeview
        columns = ("PID", "Uygulama Adı", "RSS (MB)", "VMS (MB)")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="extended")
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree.heading("PID", text="PID")
        self.tree.heading("Uygulama Adı", text="Uygulama Adı")
        self.tree.heading("RSS (MB)", text="RAM (RSS MB)")
        self.tree.heading("VMS (MB)", text="Sanal (VMS MB)")

        self.tree.column("PID", width=80, anchor="center")
        self.tree.column("Uygulama Adı", width=380, anchor="w")
        self.tree.column("RSS (MB)", width=110, anchor="e")
        self.tree.column("VMS (MB)", width=110, anchor="e")

        self.tree.tag_configure("critical", foreground=GRAY, background="#2A2A2A")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # === BUTONLAR ===
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=15)

        btn_kill = tk.Button(btn_frame, text="RAM SERBEST BIRAK", bg=PINK, fg=BG,
                          font=("Consolas", 12, "bold"), command=self.terminate_selected, padx=25, pady=10)
        btn_kill.pack(side="left", padx=20)

        btn_refresh = tk.Button(btn_frame, text="YENİLE (F5)", bg=CYAN, fg=BG,
                                font=("Consolas", 12, "bold"), command=self.refresh_all, padx=25, pady=10)
        btn_refresh.pack(side="left", padx=20)

        ToolTip(btn_kill, "Seçili süreçleri güvenli bir şekilde sonlandırır\nKritik sistem süreçleri korunur")
        ToolTip(btn_refresh, "Tüm listeyi ve göstergeleri yeniler")

        # Kısayollar
        self.root.bind_all("<F5>", lambda e: self.refresh_all())
        self.root.bind_all("<Delete>", lambda e: self.terminate_selected())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_gauge(self, parent, text, color_style):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=3)

        label = tk.Label(frame, text=text, font=("Consolas", 10, "bold"), fg=FG, bg=BG, anchor="w")
        label.pack(side="left", padx=(15, 10), fill="x", expand=True)

        bar = ttk.Progressbar(frame, style=f"{color_style}.Horizontal.TProgressbar", length=300)
        bar.pack(side="left", fill="x", expand=True, padx=10)

        return label, bar

    # ====================== GÜNCELLEME FONKSİYONLARI ======================
    def refresh_process_list(self):
        self.full_process_list = get_all_processes()
        self.apply_filter()

    def apply_filter(self, *args):
        search_term = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        for item in self.full_process_list:
            pid, name, rss, vms, tag = item
            if search_term in str(pid) or search_term in name.lower():
                self.tree.insert("", "end", values=(pid, name, rss, vms), tags=(tag,))

    def on_search(self, *args):
        self.apply_filter()

    def update_gauges(self):
        """1 saniyede bir sistem kaynaklarını güncelle."""
        # CPU
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_bar['value'] = cpu
        self.cpu_label.config(text=f"CPU: {cpu:.1f}%")

        # RAM
        mem = psutil.virtual_memory()
        self.ram_bar['value'] = mem.percent
        self.ram_label.config(text=f"RAM: {mem.percent:.1f}%")
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        self.ram_info_label.config(text=f"Toplam: {total_gb:.2f} GB  |  Kullanılan: {used_gb:.2f} GB  |  Boşta: {(mem.available/(1024**3)):.2f} GB")

        # Disk
        disk = psutil.disk_usage('/').percent
        self.disk_bar['value'] = disk
        self.disk_label.config(text=f"Disk: {disk:.1f}%")

        # Ağ hızı
        current = psutil.net_io_counters()
        elapsed = INFO_UPDATE_INTERVAL / 1000.0

        sent_kbps = (current.bytes_sent - self.last_net_io.bytes_sent) / 1024 / elapsed
        recv_kbps = (current.bytes_recv - self.last_net_io.bytes_recv) / 1024 / elapsed

        self.last_net_io = current

        self.net_label.config(text=f"Ağ: ↓{recv_kbps:.0f} KB/s   ↑{sent_kbps:.0f} KB/s")
        # Temsili progressbar (maksimum 1000 KB/s kabul ediyoruz)
        self.net_recv_bar['value'] = min(recv_kbps / 10, 100)
        self.net_sent_bar['value'] = min(sent_kbps / 10, 100)

        self.root.after(INFO_UPDATE_INTERVAL, self.update_gauges)

    def terminate_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Sonlandırmak için en az bir süreç seçin.")
            return

        targets = []
        for item in selected:
            tags = self.tree.item(item, "tags")
            if "critical" in tags:
                messagebox.showinfo("Koruma", "Kritik sistem süreçleri sonlandırılamaz.")
                continue
            pid = int(self.tree.item(item, "values")[0])
            if pid == MY_PID:
                messagebox.showwarning("Güvenlik", "Kendi sürecini sonlandıramazsın!")
                continue
            targets.append((pid, self.tree.item(item, "values")[1]))

        if not targets:
            return

        if not messagebox.askyesno("Onay", f"{len(targets)} süreç sonlandırılsın mı?\nBu işlem RAM'i serbest bırakır."):
            return

        killed = 0
        for pid, name in targets:
            if safe_terminate(pid):
                killed += 1

        messagebox.showinfo("Sonuç", f"{killed}/{len(targets)} süreç başarıyla sonlandırıldı.\nRAM serbest bırakıldı.")
        self.refresh_all()

    def refresh_all(self):
        self.refresh_process_list()

    def start_updates(self):
        self.refresh_process_list()
        self.update_gauges()

    def on_closing(self):
        if messagebox.askokcancel("Çıkış", "Uygulamayı kapatmak istiyor musunuz?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RamCleanerApp(root)
    root.mainloop()
