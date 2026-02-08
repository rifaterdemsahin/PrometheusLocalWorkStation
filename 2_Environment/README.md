# Prometheus Metrics In Local Machine Displayed with Grafana

Comprehensive monitoring solution for DaVinci Resolve workstations using Prometheus and Grafana.

## Overview

This project provides a complete monitoring stack for Windows workstations running DaVinci Resolve, including:

- **System Metrics**: CPU, GPU, Memory, and Disk usage
- **DaVinci Resolve Metrics**: Process monitoring, project tracking, and log analysis
- **Real-time Dashboards**: Pre-configured Grafana dashboards for visualization
- **Automated Installation**: PowerShell scripts for easy Windows deployment

## Project Structure Explained

This project uses a unique seven-folder structure that represents a holistic development journey. Each folder has a specific purpose, guiding you through a structured and philosophical workflow.

### 🎯 1_Real: Objectives & Key Results
- **Premise:** Every project must begin with a clear and measurable goal. This folder establishes the **"why"** behind the work.
- **Content:** High-level objectives and key results (OKRs).
- **Conclusion:** Aligns all work with a tangible purpose.

### 🗺️ 2_Environment: Roadmap & Use Cases
- **Premise:** A goal needs a path. This folder lays out the strategic plan.
- **Content:** Project roadmap, learning modules, and use cases, including environment setup files.
- **Conclusion:** Ensures a clear direction grounded in user needs.

### 🧠 3_UI: Knowledge & Skill Acquisition
- **Premise:** Development is a journey of learning.
- **Content:** A personal knowledge base for concepts, theories, and skills.
- **Conclusion:** Fosters continuous improvement.

### 📚 4_Formula: Guides & Best Practices
- **Premise:** Don't reinvent the wheel.
- **Content:** Essential guides, formulas, and code snippets.
- **Conclusion:** Solves challenges efficiently and ensures high quality.

### 💻 5_Symbols: Implementation & Code
- **Premise:** Where theory becomes reality.
- **Content:** The core application source code.
- **Conclusion:** The heart of the project.

### 🐞 6_Semblance: Error Logging & Solutions
- **Premise:** Mistakes are valuable learning opportunities.
- **Content:** A log of bugs, errors, and their solutions.
- **Conclusion:** Prevents repeated mistakes and accelerates development.

### ✅ 7_Testing: Validation & Quality Assurance
- **Premise:** A project is only complete when proven to work.
- **Content:** Testing scripts and documentation, including dashboard assets.
- **Conclusion:** Guarantees quality and confirms objectives are met.

## Components

### Installed Components (Native Windows Installation)

1.  **Prometheus** (v2.45.0+) - Time-series database and monitoring system
2.  **Windows Exporter** (v0.25.0+) - System metrics collector for Windows
3.  **DaVinci Resolve Custom Exporter** - Custom metrics for DaVinci Resolve
4.  **Grafana** (v10.0.0+) - Dashboard and visualization platform
5.  **NSSM (Non-Sucking Service Manager)** - Tool to run applications as Windows services

### Metrics Collected

#### System Metrics (Windows Exporter)
- CPU usage and performance
- GPU utilization and memory
- Disk I/O and storage capacity
- Memory usage and allocation
- Network statistics

#### DaVinci Resolve Metrics (Custom Exporter)
- Process status (running/stopped)
- CPU and memory usage by DaVinci Resolve
- Hard drive metrics for media storage
- Cache disk usage
- Project count and total size
- Log file monitoring (errors, warnings)
- Log file size tracking

## Quick Start (Native Windows Installation)

This section details the manual installation and configuration of each component required to run the monitoring stack natively on Windows.

### Prerequisites

*   **Windows Operating System**: Windows 10/11
*   **Python 3.x**: Installed and added to PATH (for DaVinci Resolve Exporter)
*   **NSSM**: Download the latest version of [NSSM (Non-Sucking Service Manager)](https://nssm.cc/download) and extract `nssm.exe` to a directory included in your system's PATH (e.g., `C:\Windows\System32` or a custom `C:\Tools` folder).

### Installation Steps

#### 1. Install Prometheus

1.  **Using Chocolatey (Recommended)**:
    ```powershell
    choco install prometheus -y
    ```
    This will download and install Prometheus, typically to `C:\ProgramData\chocolatey\lib\prometheus\tools`.
    
2.  **Manual Installation (if Chocolatey is not preferred or available)**:
    *   **Download Prometheus**: Go to the [Prometheus downloads page](https://prometheus.io/download/) and download the latest Windows release (e.g., `prometheus-*.windows-amd64.zip`).
    *   **Extract**: Extract the contents of the zip file to a directory of your choice, e.g., `C:\Prometheus`.

3.  **Configure Prometheus**:
    *   Copy the `2_Environment/prometheus.yml` file from **this repository** to your Prometheus installation directory.
        *   If installed via Chocolatey, this is typically `C:\ProgramData\chocolatey\lib\prometheus\tools`.
        *   If manually installed, this is your chosen directory, e.g., `C:\Prometheus`.

4.  **Create Windows Service using NSSM (Optional but Recommended for Auto-Start)**:
    *   Prometheus installed via Chocolatey might not automatically set itself up as a Windows service. If you want Prometheus to run automatically at system startup, you can create a service using NSSM.
    *   First, locate the `prometheus.exe` executable.
        *   For Chocolatey installations, this is typically `C:\ProgramData\chocolatey\lib\prometheus\tools\prometheus.exe`.
        *   For manual installations, it's `C:\Prometheus\prometheus.exe` (or your chosen path).
    ```powershell
    nssm install Prometheus C:\ProgramData\chocolatey\lib\prometheus\tools\prometheus.exe --config.file="C:\ProgramData\chocolatey\lib\prometheus\tools\prometheus.yml"
    nssm set Prometheus AppDirectory C:\ProgramData\chocolatey\lib\prometheus\tools
    nssm set Prometheus Description "Prometheus monitoring server"
    nssm start Prometheus
    ```
    *Note: Adjust paths if your Prometheus installation differs.*

#### 2. Install Grafana

1.  **Using Winget (Recommended)**:
    ```powershell
    winget install GrafanaLabs.Grafana.OSS
    ```
    This will download and install Grafana, typically setting it up as a Windows service that starts automatically.
    
2.  **Manual Installation (if Winget is not preferred or available)**:
    *   **Download Grafana**: Go to the [Grafana downloads page](https://grafana.com/grafana/download?platform=windows) and download the latest Windows installer (e.g., `grafana-*.windows-amd64.msi`).
    *   **Install**: Run the installer and follow the prompts. Grafana will typically be installed to `C:\Program Files\GrafanaLabs\grafana`. It will also set itself up as a Windows service.

3.  **Verify and Access Grafana**:
    *   **Start Grafana Service**: The installer (either `winget` or manual) usually starts the service automatically. If not, open Windows Services (search for `services.msc`), find the service named 'Grafana', and start it manually.
    *   **Access Grafana**: Open your web browser and navigate to `http://localhost:3000`. The default login credentials are `admin` for both username and password.

#### 3. Install Windows Exporter

1.  **Download Windows Exporter**: Go to the [Windows Exporter releases page](https://github.com/prometheus-community/windows_exporter/releases) and download the latest Windows release (e.g., `windows_exporter-*.windows-amd64.zip`).
2.  **Extract**: Extract the contents of the zip file to a directory of your choice, e.g., `C:\windows_exporter`.
3.  **Create Windows Service using NSSM**:
    ```powershell
    nssm install windows_exporter C:\windows_exporter\windows_exporter.exe
    nssm set windows_exporter AppDirectory C:\windows_exporter
    nssm set windows_exporter Description "Prometheus Windows Exporter"
    nssm start windows_exporter
    ```
    *Note: The service name used with NSSM here is `windows_exporter`. Adjust paths if your Windows Exporter installation differs.*

#### 4. Install DaVinci Resolve Custom Exporter

1.  **Install Python Dependencies**:
    ```powershell
    pip install -r 2_Environment/requirements.txt
    ```
2.  **Locate Exporter Script**: The Python script is located at `5_Symbols/davinci_resolve_exporter.py` in this repository.
3.  **Create Windows Service using NSSM**:
    ```powerspowershell
    nssm install DaVinciResolveExporter C:\Python3x\python.exe "C:\projects\PrometheusLocalWorkStation\5_Symbols\davinci_resolve_exporter.py"
    nssm set DaVinciResolveExporter AppDirectory "C:\projects\PrometheusLocalWorkStation\5_Symbols"
    nssm set DaVinciResolveExporter Description "Prometheus DaVinci Resolve Custom Exporter"
    nssm start DaVinciResolveExporter
    ```
    *Note: Replace `C:\Python3x\python.exe` with the actual path to your Python executable.*

### Access the Services

Once all services are running:
-   Prometheus: http://localhost:9090
-   Grafana: http://localhost:3000 (login: admin/admin)
-   Windows Exporter: http://localhost:9182/metrics
-   DaVinci Resolve Exporter: http://localhost:9183/metrics

## Testing

The project includes comprehensive test suites to verify component functionality.

### Test the Metrics Exporter

```bash
# Ensure DaVinci Resolve Exporter is running (as a Windows Service)
python 7_Testing/test_metrics_exporter.py
```

### Test Grafana Connectivity

```bash
# Ensure Grafana and Prometheus are running (as Windows Services)
python 7_Testing/test_grafana_connectivity.py
```

## Dashboard Setup

### Import the DaVinci Resolve Dashboard

1.  Open Grafana at http://localhost:3000
2.  Login with default credentials (`admin`/`admin`)
3.  Navigate to **Configuration → Data Sources**
4.  Click **Add data source** → Select **Prometheus**
5.  Set URL to `http://localhost:9090`
6.  Click **Save & Test**
7.  Navigate to **Dashboards → Import**
8.  Click **Upload JSON file**
9.  Select `7_Testing/davinci_resolve_dashboard.json`
10. Click **Import**

### Dashboard Features

The pre-configured dashboard includes:

- **System Overview**: CPU, memory, and GPU utilization
- **DaVinci Resolve Status**: Process monitoring and resource usage
- **Storage Metrics**: Media storage and cache disk usage
- **Project Information**: Project count and total size
- **Log Monitoring**: Error and warning tracking from DaVinci Resolve logs

## Configuration

### Prometheus Configuration

The Prometheus configuration is located at `C:\Prometheus\prometheus.yml` (assuming your installation path). Key settings:

- Scrape interval: 15 seconds
- Retention period: 30 days
- Maximum storage: 10GB

You will need to ensure your `prometheus.yml` is configured to scrape the native Windows Exporter and DaVinci Resolve Exporter. An example `scrape_configs` section might look like this:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'windows_exporter'
    static_configs:
      - targets: ['localhost:9182']

  - job_name: 'davinci_resolve_exporter'
    static_configs:
      - targets: ['localhost:9183']
```

### DaVinci Resolve Exporter Configuration

The exporter can be configured using environment variables. When running as a service via NSSM, you can set these environment variables using `nssm set <servicename> AppEnvironmentExtra`.

```powershell
# Port (default: 9183)
nssm set DaVinciResolveExporter AppEnvironmentExtra EXPORTER_PORT=9183

# Scrape interval in seconds (default: 30)
nssm set DaVinciResolveExporter AppEnvironmentExtra SCRAPE_INTERVAL=30
```
Then restart the service: `nssm restart DaVinciResolveExporter`.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Grafana UI                     │
│              (http://localhost:3000)            │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              Prometheus Server                  │
│              (http://localhost:9090)            │
└───────┬────────────┬──────────────┬─────────────┘
        │            │              │
        ▼            ▼              ▼
┌──────────┐  ┌─────────────┐  ┌──────────────────┐
│ Windows  │  │   DaVinci   │  │   Prometheus     │
│ Exporter │  │   Resolve   │  │   Self-Monitor   │
│  :9182   │  │  Exporter   │  │      :9183    │
│          │  │             │  │                  │
└──────────┘  └─────────────┘  └──────────────────┘
```

## Troubleshooting

### Common Issues

**Prometheus not starting**
- Check configuration: `C:\Prometheus\prometheus.yml`
- Verify YAML syntax is correct
- Check service logs (Event Viewer) for errors.

**Windows Exporter not collecting GPU metrics**
- Ensure GPU drivers are up to date
- For NVIDIA: Install CUDA toolkit
- For AMD: Ensure AMD drivers with metrics support

**DaVinci Resolve Exporter not finding logs**
- Check DaVinci Resolve installation path
- Default log location: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\logs`
- Verify Python dependencies are installed.
- Check NSSM service logs for errors.

**Grafana dashboard shows no data**
- Verify Prometheus data source is configured correctly in Grafana.
- Check that all exporters and Prometheus are running as Windows services.
- Ensure metrics are being scraped (check Prometheus targets UI at `http://localhost:9090/targets`).

## Development

### Project Structure

```
PrometheusLocalWorkStation/
├── 1_Real/                          # Objectives & Key Results (OKRs)
├── 2_Environment/                   # Roadmap, Use Cases, Environment Setup
│   ├── install_windows.ps1
│   ├── prometheus.yml
│   ├── README.md
│   ├── requirements.txt
│   └── WINDOWS_INSTALL.md
├── 3_UI/                            # Knowledge & Skill Acquisition
│   └── antigravity.md
├── 4_Formula/                       # Guides & Best Practices
├── 5_Symbols/                       # Implementation & Code
│   └── davinci_resolve_exporter.py
├── 6_Semblance/                     # Error Logging & Solutions
├── 7_Testing/                       # Validation & Quality Assurance
│   ├── davinci_resolve_dashboard.json
│   ├── test_grafana_connectivity.py
│   └── test_metrics_exporter.py
└── .gitignore
```

### Running Tests Locally

```bash
# Ensure Python dependencies are installed
pip install -r 2_Environment/requirements.txt

# Ensure Prometheus, Grafana, Windows Exporter, and DaVinci Resolve Exporter are running as Windows services.

# Run all tests
python 7_Testing/test_metrics_exporter.py
python 7_Testing/test_grafana_connectivity.py
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for monitoring DaVinci Resolve workstations.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Review the troubleshooting section above

## Acknowledgments

- [Prometheus](https://prometheus.io/) - Monitoring and alerting toolkit
- [Grafana](https://grafana.com/) - Analytics and monitoring platform
- [Windows Exporter](https://github.com/prometheus-community/windows_exporter) - Windows metrics collector
- [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/) - Video editing software by Blackmagic Design
- [NSSM (Non-Sucking Service Manager)](https://nssm.cc/) - For running applications as Windows services