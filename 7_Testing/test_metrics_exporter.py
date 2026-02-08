#!/usr/bin/env python3
"""
Test suite for DaVinci Resolve Metrics Exporter

This test verifies that the exporter is working correctly and exposing metrics.
"""

import unittest
import requests
import time
import subprocess
import sys
import os
from pathlib import Path


class TestMetricsExporter(unittest.TestCase):
    """Test cases for the metrics exporter"""
    
    @classmethod
    def setUpClass(cls):
        """Start the exporter before tests"""
        cls.exporter_url = "http://localhost:9183/metrics"
        cls.timeout = 5
        print("Testing Metrics Exporter connectivity...")
    
    def test_01_exporter_is_reachable(self):
        """Test that the exporter endpoint is reachable"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200, 
                           f"Exporter should return 200 OK, got {response.status_code}")
            print("✓ Exporter is reachable")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not reach exporter at {self.exporter_url}: {e}")
    
    def test_02_metrics_format_is_valid(self):
        """Test that metrics are in valid Prometheus format"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Check for basic Prometheus format
            self.assertIn("# HELP", content, "Metrics should contain HELP comments")
            self.assertIn("# TYPE", content, "Metrics should contain TYPE comments")
            print("✓ Metrics format is valid")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_03_davinci_resolve_info_present(self):
        """Test that DaVinci Resolve info metric is present"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            self.assertIn("davinci_resolve_info", content, 
                         "Should expose davinci_resolve_info metric")
            print("✓ DaVinci Resolve info metric present")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_04_process_metrics_present(self):
        """Test that process metrics are present"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Check for key process metrics
            metrics = [
                "davinci_resolve_running",
                "davinci_resolve_cpu_percent",
                "davinci_resolve_memory_bytes"
            ]
            
            for metric in metrics:
                self.assertIn(metric, content, 
                            f"Should expose {metric} metric")
            
            print("✓ Process metrics present")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_05_disk_metrics_present(self):
        """Test that disk metrics are present"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Check for disk metrics
            disk_metrics = [
                "davinci_media_disk_total_bytes",
                "davinci_media_disk_used_bytes",
                "davinci_media_disk_free_bytes",
                "davinci_cache_disk_total_bytes"
            ]
            
            for metric in disk_metrics:
                self.assertIn(metric, content, 
                            f"Should expose {metric} metric")
            
            print("✓ Disk metrics present")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_06_log_metrics_present(self):
        """Test that log metrics are present"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Check for log metrics
            log_metrics = [
                "davinci_log_errors_total",
                "davinci_log_warnings_total",
                "davinci_log_size_bytes"
            ]
            
            for metric in log_metrics:
                self.assertIn(metric, content, 
                            f"Should expose {metric} metric")
            
            print("✓ Log metrics present")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_07_project_metrics_present(self):
        """Test that project metrics are present"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Check for project metrics
            project_metrics = [
                "davinci_project_count",
                "davinci_project_total_size_bytes"
            ]
            
            for metric in project_metrics:
                self.assertIn(metric, content, 
                            f"Should expose {metric} metric")
            
            print("✓ Project metrics present")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")
    
    def test_08_metrics_have_values(self):
        """Test that metrics have actual numeric values"""
        try:
            response = requests.get(self.exporter_url, timeout=self.timeout)
            content = response.text
            
            # Parse lines and check for values
            lines = content.split('\n')
            metric_lines = [line for line in lines if line and not line.startswith('#')]
            
            self.assertGreater(len(metric_lines), 0, 
                             "Should have at least some metric values")
            
            # Check that values are numeric
            for line in metric_lines[:10]:  # Check first 10 metrics
                if ' ' in line:
                    parts = line.rsplit(' ', 1)
                    if len(parts) == 2:
                        value = parts[1]
                        try:
                            float(value)
                        except ValueError:
                            self.fail(f"Metric value should be numeric, got: {value}")
            
            print("✓ Metrics have valid numeric values")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not fetch metrics: {e}")


class TestWindowsExporter(unittest.TestCase):
    """Test cases for Windows Exporter"""
    
    def test_windows_exporter_is_reachable(self):
        """Test that Windows Exporter is reachable"""
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=5)
            self.assertEqual(response.status_code, 200)
            print("✓ Windows Exporter is reachable")
        except requests.exceptions.RequestException:
            self.skipTest("Windows Exporter not running (expected if not on Windows)")
    
    def test_windows_cpu_metrics_present(self):
        """Test that CPU metrics are exposed"""
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=5)
            content = response.text
            self.assertIn("windows_cpu", content)
            print("✓ Windows CPU metrics present")
        except requests.exceptions.RequestException:
            self.skipTest("Windows Exporter not running")
    
    def test_windows_memory_metrics_present(self):
        """Test that memory metrics are exposed"""
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=5)
            content = response.text
            self.assertIn("windows_memory", content)
            print("✓ Windows memory metrics present")
        except requests.exceptions.RequestException:
            self.skipTest("Windows Exporter not running")
    
    def test_windows_disk_metrics_present(self):
        """Test that disk metrics are exposed"""
        try:
            response = requests.get("http://localhost:9182/metrics", timeout=5)
            content = response.text
            self.assertIn("windows_logical_disk", content)
            print("✓ Windows disk metrics present")
        except requests.exceptions.RequestException:
            self.skipTest("Windows Exporter not running")


def main():
    """Run tests"""
    print("=" * 70)
    print("DaVinci Resolve Metrics Exporter Test Suite")
    print("=" * 70)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsExporter))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsExporter))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
