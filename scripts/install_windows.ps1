# Windows Installation Script for PrometheusLocalWorkStation
# This script automates the installation of Prometheus, Windows Exporter, Grafana, and DaVinci Resolve Exporter
# 
# Run as Administrator: powershell -ExecutionPolicy Bypass -File .\install_windows.ps1

param(
    [switch]$SkipDownloads = $false,
    [switch]$SkipServices = $false,
    [string]$InstallPath = "C:\Program Files"
)

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PrometheusLocalWorkStation Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Component versions
$PROMETHEUS_VERSION = "2.45.0"
$WINDOWS_EXPORTER_VERSION = "0.25.0"
$GRAFANA_VERSION = "10.0.0"

Write-Host "Components to be installed:" -ForegroundColor Green
Write-Host "  - Prometheus v$PROMETHEUS_VERSION" -ForegroundColor White
Write-Host "  - Windows Exporter v$WINDOWS_EXPORTER_VERSION" -ForegroundColor White
Write-Host "  - Grafana v$GRAFANA_VERSION" -ForegroundColor White
Write-Host "  - DaVinci Resolve Custom Exporter" -ForegroundColor White
Write-Host ""

# Create temporary directory
$TempDir = "$env:TEMP\prometheus_install"
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Write-Host "Using temporary directory: $TempDir" -ForegroundColor Gray
Write-Host ""

# Function to download file with progress
function Download-File {
    param(
        [string]$Url,
        [string]$Output
    )
    
    Write-Host "Downloading: $Url" -ForegroundColor Yellow
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $Url -OutFile $Output -UseBasicParsing
        $ProgressPreference = 'Continue'
        Write-Host "  ✓ Downloaded successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to install Prometheus
function Install-Prometheus {
    Write-Host "Installing Prometheus..." -ForegroundColor Cyan
    
    $PrometheusPath = "$InstallPath\Prometheus"
    $DownloadUrl = "https://github.com/prometheus/prometheus/releases/download/v$PROMETHEUS_VERSION/prometheus-$PROMETHEUS_VERSION.windows-amd64.zip"
    $ZipFile = "$TempDir\prometheus.zip"
    
    if (-not $SkipDownloads) {
        if (-not (Download-File -Url $DownloadUrl -Output $ZipFile)) {
            return $false
        }
    }
    
    # Extract
    Write-Host "Extracting Prometheus..." -ForegroundColor Yellow
    if (Test-Path $PrometheusPath) {
        Remove-Item -Path $PrometheusPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $PrometheusPath -Force | Out-Null
    Expand-Archive -Path $ZipFile -DestinationPath $TempDir -Force
    
    # Move files
    $ExtractedPath = Get-ChildItem -Path $TempDir -Filter "prometheus-*" -Directory | Select-Object -First 1
    Get-ChildItem -Path $ExtractedPath.FullName | Move-Item -Destination $PrometheusPath -Force
    
    # Copy configuration
    $ConfigSource = Join-Path $PSScriptRoot "..\config\prometheus.yml"
    if (Test-Path $ConfigSource) {
        Copy-Item -Path $ConfigSource -Destination "$PrometheusPath\prometheus.yml" -Force
        Write-Host "  ✓ Configuration copied" -ForegroundColor Green
    }
    
    Write-Host "  ✓ Prometheus installed to $PrometheusPath" -ForegroundColor Green
    return $true
}

# Function to install Windows Exporter
function Install-WindowsExporter {
    Write-Host "Installing Windows Exporter..." -ForegroundColor Cyan
    
    $DownloadUrl = "https://github.com/prometheus-community/windows_exporter/releases/download/v$WINDOWS_EXPORTER_VERSION/windows_exporter-$WINDOWS_EXPORTER_VERSION-amd64.msi"
    $MsiFile = "$TempDir\windows_exporter.msi"
    
    if (-not $SkipDownloads) {
        if (-not (Download-File -Url $DownloadUrl -Output $MsiFile)) {
            return $false
        }
    }
    
    # Install MSI with collectors enabled
    Write-Host "Installing Windows Exporter service..." -ForegroundColor Yellow
    $Arguments = @(
        "/i"
        "`"$MsiFile`""
        "ENABLED_COLLECTORS=cpu,cs,logical_disk,memory,net,os,system"
        "/quiet"
        "/norestart"
    )
    
    Start-Process -FilePath "msiexec.exe" -ArgumentList $Arguments -Wait -NoNewWindow
    
    Write-Host "  ✓ Windows Exporter installed" -ForegroundColor Green
    return $true
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    
    # Check if Python is installed
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "  ! Python not found. Please install Python 3.9 or later" -ForegroundColor Yellow
        Write-Host "    Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
    
    # Install required packages
    Write-Host "Installing pip packages..." -ForegroundColor Yellow
    $packages = @("prometheus-client", "psutil", "watchdog")
    
    foreach ($package in $packages) {
        python -m pip install $package --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Installed $package" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to install $package" -ForegroundColor Red
        }
    }
    
    return $true
}

# Function to install DaVinci Resolve Exporter
function Install-DaVinciExporter {
    Write-Host "Installing DaVinci Resolve Exporter..." -ForegroundColor Cyan
    
    $ExporterPath = "$InstallPath\DaVinciResolveExporter"
    New-Item -ItemType Directory -Path $ExporterPath -Force | Out-Null
    
    # Copy exporter script
    $ExporterSource = Join-Path $PSScriptRoot "..\exporters\davinci_resolve_exporter.py"
    if (Test-Path $ExporterSource) {
        Copy-Item -Path $ExporterSource -Destination "$ExporterPath\davinci_resolve_exporter.py" -Force
        Write-Host "  ✓ Exporter copied to $ExporterPath" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Exporter source not found at $ExporterSource" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to install Grafana
function Install-Grafana {
    Write-Host "Installing Grafana..." -ForegroundColor Cyan
    
    $GrafanaPath = "$InstallPath\GrafanaLabs\grafana"
    $DownloadUrl = "https://dl.grafana.com/oss/release/grafana-$GRAFANA_VERSION.windows-amd64.zip"
    $ZipFile = "$TempDir\grafana.zip"
    
    if (-not $SkipDownloads) {
        if (-not (Download-File -Url $DownloadUrl -Output $ZipFile)) {
            return $false
        }
    }
    
    # Extract
    Write-Host "Extracting Grafana..." -ForegroundColor Yellow
    if (Test-Path "$InstallPath\GrafanaLabs") {
        Remove-Item -Path "$InstallPath\GrafanaLabs" -Recurse -Force
    }
    New-Item -ItemType Directory -Path "$InstallPath\GrafanaLabs" -Force | Out-Null
    Expand-Archive -Path $ZipFile -DestinationPath "$InstallPath\GrafanaLabs" -Force
    
    # Rename directory
    $ExtractedPath = Get-ChildItem -Path "$InstallPath\GrafanaLabs" -Filter "grafana-*" -Directory | Select-Object -First 1
    if ($ExtractedPath) {
        Move-Item -Path $ExtractedPath.FullName -Destination $GrafanaPath -Force
    }
    
    Write-Host "  ✓ Grafana installed to $GrafanaPath" -ForegroundColor Green
    return $true
}

# Function to create Windows Services
function Create-Services {
    if ($SkipServices) {
        Write-Host "Skipping service creation (--SkipServices flag set)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Creating Windows Services..." -ForegroundColor Cyan
    
    # Prometheus Service
    $PrometheusExe = "$InstallPath\Prometheus\prometheus.exe"
    if (Test-Path $PrometheusExe) {
        Write-Host "Creating Prometheus service..." -ForegroundColor Yellow
        New-Service -Name "Prometheus" -BinaryPathName "`"$PrometheusExe`" --config.file=`"$InstallPath\Prometheus\prometheus.yml`" --storage.tsdb.path=`"$InstallPath\Prometheus\data`"" -DisplayName "Prometheus Monitoring" -StartupType Automatic -ErrorAction SilentlyContinue
        Write-Host "  ✓ Prometheus service created" -ForegroundColor Green
    }
    
    # DaVinci Resolve Exporter Service (using NSSM or similar would be better in production)
    Write-Host "  ! DaVinci Resolve Exporter service requires manual setup" -ForegroundColor Yellow
    Write-Host "    Run: python `"$InstallPath\DaVinciResolveExporter\davinci_resolve_exporter.py`"" -ForegroundColor Gray
    
    # Grafana Service
    $GrafanaExe = "$InstallPath\GrafanaLabs\grafana\bin\grafana-server.exe"
    if (Test-Path $GrafanaExe) {
        Write-Host "Creating Grafana service..." -ForegroundColor Yellow
        & $GrafanaExe install -config "$InstallPath\GrafanaLabs\grafana\conf\defaults.ini"
        Write-Host "  ✓ Grafana service created" -ForegroundColor Green
    }
}

# Function to start services
function Start-Services {
    Write-Host "Starting services..." -ForegroundColor Cyan
    
    $services = @("Prometheus", "windows_exporter", "Grafana")
    
    foreach ($service in $services) {
        try {
            $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
            if ($svc) {
                Start-Service -Name $service -ErrorAction SilentlyContinue
                Write-Host "  ✓ Started $service" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ! Could not start $service" -ForegroundColor Yellow
        }
    }
}

# Function to verify installation
function Test-Installation {
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Cyan
    
    $endpoints = @{
        "Prometheus" = "http://localhost:9090"
        "Windows Exporter" = "http://localhost:9182/metrics"
        "DaVinci Resolve Exporter" = "http://localhost:9183/metrics"
        "Grafana" = "http://localhost:3000"
    }
    
    Start-Sleep -Seconds 5
    
    foreach ($endpoint in $endpoints.GetEnumerator()) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Value -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            Write-Host "  ✓ $($endpoint.Key) is running" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ $($endpoint.Key) is not accessible" -ForegroundColor Red
        }
    }
}

# Main installation process
Write-Host "Starting installation..." -ForegroundColor Cyan
Write-Host ""

$success = $true

# Install components
if (Install-Prometheus) { } else { $success = $false }
if (Install-WindowsExporter) { } else { $success = $false }
if (Install-PythonDependencies) { } else { $success = $false }
if (Install-DaVinciExporter) { } else { $success = $false }
if (Install-Grafana) { } else { $success = $false }

# Create and start services
if ($success) {
    Create-Services
    Start-Services
    Test-Installation
}

# Cleanup
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Gray
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the services at:" -ForegroundColor White
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Gray
Write-Host "  Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open Grafana and add Prometheus as a data source" -ForegroundColor Gray
Write-Host "  2. Import the DaVinci Resolve dashboard from dashboards/davinci_resolve_dashboard.json" -ForegroundColor Gray
Write-Host "  3. Start DaVinci Resolve Exporter manually or as a service" -ForegroundColor Gray
Write-Host ""
