import tkinter as tk
from tkinter import messagebox, ttk
import psutil  # type: ignore
import os

# ====================== KORUNACAK KRİTİK SÜREÇLER ======================
CRITICAL_PROCESSES = {
    "svchost.exe", "csrss.exe", "winlogon.exe", 
    "lsass.exe", "smss.exe", "services.exe", "explorer.exe"
}

MY_PID = os.getpid()
FULL_PROCESS_LIST = []

# ====================== GÜVENLİ SONLANDIRMA ======================
def safe_kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        gone, still_alive = psutil.wait_procs([p], timeout=3)
        for proc in still_alive:
            proc.kill()
        return True
    except:
        return False

# ====================== SÜREÇ LİSTELEME ======================
def get_process_list():
    global FULL_PROCESS_LIST
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            info = proc.info
            pid = info['pid']
            name = info['name'] or "[Bilinmeyen]"
            
            if pid == MY_PID:
                name += " (Bu Uygulama - Koruma Aktif)"
            
            mem = info['memory_info']
            rss_mb = mem.rss / (1024 * 1024)
            vms_mb = mem.vms / (1024 * 1024)

            # Kritik süreçse gri renkte göster ve seçimi engelle
            is_critical = any(crit.lower() in name.lower() for crit in CRITICAL_PROCESSES)
            tag = "critical" if is_critical else "normal"
            
            processes.append((pid, name, f"{rss_mb:.1f}", f"{vms_mb:.1f}", tag))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda x: float(x[2]), reverse=True)
    FULL_PROCESS_LIST = processes
    return processes

# ====================== FİLTRELEME VE YÜKLEME ======================
def load_process_list(refresh_data=False):
    selected_pids = {int(tree.item(item, "values")[0]) for item in tree.selection() if tree.item(item, "tags")[0] != "critical"}

    if refresh_data or not FULL_PROCESS_LIST:
        get_process_list()

    filter_processes()

    # Sadece normal süreçleri tekrar seç
    for item in tree.get_children():
        pid = int(tree.item(item, "values")[0])
        if pid in selected_pids:
            tree.selection_add(item)

    update_ram_info()

def filter_processes(event=None):
    filter_text = search_entry.get().lower()
    tree.delete(*tree.get_children())

    for pid, name, rss, vms, tag in FULL_PROCESS_LIST:
        if filter_text in str(pid) or filter_text.lower() in name.lower():
            item = tree.insert("", "end", values=(pid, name, rss, vms), tags=(tag,))
            if tag == "critical":
                tree.item(item, tags=("critical",))

# ====================== SÜREÇ SONLANDIRMA ======================
def terminate_selected_processes():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Uyarı", "Lütfen sonlandırmak istediğiniz süreçleri seçin.")
        return

    pids = []
    names = []
    for item in selected_items:
        if "critical" in tree.item(item, "tags"):
            messagebox.showinfo("Koruma Aktif", "Kritik sistem süreçleri güvenlik nedeniyle sonlandırılamaz.")
            continue
        values = tree.item(item, "values")
        pid = int(values[0])
        name = values[1]
        if pid == MY_PID:
            messagebox.showwarning("Güvenlik", "IW Ram Cleaner kendi sürecini sonlandıramaz!")
            continue
        pids.append(pid)
        names.append(name)

    if not pids:
        return

    if not messagebox.askyesno("Onay", f"{len(pids)} süreç sonlandırılsın mı?\nRAM serbest bırakılacak."):
        return

    killed = 0
    for pid, name in zip(pids, names):
        if safe_kill_process(pid):
            killed += 1

    messagebox.showinfo("Tamamlandı", f"{killed} süreç başarıyla sonlandırıldı.\nRAM serbest bırakıldı!")
    load_process_list(refresh_data=True)

# ====================== RAM BİLGİSİ ======================
def update_ram_info():
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    avail_gb = mem.available / (1024**3)
    percent = mem.percent
    ram_label.config(
        text=f"Toplam: {total_gb:.2f} GB │ Kullanılan: {used_gb:.2f} GB ({percent:.1f}%) │ Boş: {avail_gb:.2f} GB"
    )

# ====================== TOOLTIP ======================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1,
                         font=("Segoe UI", 9), padx=5, pady=3)
        label.pack()
    def hide_tip(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ====================== ARAYÜZ ======================
root = tk.Tk()
root.title("IW Ram Cleaner")
root.geometry("820x580")
root.configure(bg="#1A1A1A")
root.minsize(700, 500)

BG = "#1A1A1A"
CYAN = "#00FFFF"
PINK = "#FF00FF"

style = ttk.Style()
style.theme_use("default")
style.configure(".", background=BG, foreground="white", font=("Consolas", 10))
style.configure("Treeview", background=BG, foreground=CYAN, fieldbackground=BG, rowheight=26)
style.configure("Treeview.Heading", background=BG, foreground=PINK, font=("Consolas", 11, "bold"))
style.map("Treeview", background=[("selected", PINK)], foreground=[("selected", BG)])

# Kritik süreçler gri renkte
tree = ttk.Treeview(root, columns=("PID", "Uygulama Adı", "RSS (MB)", "VMS (MB)"), show="headings", selectmode="extended")
tree.tag_configure("critical", foreground="#888888", background="#2A2A2A")

# Başlık
tk.Label(root, text="IW RAM CLEANER", font=("Consolas", 22, "bold"), fg=PINK, bg=BG).pack(pady=(15, 5))
tk.Label(root, text="Night Club Edition", font=("Consolas", 9), fg=CYAN, bg=BG).pack(pady=(0, 10))

# RAM Çubuğu
ram_label = tk.Label(root, text="", font=("Consolas", 10), fg=CYAN, bg=BG)
ram_label.pack(pady=(0, 10))

# Arama
frame_search = tk.Frame(root, bg=BG)
frame_search.pack(padx=20, pady=(5, 10), fill="x")
tk.Label(frame_search, text="Arama:", fg=CYAN, bg=BG, font=("Consolas", 10, "bold")).pack(side="left")
search_entry = tk.Entry(frame_search, fg=PINK, bg="#2D2D2D", insertbackground=PINK, relief="solid", font=("Consolas", 10))
search_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
search_entry.bind("<KeyRelease>", filter_processes)

# Treeview
tree.pack(padx=20, pady=10, fill="both", expand=True)
tree.heading("PID", text="PID")
tree.heading("Uygulama Adı", text="Uygulama Adı")
tree.heading("RSS (MB)", text="RAM (RSS)")
tree.heading("VMS (MB)", text="Sanal (VMS)")
tree.column("PID", width=70, anchor="center")
tree.column("Uygulama Adı", width=350)
tree.column("RSS (MB)", width=100, anchor="e")
tree.column("VMS (MB)", width=100, anchor="e")

# Butonlar
frame_buttons = tk.Frame(root, bg=BG)
frame_buttons.pack(pady=20)
btn_kill = tk.Button(frame_buttons, text="RAM SERBEST BIRAK", bg=PINK, fg=BG,
                     font=("Consolas", 12, "bold"), command=terminate_selected_processes, relief="raised", padx=20, pady=8)
btn_kill.pack(side="left", padx=15)
btn_refresh = tk.Button(frame_buttons, text="YENİLE", bg=CYAN, fg=BG,
                        font=("Consolas", 12, "bold"), command=lambda: load_process_list(True), relief="raised", padx=20, pady=8)
btn_refresh.pack(side="left", padx=15)

ToolTip(btn_kill, "Seçili süreçleri güvenli şekilde sonlandırır")
ToolTip(btn_refresh, "Listeyi yeniler (F5)")

# Kısayollar
root.bind_all("<F5>", lambda e: load_process_list(True))
root.bind_all("<Delete>", lambda e: terminate_selected_processes())
root.protocol("WM_DELETE_WINDOW", 
              lambda: root.destroy() if messagebox.askokcancel("Çıkış", "Çıkmak istiyor musunuz?") else None)

# İlk yükleme
load_process_list(refresh_data=True)
root.mainloop()