# Grafana PC Performance Monitor Dashboard - No Data Issue

**Problem:** The "PC Performance Monitor" Grafana dashboard (`http://localhost:3000/d/pc_monitor_01/pc-performance-monitor`) does not display any data. Panels show "No Data" or similar errors.

**Cause:** The metrics used by this dashboard (`windows_cpu_time_total`, `windows_os_physical_memory_free_bytes`, etc.) are provided by the **Windows Exporter**. According to the `component_status_report.txt`, the Windows Exporter is currently "Not Installed" or not running as a service.

Prometheus, which Grafana relies on, scrapes these metrics from the Windows Exporter. If the Windows Exporter is not active, it's not exposing any metrics, and thus Prometheus cannot scrape them. Without data in Prometheus, Grafana cannot display anything on the dashboard.

**Solution:**
1.  **Install the Windows Exporter**: Follow the instructions provided in the `2_Environment/README.md` under the section "3. Install Windows Exporter". This involves downloading the exporter, extracting it, and creating a Windows service for it using NSSM.
2.  **Ensure Prometheus Configuration**: Verify that your Prometheus configuration (`prometheus.yml`) is correctly set up to scrape the `windows_exporter` on port `9182`. Refer to the "Prometheus Configuration" section in `2_Environment/README.md`.
3.  **Start the Windows Exporter Service**: After installation, ensure the `windows_exporter` service is running in Windows Services (`services.msc`).
4.  **Check Prometheus Targets**: Once the Windows Exporter is running, check the Prometheus UI at `http://localhost:9090/targets` to confirm that Prometheus is successfully scraping metrics from `localhost:9182`.

After completing these steps, the "PC Performance Monitor" dashboard in Grafana should begin to populate with data.