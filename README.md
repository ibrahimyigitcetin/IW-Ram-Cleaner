# 🌌 IW Ram Cleaner | Retro Night Club Edition

<div align="center">
  <img src="https://img.shields.io/github/languages/count/ibrahimyigitcetin/IW-Ram-Cleaner?style=flat-square&color=blueviolet" alt="Language Count">
  <img src="https://img.shields.io/github/languages/top/ibrahimyigitcetin/IW-Ram-Cleaner?style=flat-square&color=1e90ff" alt="Top Language">
  <img src="https://img.shields.io/github/last-commit/ibrahimyigitcetin/IW-Ram-Cleaner?style=flat-square&color=ff69b4" alt="Last Commit">
  <img src="https://img.shields.io/github/license/ibrahimyigitcetin/IW-Ram-Cleaner?style=flat-square&color=yellow" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-green?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=flat-square" alt="Contributions">
</div>

## 🌟 About the Project

**IW Ram Cleaner** is a powerful and aesthetic Python application designed to manage RAM (Memory) consumption on your system. It allows you to easily detect high-resource or unresponsive processes and instantly free up memory while preserving system stability through its intelligent **Safe Kill** mechanism.

The application is designed with a classic **"Retro Night Club Game"** aesthetic; it brings a dynamic and enjoyable approach to system management using dark backgrounds, neon colors (Cyan and Pink), and the `Consolas` font.

![IW Ram Cleaner](./docs/iwrc.png)

### ✨ Powerful Features

| Feature | Detailed Description |
| :--- | :--- |
| **🛡️ Smart Protection (Safe Kill)** | The application recognizes critical Windows system processes such as `csrss.exe` and `winlogon.exe`. Accidental termination of these processes is automatically blocked and the user is presented with a strong warning about the potential for system crashes. |
| **📈 Detailed Memory Metrics** | The process list includes two important memory metrics: **RSS (Resident Set Size)**: The amount the process is using in physical RAM (Real RAM). **VMS (Virtual Memory Size)**: The total amount of virtual memory allocated by the process. |
| **📊 System RAM Overview** | At the top of the window, there is a real-time, up-to-date information bar showing your system's **Total**, **Used**, and **Free** RAM amounts. |
| **🔍 Multi-Select and Filtering** | Select multiple processes with a single click and drag, or using **`Ctrl` / `Shift`** keys. The search box at the top provides instant, high-performance filtering by process **Name** or **PID** (Process ID). |
| **🔝 Smart Sorting** | The list opens with **smart sorting** that brings the applications consuming the **most RAM (RSS)** to the top. You can change the sort order by clicking column headers; the first click switches to descending order (highest on top), the next click switches to ascending order, and sorting is performed correctly numerically/alphabetically. |
| **⚡ Enhanced User Experience (UX)** | The application supports keyboard shortcuts for fast interaction: refresh the list with **`F5`** and terminate selected processes with **`Delete`**. **Tooltips** are also available on buttons to provide information. |

-----

## ⚙️ Installation and Launch

You need **Python 3.x** and the **`psutil`** library to run this application.

### 1\. Library Installation

Install the required dependencies using the following command:

```bash
pip install psutil
```

### 2\. Launch

Run the file where you saved the code (e.g. `iw_ram_cleaner.py`) in the terminal:

```bash
python iw_ram_cleaner.py
```

> 🚨 **Administrator Privileges:** To reliably terminate critical processes on Windows or Linux systems, it is recommended to run the application with **Administrator/Root** privileges.

-----

## ⬇️ User Download and Launch

To download the executable (.exe) version of the application, please go to the **GitHub Releases** page and download the latest release (for example, the **iwrc.exe** file under the v0.1.0-beta tag).

## 🖥️ Usage Guide

1. **Top Panel** → Monitor your CPU, RAM, Disk, and Network speeds in real time.
2. **RAM Status** → Total / Used / Free memory amounts are displayed in detail.
3. **Process List** → Processes consuming the most RAM appear at the top. Critical ones are marked with 🚨.
4. **Search** → Quickly filter by typing a process name or PID.
5. **Termination**
   - Select one or more processes (`Ctrl` / `Shift` or drag).
   - Click the `💥 FREE RAM / TERMINATE` button or press the `Delete` key.
   - Critical processes are automatically blocked and confirmation is requested.
6. **Refresh** → Update all data with the `🔄 REFRESH (F5)` button or the F5 key.

-----

## 🎨 Retro Theme Color Scheme

| Component           | Hex Code    | Description               |
|---------------------|-------------|---------------------------|
| **Deep Background** | `#0a0a0a`   | Main BG                   |
| **Layer 1**         | `#1a1a1a`   | Panels                    |
| **Layer 2**         | `#252525`   | Inner frames              |
| **Neon Cyan**       | `#00BFFF`   | RAM, normal buttons       |
| **Neon Pink**       | `#FF1493`   | Headers, kill button      |
| **Neon Purple**     | `#9D00FF`   | Borders and highlights    |
| **Neon Red**        | `#FF0055`   | Critical warnings         |
| **Neon Green**      | `#00FF7F`   | Statistics                |

-----

## 🤝 Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For details, please refer to [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 📄 License

This project is distributed under the MIT license. For details, please refer to [LICENSE.md](LICENSE.md).

---

🌍 For Turkish version, see: [README-tr-TR.md](README-tr-TR.md)
