## PLC-Mech – Mock PLC, Client & Dashboard

This project is a **proof-of-concept data pipeline and web dashboard** for Siemens S7 PLCs:

- A **mock PLC server** using `python-snap7` (no hardware required).
- A **Python client** that reads a REAL value from a DB.
- A **Streamlit dashboard** (with Plotly) that shows **live trends and statistics**.

It is designed so you can later point the same client and dashboard at a **real PLC**.

---

## 1. Prerequisites

- **Python** 3.10+.
- **Git** (optional, for cloning from GitHub).

### 1.1 Linux – Snap7 native library

On Ubuntu/Debian, install the Snap7 native library:

```bash
sudo apt update
sudo apt install libsnap7-1
```

If your distro doesn’t have `libsnap7`, follow the instructions from the Snap7 project to install it, then continue.

### 1.2 Windows – Snap7 native library

On Windows you also need the Snap7 DLL:

1. Download the Snap7 Windows package (x86 or x64) from the official project.
2. Copy the **Snap7 DLL** (e.g. `snap7.dll`) to a location on your `PATH`, or next to your Python executable, or next to this project (e.g. in the project root).
3. Make sure you use the **64‑bit DLL** if your Python is 64‑bit (most common).

If `python-snap7` cannot find the DLL, you will get import or connection errors; in that case, double‑check that `snap7.dll` is in a folder listed in your `PATH` and restart your terminal/IDE.

---

## 2. Get the project

If you already have the folder (e.g. `~/Downloads/islam`), skip to step 3.

From GitHub:

```bash
cd ~
git clone https://github.com/AliHossamTesla/PLC-Mech.git
cd PLC-Mech
```

From a local archive/folder:

```bash
cd /home/tesla/Downloads/islam
```

All commands below assume you are **inside the project root**.

---

## 3. Create & activate a virtual environment

Using a virtual environment is recommended on **both Linux and Windows**.

### 3.1 Linux

```bash
cd /home/tesla/Downloads/islam    # or your clone path

python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` in your shell prompt.

To deactivate later:

```bash
deactivate
```

### 3.2 Windows (PowerShell / CMD)

From the project directory:

```powershell
cd C:\path\to\PLC-Mech   # adjust to your clone path

python -m venv .venv

# PowerShell:
.venv\Scripts\Activate.ps1

# or CMD:
.venv\Scripts\activate.bat
```

You should now see `(.venv)` in your prompt. To deactivate:

```powershell
deactivate
```

---

## 4. Install Python dependencies

With the virtual environment **activated**:

```bash
pip install -r requirements.txt
```

This installs:

- `python-snap7` – Snap7 client/server bindings
- `streamlit` – web dashboard
- `pandas` – data handling
- `plotly` – plotting

---

## 5. Run the mock PLC server

Terminal 1 (Linux):

```bash
cd /home/tesla/Downloads/islam
source .venv/bin/activate

python mock_server.py
```

Terminal 1 (Windows PowerShell / CMD):

```powershell
cd C:\path\to\PLC-Mech
.venv\Scripts\Activate.ps1   # or .venv\Scripts\activate.bat

python mock_server.py
```

You should see logs like:

```text
[SERVER] Mock PLC started on 127.0.0.1:1102, DB1, size=4 bytes
[SERVER] Starting update loop with interval=0.5s.
[SERVER] Wrote value 50.00 to DB1.DBD0
[SERVER] Wrote value 73.99 to DB1.DBD0
...
```

This is a **fake S7 server** exposing:

- DB **1**
- REAL value at **DB1.DBD0** (4 bytes)
- Value varies as a **sine wave** between 0 and 100.

---

## 6. Run the real-time dashboard

Open **another terminal** (Terminal 2).

Linux:

```bash
cd /home/tesla/Downloads/islam
source .venv/bin/activate

streamlit run dashboard.py
```

Windows PowerShell / CMD:

```powershell
cd C:\path\to\PLC-Mech
.venv\Scripts\Activate.ps1   # or .venv\Scripts\activate.bat

streamlit run dashboard.py
```

Streamlit will print something like:

```text
Local URL: http://localhost:8501
Network URL: http://192.168.1.5:8501
```

Open the local URL in your browser.

### 6.1 Dashboard features (Mock mode)

- In the **sidebar**, the “Connection” section shows:
  - **PLC source**: defaults to **“Mock (local)”**
  - Uses `127.0.0.1`, rack `0`, slot `1`, port `1102`.
- The main view shows:
  - **Metrics**:
    - Current value
    - Moving average (last 10 samples)
    - Minimum and maximum
  - **Plotly line chart** of the value over time.
  - **Raw Data** expander with the latest readings (Pandas DataFrame).

Data updates every **0.5 seconds**.

---

## 7. Switching between Mock and Real PLC

The dashboard can connect either to:

- The **local mock PLC**, or
- A **real S7 PLC** on your network.

Use the **sidebar**:

- **Mock (local)**:
  - No configuration needed (assumes `mock_server.py` is running).

- **Real PLC**:
  - Enter:
    - PLC IP address (e.g. `192.168.0.10`)
    - Rack (usually `0`)
    - Slot (e.g. `1` for many S7-1200/1500 CPUs)
    - TCP port (usually `102`)
  - The app will:
    - Create or reconfigure a `PLCReader` with those settings.
    - Attempt to connect using `python-snap7`.
    - Read `DB1.DBD0` as a REAL.

If the connection fails, you’ll see an error like:

```text
Failed to connect to PLC: ...
```

You can then switch back to **Mock (local)**; the app will reconnect to `127.0.0.1:1102` and resume showing the simulated signal.

---

## 8. Direct CLI client test (optional)

You can test the client without Streamlit using the simple text loop.

Linux:

```bash
cd /home/tesla/Downloads/islam
source .venv/bin/activate

python plc_client.py
```

Windows PowerShell / CMD:

```powershell
cd C:\path\to\PLC-Mech
.venv\Scripts\Activate.ps1   # or .venv\Scripts\activate.bat

python plc_client.py
```

This will print timestamped readings from DB1.DBD0 until you press `Ctrl+C`.

---

## 9. Project structure (overview)

- `mock_server.py` – Snap7 **Server** acting as a mock PLC (DB1, REAL value).
- `plc_client.py` – Snap7 **Client** (`PLCReader` class) that reads DB1.DBD0.
- `dashboard.py` – Streamlit dashboard using `PLCReader`, Pandas, and Plotly.
- `requirements.txt` – Python dependencies.
- `SHUBRA_PROJECT_DOCUMENTATION.md` – Documentation of the original TIA Portal HMI export.
- `shubra/` – Exported TIA Portal v16 WinCC project files (binary/proprietary).

This gives you a complete path from **PLC (real or mock)** → **Python client** → **live web analytics UI**.

