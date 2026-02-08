# PrometheusLocalWorkStation

Comprehensive monitoring solution for DaVinci Resolve workstations using Prometheus and Grafana.

## Overview

This project provides a complete monitoring stack for Windows workstations running DaVinci Resolve, including:

- **System Metrics**: CPU, GPU, Memory, and Disk usage
- **DaVinci Resolve Metrics**: Process monitoring, project tracking, and log analysis
- **Real-time Dashboards**: Pre-configured Grafana dashboards for visualization
- **Automated Installation**: PowerShell scripts for easy Windows deployment

## Components

### Installed Components

1. **Prometheus** (v2.45.0+) - Time-series database and monitoring system
2. **Windows Exporter** (v0.25.0+) - System metrics collector for Windows
3. **DaVinci Resolve Custom Exporter** - Custom metrics for DaVinci Resolve
4. **Grafana** (v10.0.0+) - Dashboard and visualization platform

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

## Quick Start

### Windows Installation

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/rifaterdemsahin/PrometheusLocalWorkStation.git
   cd PrometheusLocalWorkStation
   ```

2. **Run the installation script as Administrator**:
   ```powershell
   cd scripts
   .\install_windows.ps1
   ```

3. **Access the services**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (login: admin/admin)
   - Windows Exporter: http://localhost:9182/metrics
   - DaVinci Resolve Exporter: http://localhost:9183/metrics

### Manual Installation

For detailed manual installation steps, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md).

## Testing

The project includes comprehensive test suites to verify component functionality.

### Test the Metrics Exporter

```bash
# Install dependencies
pip install -r requirements.txt

# Start the DaVinci Resolve Exporter
python exporters/davinci_resolve_exporter.py

# In another terminal, run tests
python tests/test_metrics_exporter.py
```

### Test Grafana Connectivity

```bash
# Ensure Grafana is running
# Run Grafana tests
python tests/test_grafana_connectivity.py
```

## Dashboard Setup

### Import the DaVinci Resolve Dashboard

1. Open Grafana at http://localhost:3000
2. Login with default credentials (admin/admin)
3. Navigate to **Configuration → Data Sources**
4. Click **Add data source** → Select **Prometheus**
5. Set URL to `http://localhost:9090`
6. Click **Save & Test**
7. Navigate to **Dashboards → Import**
8. Click **Upload JSON file**
9. Select `dashboards/davinci_resolve_dashboard.json`
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

The Prometheus configuration is located at `config/prometheus.yml`. Key settings:

- Scrape interval: 15 seconds
- Retention period: 30 days
- Maximum storage: 10GB

### DaVinci Resolve Exporter Configuration

The exporter can be configured using environment variables:

```bash
# Port (default: 9183)
set EXPORTER_PORT=9183

# Scrape interval in seconds (default: 30)
set SCRAPE_INTERVAL=30

# Run the exporter
python exporters/davinci_resolve_exporter.py
```

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
│  :9182   │  │  Exporter   │  │      :9090       │
│          │  │    :9183    │  │                  │
└──────────┘  └─────────────┘  └──────────────────┘
```

## Troubleshooting

### Common Issues

**Prometheus not starting**
- Check configuration: `C:\Program Files\Prometheus\prometheus.yml`
- Verify YAML syntax is correct
- Check logs for errors

**Windows Exporter not collecting GPU metrics**
- Ensure GPU drivers are up to date
- For NVIDIA: Install CUDA toolkit
- For AMD: Ensure AMD drivers with metrics support

**DaVinci Resolve Exporter not finding logs**
- Check DaVinci Resolve installation path
- Default log location: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\logs`
- Verify Python dependencies are installed

**Grafana dashboard shows no data**
- Verify Prometheus data source is configured correctly
- Check that all exporters are running
- Ensure metrics are being scraped (check Prometheus targets)

## Development

### Project Structure

```
PrometheusLocalWorkStation/
├── config/                          # Configuration files
│   └── prometheus.yml              # Prometheus configuration
├── dashboards/                      # Grafana dashboards
│   └── davinci_resolve_dashboard.json
├── exporters/                       # Custom exporters
│   └── davinci_resolve_exporter.py # DaVinci Resolve metrics
├── scripts/                         # Installation scripts
│   └── install_windows.ps1         # Windows installer
├── tests/                           # Test suites
│   ├── test_metrics_exporter.py    # Exporter tests
│   └── test_grafana_connectivity.py # Grafana tests
├── requirements.txt                 # Python dependencies
├── WINDOWS_INSTALL.md              # Detailed installation guide
└── README.md                        # This file
```

### Running Tests Locally

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start all services
# - Prometheus
# - Windows Exporter
# - DaVinci Resolve Exporter
# - Grafana

# Run all tests
python tests/test_metrics_exporter.py
python tests/test_grafana_connectivity.py
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for monitoring DaVinci Resolve workstations.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed setup instructions
- Review the troubleshooting section above

## Acknowledgments

- [Prometheus](https://prometheus.io/) - Monitoring and alerting toolkit
- [Grafana](https://grafana.com/) - Analytics and monitoring platform
- [Windows Exporter](https://github.com/prometheus-community/windows_exporter) - Windows metrics collector
- [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/) - Video editing software by Blackmagic Design
