# Windows Installation Guide - PrometheusLocalWorkStation

This guide provides step-by-step instructions for installing and configuring Prometheus monitoring for DaVinci Resolve on Windows.

## Components to be Installed

### 1. Prometheus (v2.45.0+)
- **Purpose**: Time-series database and monitoring system
- **Download**: https://prometheus.io/download/
- **Installation Path**: `C:\Program Files\Prometheus`

### 2. Windows Exporter (v0.25.0+)
- **Purpose**: Exports Windows system metrics (CPU, Memory, Disk, GPU)
- **Download**: https://github.com/prometheus-community/windows_exporter/releases
- **Installation Path**: Service running on port 9182
- **Metrics Exported**:
  - CPU usage and temperature
  - GPU metrics (NVIDIA/AMD)
  - Disk I/O and storage
  - Memory usage
  - Network statistics

### 3. DaVinci Resolve Custom Exporter
- **Purpose**: Exports DaVinci Resolve specific metrics
- **Location**: `./exporters/davinci_resolve_exporter.py`
- **Port**: 9183
- **Metrics Exported**:
  - Project file locations
  - Render queue status
  - Cache disk usage
  - Log file monitoring
  - Media storage health

### 4. Grafana (v10.0.0+)
- **Purpose**: Visualization and dashboard for metrics
- **Download**: https://grafana.com/grafana/download?platform=windows
- **Installation Path**: `C:\Program Files\GrafanaLabs\grafana`
- **Default Port**: 3000

## Installation Steps

### Step 1: Install Prometheus

```powershell
# Run as Administrator
cd C:\
mkdir "Program Files\Prometheus"
cd "Program Files\Prometheus"

# Download Prometheus (adjust version as needed)
Invoke-WebRequest -Uri "https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.windows-amd64.zip" -OutFile "prometheus.zip"

# Extract
Expand-Archive -Path "prometheus.zip" -DestinationPath "."
Move-Item -Path ".\prometheus-*\*" -Destination "."

# Copy configuration
Copy-Item ".\config\prometheus.yml" -Destination "C:\Program Files\Prometheus\prometheus.yml"
```

### Step 2: Install Windows Exporter

```powershell
# Download Windows Exporter
Invoke-WebRequest -Uri "https://github.com/prometheus-community/windows_exporter/releases/download/v0.25.0/windows_exporter-0.25.0-amd64.msi" -OutFile "windows_exporter.msi"

# Install as service (includes CPU, Memory, Disk, and GPU collectors)
msiexec /i windows_exporter.msi ENABLED_COLLECTORS="cpu,cs,logical_disk,memory,net,os,system,gpu"
```

### Step 3: Install Python and DaVinci Resolve Exporter

```powershell
# Install Python 3.9+
winget install Python.Python.3.11

# Install dependencies
pip install prometheus-client psutil watchdog

# Copy exporter to installation directory
mkdir "C:\Program Files\DaVinciResolveExporter"
Copy-Item ".\exporters\davinci_resolve_exporter.py" -Destination "C:\Program Files\DaVinciResolveExporter\"
```

### Step 4: Install Grafana

```powershell
# Download Grafana
Invoke-WebRequest -Uri "https://dl.grafana.com/oss/release/grafana-10.0.0.windows-amd64.zip" -OutFile "grafana.zip"

# Extract to Program Files
Expand-Archive -Path "grafana.zip" -DestinationPath "C:\Program Files\GrafanaLabs\"

# Install as Windows Service
cd "C:\Program Files\GrafanaLabs\grafana\bin"
.\grafana-server.exe install
Start-Service Grafana
```

### Step 5: Configure Services

All services should be configured to start automatically:

```powershell
# Set services to auto-start
Set-Service -Name "Prometheus" -StartupType Automatic
Set-Service -Name "windows_exporter" -StartupType Automatic
Set-Service -Name "DaVinciResolveExporter" -StartupType Automatic
Set-Service -Name "Grafana" -StartupType Automatic
```

## Running Installation Script

For automated installation, use the provided PowerShell script:

```powershell
# Run as Administrator
cd scripts
.\install_windows.ps1
```

## Verification

After installation, verify all components are running:

```powershell
# Check Prometheus (should return metrics)
Invoke-WebRequest -Uri "http://localhost:9090/metrics"

# Check Windows Exporter (should return system metrics)
Invoke-WebRequest -Uri "http://localhost:9182/metrics"

# Check DaVinci Resolve Exporter (should return custom metrics)
Invoke-WebRequest -Uri "http://localhost:9183/metrics"

# Check Grafana (should show login page)
Start-Process "http://localhost:3000"
```

## Default Ports

| Component | Port | Purpose |
|-----------|------|---------|
| Prometheus | 9090 | Main Prometheus interface |
| Windows Exporter | 9182 | System metrics |
| DaVinci Resolve Exporter | 9183 | DaVinci Resolve metrics |
| Grafana | 3000 | Dashboard interface |

## Grafana Initial Setup

1. Open browser to `http://localhost:3000`
2. Login with default credentials: `admin` / `admin`
3. Add Prometheus as data source:
   - Configuration → Data Sources → Add data source
   - Select "Prometheus"
   - URL: `http://localhost:9090`
   - Click "Save & Test"
4. Import DaVinci Resolve dashboard:
   - Dashboards → Import
   - Upload `./dashboards/davinci_resolve_dashboard.json`

## Troubleshooting

### Prometheus not starting
- Check configuration file: `C:\Program Files\Prometheus\prometheus.yml`
- Check logs: `C:\Program Files\Prometheus\prometheus.log`

### Windows Exporter not collecting GPU metrics
- Ensure GPU drivers are up to date
- For NVIDIA: Install CUDA toolkit
- For AMD: Ensure AMD drivers with metrics support

### DaVinci Resolve Exporter not finding logs
- Check DaVinci Resolve installation path in exporter configuration
- Default log location: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\logs`

## Next Steps

- Configure custom alerts in Prometheus
- Customize Grafana dashboard
- Set up email notifications for critical metrics
- Configure retention policies for metrics data
