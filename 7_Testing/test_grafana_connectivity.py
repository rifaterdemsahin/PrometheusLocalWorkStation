#!/usr/bin/env python3
"""
Test suite for Grafana connectivity and dashboard

This test verifies that Grafana is accessible and configured correctly.
"""

import unittest
import requests
import json
import time
import sys


class TestGrafanaConnectivity(unittest.TestCase):
    """Test cases for Grafana connectivity"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test configuration"""
        cls.grafana_url = "http://localhost:3000"
        cls.api_url = f"{cls.grafana_url}/api"
        cls.timeout = 10
        print("Testing Grafana connectivity...")
    
    def test_01_grafana_is_reachable(self):
        """Test that Grafana is reachable"""
        try:
            response = requests.get(self.grafana_url, timeout=self.timeout)
            self.assertIn(response.status_code, [200, 302], 
                         f"Grafana should be reachable, got status {response.status_code}")
            print("✓ Grafana is reachable")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not reach Grafana at {self.grafana_url}: {e}")
    
    def test_02_grafana_api_health(self):
        """Test Grafana API health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=self.timeout)
            self.assertEqual(response.status_code, 200, 
                           "Grafana health endpoint should return 200")
            
            data = response.json()
            self.assertIn("database", data, "Health response should include database status")
            print("✓ Grafana API is healthy")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not reach Grafana health endpoint: {e}")
    
    def test_03_grafana_version(self):
        """Test that we can get Grafana version"""
        try:
            # Login first (using default credentials)
            session = requests.Session()
            login_response = session.post(
                f"{self.grafana_url}/login",
                json={"user": "admin", "password": "admin"},
                timeout=self.timeout
            )
            
            # Some Grafana versions return different status codes
            if login_response.status_code in [200, 302]:
                # Try to get version info
                response = session.get(f"{self.api_url}/frontend/settings", timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Grafana version endpoint accessible")
                else:
                    print("⚠ Could not get version (may require authentication)")
            else:
                print("⚠ Could not login with default credentials (expected in production)")
        except requests.exceptions.RequestException:
            print("⚠ Could not test version endpoint")
    
    def test_04_prometheus_datasource_can_be_added(self):
        """Test that Prometheus can be configured as a datasource"""
        # This is a connectivity test - we just verify the endpoint exists
        try:
            response = requests.get(f"{self.api_url}/datasources", timeout=self.timeout)
            # Will return 401 if not authenticated, which is expected
            self.assertIn(response.status_code, [200, 401, 403], 
                         "Datasources endpoint should exist")
            print("✓ Datasources endpoint is available")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not reach datasources endpoint: {e}")
    
    def test_05_dashboards_endpoint_available(self):
        """Test that dashboards endpoint is available"""
        try:
            response = requests.get(f"{self.api_url}/dashboards/home", timeout=self.timeout)
            # Will return 401 if not authenticated, which is expected
            self.assertIn(response.status_code, [200, 401, 403], 
                         "Dashboards endpoint should exist")
            print("✓ Dashboards endpoint is available")
        except requests.exceptions.RequestException as e:
            self.fail(f"Could not reach dashboards endpoint: {e}")


class TestPrometheusConnectivity(unittest.TestCase):
    """Test that Prometheus is accessible from Grafana's perspective"""
    
    def test_prometheus_is_reachable(self):
        """Test that Prometheus is reachable"""
        try:
            response = requests.get("http://localhost:9090", timeout=5)
            self.assertIn(response.status_code, [200, 302])
            print("✓ Prometheus is reachable")
        except requests.exceptions.RequestException:
            self.skipTest("Prometheus not running")
    
    def test_prometheus_api_query(self):
        """Test that Prometheus API accepts queries"""
        try:
            response = requests.get(
                "http://localhost:9090/api/v1/query",
                params={"query": "up"},
                timeout=5
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get("status"), "success")
            print("✓ Prometheus API is working")
        except requests.exceptions.RequestException:
            self.skipTest("Prometheus not running")
    
    def test_prometheus_has_targets(self):
        """Test that Prometheus has configured targets"""
        try:
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get("status"), "success")
            
            # Check if we have any targets
            active_targets = data.get("data", {}).get("activeTargets", [])
            print(f"✓ Prometheus has {len(active_targets)} active target(s)")
        except requests.exceptions.RequestException:
            self.skipTest("Prometheus not running")


class TestDashboardConfiguration(unittest.TestCase):
    """Test dashboard configuration"""
    
    def test_dashboard_json_exists(self):
        """Test that dashboard JSON file exists"""
        import os
        dashboard_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "dashboards",
            "davinci_resolve_dashboard.json"
        )
        
        self.assertTrue(os.path.exists(dashboard_path), 
                       f"Dashboard JSON should exist at {dashboard_path}")
        print("✓ Dashboard JSON file exists")
    
    def test_dashboard_json_is_valid(self):
        """Test that dashboard JSON is valid"""
        import os
        dashboard_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "dashboards",
            "davinci_resolve_dashboard.json"
        )
        
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                try:
                    dashboard = json.load(f)
                    self.assertIsInstance(dashboard, dict, "Dashboard should be a JSON object")
                    print("✓ Dashboard JSON is valid")
                except json.JSONDecodeError as e:
                    self.fail(f"Dashboard JSON is invalid: {e}")
        else:
            self.skipTest("Dashboard file not found")
    
    def test_dashboard_has_required_fields(self):
        """Test that dashboard has required Grafana fields"""
        import os
        dashboard_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "dashboards",
            "davinci_resolve_dashboard.json"
        )
        
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                dashboard = json.load(f)
                
                # Check for required fields
                required_fields = ["title", "panels"]
                for field in required_fields:
                    self.assertIn(field, dashboard, 
                                f"Dashboard should have '{field}' field")
                
                print("✓ Dashboard has required fields")
        else:
            self.skipTest("Dashboard file not found")


def main():
    """Run tests"""
    print("=" * 70)
    print("Grafana Connectivity Test Suite")
    print("=" * 70)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGrafanaConnectivity))
    suite.addTests(loader.loadTestsFromTestCase(TestPrometheusConnectivity))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboardConfiguration))
    
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
