import requests
import sys
from datetime import datetime
import json

class AuthInventoryAPITester:
    def __init__(self, base_url="https://manufactory-data.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Store created IDs for testing
        self.product_id = None
        self.warehouse_id = None
        self.bin_id = None
        
        # Authentication data
        self.session_token = None
        self.user_data = None
        self.admin_session_token = None
        self.admin_user_data = None
        self.test_user_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                self.test_results.append({"test": name, "status": "PASSED", "code": response.status_code})
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.test_results.append({"test": name, "status": "FAILED", "expected": expected_status, "got": response.status_code})
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({"test": name, "status": "ERROR", "error": str(e)})
            return False, {}

    def test_create_product(self):
        """Test creating a product"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Product",
            "POST",
            "products",
            200,
            data={
                "code": f"PROD-{timestamp}",
                "name": f"Test Product {timestamp}",
                "description": "Test product for inventory",
                "unit": "pcs"
            }
        )
        if success and 'id' in response:
            self.product_id = response['id']
            print(f"   Created product ID: {self.product_id}")
            return True
        return False

    def test_get_products(self):
        """Test getting all products"""
        success, response = self.run_test(
            "Get Products",
            "GET",
            "products",
            200
        )
        if success:
            print(f"   Found {len(response)} products")
        return success

    def test_create_warehouse(self):
        """Test creating a warehouse"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Warehouse",
            "POST",
            "warehouses",
            200,
            data={
                "code": f"WH-{timestamp}",
                "name": f"Test Warehouse {timestamp}",
                "location": "Test Location"
            }
        )
        if success and 'id' in response:
            self.warehouse_id = response['id']
            print(f"   Created warehouse ID: {self.warehouse_id}")
            return True
        return False

    def test_get_warehouses(self):
        """Test getting all warehouses"""
        success, response = self.run_test(
            "Get Warehouses",
            "GET",
            "warehouses",
            200
        )
        if success:
            print(f"   Found {len(response)} warehouses")
        return success

    def test_create_bin(self):
        """Test creating a bin"""
        if not self.warehouse_id:
            print("⚠️  Skipping - No warehouse ID available")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Bin",
            "POST",
            "bins",
            200,
            data={
                "warehouse_id": self.warehouse_id,
                "code": f"BIN-{timestamp}",
                "name": f"Test Bin {timestamp}"
            }
        )
        if success and 'id' in response:
            self.bin_id = response['id']
            print(f"   Created bin ID: {self.bin_id}")
            return True
        return False

    def test_get_bins(self):
        """Test getting all bins"""
        success, response = self.run_test(
            "Get Bins",
            "GET",
            "bins",
            200
        )
        if success:
            print(f"   Found {len(response)} bins")
        return success

    def test_get_bins_filtered(self):
        """Test getting bins filtered by warehouse"""
        if not self.warehouse_id:
            print("⚠️  Skipping - No warehouse ID available")
            return False
            
        success, response = self.run_test(
            "Get Bins (Filtered by Warehouse)",
            "GET",
            "bins",
            200,
            params={"warehouse_id": self.warehouse_id}
        )
        if success:
            print(f"   Found {len(response)} bins for warehouse")
        return success

    def test_stock_receipt(self):
        """Test creating a stock receipt (incoming inventory)"""
        if not self.product_id or not self.warehouse_id:
            print("⚠️  Skipping - Missing product or warehouse ID")
            return False
            
        success, response = self.run_test(
            "Create Stock Receipt",
            "POST",
            "stock-moves",
            200,
            data={
                "product_id": self.product_id,
                "move_type": "receipt",
                "to_warehouse_id": self.warehouse_id,
                "to_bin_id": self.bin_id,
                "quantity": 100,
                "reference": "PO-001",
                "notes": "Initial stock receipt"
            }
        )
        return success

    def test_get_inventory(self):
        """Test getting inventory"""
        success, response = self.run_test(
            "Get Inventory",
            "GET",
            "inventory",
            200
        )
        if success:
            print(f"   Found {len(response)} inventory items")
            for item in response:
                if item.get('product_id') == self.product_id:
                    print(f"   Test product quantity: {item.get('quantity')}")
        return success

    def test_get_inventory_filtered_by_product(self):
        """Test getting inventory filtered by product"""
        if not self.product_id:
            print("⚠️  Skipping - No product ID available")
            return False
            
        success, response = self.run_test(
            "Get Inventory (Filtered by Product)",
            "GET",
            "inventory",
            200,
            params={"product_id": self.product_id}
        )
        if success:
            print(f"   Found {len(response)} inventory items for product")
        return success

    def test_get_inventory_filtered_by_warehouse(self):
        """Test getting inventory filtered by warehouse"""
        if not self.warehouse_id:
            print("⚠️  Skipping - No warehouse ID available")
            return False
            
        success, response = self.run_test(
            "Get Inventory (Filtered by Warehouse)",
            "GET",
            "inventory",
            200,
            params={"warehouse_id": self.warehouse_id}
        )
        if success:
            print(f"   Found {len(response)} inventory items for warehouse")
        return success

    def test_stock_issue(self):
        """Test creating a stock issue (outgoing inventory)"""
        if not self.product_id or not self.warehouse_id:
            print("⚠️  Skipping - Missing product or warehouse ID")
            return False
            
        success, response = self.run_test(
            "Create Stock Issue",
            "POST",
            "stock-moves",
            200,
            data={
                "product_id": self.product_id,
                "move_type": "issue",
                "from_warehouse_id": self.warehouse_id,
                "from_bin_id": self.bin_id,
                "quantity": 20,
                "reference": "SO-001",
                "notes": "Sales order fulfillment"
            }
        )
        return success

    def test_inventory_adjustment(self):
        """Test creating an inventory adjustment"""
        if not self.product_id or not self.warehouse_id:
            print("⚠️  Skipping - Missing product or warehouse ID")
            return False
            
        success, response = self.run_test(
            "Create Inventory Adjustment",
            "POST",
            "adjustments",
            200,
            data={
                "product_id": self.product_id,
                "warehouse_id": self.warehouse_id,
                "bin_id": self.bin_id,
                "quantity_change": 5,
                "reason": "Physical count correction"
            }
        )
        return success

    def test_get_stock_moves(self):
        """Test getting stock moves"""
        success, response = self.run_test(
            "Get Stock Moves",
            "GET",
            "stock-moves",
            200
        )
        if success:
            print(f"   Found {len(response)} stock moves")
        return success

    def test_get_adjustments(self):
        """Test getting adjustments"""
        success, response = self.run_test(
            "Get Adjustments",
            "GET",
            "adjustments",
            200
        )
        if success:
            print(f"   Found {len(response)} adjustments")
        return success

    def verify_inventory_calculation(self):
        """Verify that inventory is correctly calculated after all operations"""
        if not self.product_id:
            print("⚠️  Skipping - No product ID available")
            return False
            
        print(f"\n🔍 Verifying Inventory Calculation...")
        success, response = self.run_test(
            "Verify Final Inventory",
            "GET",
            "inventory",
            200,
            params={"product_id": self.product_id}
        )
        
        if success and len(response) > 0:
            item = response[0]
            quantity = item.get('quantity', 0)
            # Expected: 100 (receipt) - 20 (issue) + 5 (adjustment) = 85
            expected = 85
            if quantity == expected:
                print(f"✅ Inventory calculation correct: {quantity} (expected {expected})")
                return True
            else:
                print(f"❌ Inventory calculation incorrect: {quantity} (expected {expected})")
                return False
        return False

def main():
    print("=" * 60)
    print("INVENTORY MANAGEMENT SYSTEM - API TESTING")
    print("=" * 60)
    
    tester = InventoryAPITester()
    
    # Test sequence following the workflow
    print("\n📦 TESTING PRODUCTS")
    print("-" * 60)
    tester.test_create_product()
    tester.test_get_products()
    
    print("\n🏢 TESTING WAREHOUSES")
    print("-" * 60)
    tester.test_create_warehouse()
    tester.test_get_warehouses()
    
    print("\n📍 TESTING BINS")
    print("-" * 60)
    tester.test_create_bin()
    tester.test_get_bins()
    tester.test_get_bins_filtered()
    
    print("\n📥 TESTING STOCK RECEIPT")
    print("-" * 60)
    tester.test_stock_receipt()
    
    print("\n📊 TESTING INVENTORY RETRIEVAL")
    print("-" * 60)
    tester.test_get_inventory()
    tester.test_get_inventory_filtered_by_product()
    tester.test_get_inventory_filtered_by_warehouse()
    
    print("\n📤 TESTING STOCK ISSUE")
    print("-" * 60)
    tester.test_stock_issue()
    
    print("\n🔧 TESTING INVENTORY ADJUSTMENT")
    print("-" * 60)
    tester.test_inventory_adjustment()
    
    print("\n📜 TESTING HISTORY")
    print("-" * 60)
    tester.test_get_stock_moves()
    tester.test_get_adjustments()
    
    print("\n✓ VERIFYING INVENTORY CALCULATIONS")
    print("-" * 60)
    tester.verify_inventory_calculation()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
