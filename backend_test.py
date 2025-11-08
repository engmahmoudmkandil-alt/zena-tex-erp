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
        self.test_user_email = None
        self.admin_user_email = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_token=None, cookies=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if provided
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, cookies=cookies)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, cookies=cookies)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, params=params, cookies=cookies)

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

    # ========== AUTHENTICATION TESTS ==========
    
    def test_register_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        self.test_user_email = f"test.user.{timestamp}@example.com"
        success, response = self.run_test(
            "Register User",
            "POST",
            "auth/register",
            200,
            data={
                "email": self.test_user_email,
                "password": "TestPass123!",
                "name": f"Test User {timestamp}",
                "phone": "+1234567890",
                "role": "Inventory Officer"
            }
        )
        if success and 'user_id' in response:
            self.test_user_id = response['user_id']
            print(f"   Created user ID: {self.test_user_id}")
            print(f"   Email: {self.test_user_email}")
        return success

    def test_register_admin_user(self):
        """Test admin user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        self.admin_user_email = f"admin.user.{timestamp}@example.com"
        success, response = self.run_test(
            "Register Admin User",
            "POST",
            "auth/register",
            200,
            data={
                "email": self.admin_user_email,
                "password": "AdminPass123!",
                "name": f"Admin User {timestamp}",
                "phone": "+1234567891",
                "role": "Admin"
            }
        )
        if success:
            print(f"   Email: {self.admin_user_email}")
        return success

    def test_login_user(self):
        """Test user login"""
        if not self.test_user_email:
            print("⚠️  Skipping - No test user email available")
            return False
            
        success, response = self.run_test(
            "Login User",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": "TestPass123!"
            }
        )
        if success and 'session_token' in response:
            self.session_token = response['session_token']
            self.user_data = response['user']
            print(f"   Session token: {self.session_token[:20]}...")
            print(f"   User role: {self.user_data['role']}")
        return success

    def test_login_admin_user(self):
        """Test admin login"""
        if not self.admin_user_email:
            print("⚠️  Skipping - No admin user email available")
            return False
            
        success, response = self.run_test(
            "Login Admin User",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.admin_user_email,
                "password": "AdminPass123!"
            }
        )
        if success and 'session_token' in response:
            self.admin_session_token = response['session_token']
            self.admin_user_data = response['user']
            print(f"   Admin session token: {self.admin_session_token[:20]}...")
            print(f"   Admin role: {self.admin_user_data['role']}")
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   User: {response.get('name')} ({response.get('role')})")
        return success

    def test_logout(self):
        """Test user logout"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Logout User",
            "POST",
            "auth/logout",
            200,
            auth_token=self.session_token
        )
        return success

    def test_protected_route_without_auth(self):
        """Test accessing protected route without authentication"""
        success, response = self.run_test(
            "Access Protected Route (No Auth)",
            "GET",
            "products",
            401  # Should fail with 401
        )
        return success

    def test_user_management_access_denied(self):
        """Test that non-admin users cannot access user management"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "User Management Access (Non-Admin)",
            "GET",
            "users",
            403,  # Should fail with 403 Forbidden
            auth_token=self.session_token
        )
        return success

    def test_user_management_admin_access(self):
        """Test that admin users can access user management"""
        if not self.admin_session_token:
            print("⚠️  Skipping - No admin session token available")
            return False
            
        success, response = self.run_test(
            "User Management Access (Admin)",
            "GET",
            "users",
            200,
            auth_token=self.admin_session_token
        )
        if success:
            print(f"   Found {len(response)} users")
        return success

    def test_audit_logs_access(self):
        """Test audit logs access (Admin, Accountant, CEO/Viewer)"""
        if not self.admin_session_token:
            print("⚠️  Skipping - No admin session token available")
            return False
            
        success, response = self.run_test(
            "Audit Logs Access (Admin)",
            "GET",
            "audit-logs",
            200,
            auth_token=self.admin_session_token
        )
        if success:
            print(f"   Found {len(response)} audit logs")
        return success

    def test_role_update(self):
        """Test updating user role (Admin only)"""
        if not self.admin_session_token or not self.test_user_id:
            print("⚠️  Skipping - No admin session or test user ID available")
            return False
            
        # Test changing role to Production Manager
        success, response = self.run_test(
            "Update User Role to Production Manager",
            "PATCH",
            f"users/{self.test_user_id}/role",
            200,
            params={"role": "Production Manager"},
            auth_token=self.admin_session_token
        )
        
        if success:
            # Change role back to Inventory Officer for subsequent tests
            success2, response2 = self.run_test(
                "Update User Role back to Inventory Officer",
                "PATCH",
                f"users/{self.test_user_id}/role",
                200,
                params={"role": "Inventory Officer"},
                auth_token=self.admin_session_token
            )
            return success2
        
        return success

    # ========== INVENTORY TESTS (WITH AUTH) ==========
    
    def test_create_product(self):
        """Test creating a product (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Product (Authenticated)",
            "POST",
            "products",
            200,
            data={
                "code": f"PROD-{timestamp}",
                "name": f"Test Product {timestamp}",
                "description": "Test product for inventory",
                "unit": "pcs"
            },
            auth_token=self.session_token
        )
        if success and 'id' in response:
            self.product_id = response['id']
            print(f"   Created product ID: {self.product_id}")
            return True
        return False

    def test_get_products(self):
        """Test getting all products (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Products (Authenticated)",
            "GET",
            "products",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} products")
        return success

    def test_create_warehouse(self):
        """Test creating a warehouse (requires auth) - using admin token"""
        if not self.admin_session_token:
            print("⚠️  Skipping - No admin session token available")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Warehouse (Admin)",
            "POST",
            "warehouses",
            200,
            data={
                "code": f"WH-{timestamp}",
                "name": f"Test Warehouse {timestamp}",
                "location": "Test Location"
            },
            auth_token=self.admin_session_token
        )
        if success and 'id' in response:
            self.warehouse_id = response['id']
            print(f"   Created warehouse ID: {self.warehouse_id}")
            return True
        return False

    def test_get_warehouses(self):
        """Test getting all warehouses (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Warehouses (Authenticated)",
            "GET",
            "warehouses",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} warehouses")
        return success

    def test_create_bin(self):
        """Test creating a bin (requires auth) - using admin token"""
        if not self.warehouse_id or not self.admin_session_token:
            print("⚠️  Skipping - No warehouse ID or admin session token available")
            return False
            
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Bin (Admin)",
            "POST",
            "bins",
            200,
            data={
                "warehouse_id": self.warehouse_id,
                "code": f"BIN-{timestamp}",
                "name": f"Test Bin {timestamp}"
            },
            auth_token=self.admin_session_token
        )
        if success and 'id' in response:
            self.bin_id = response['id']
            print(f"   Created bin ID: {self.bin_id}")
            return True
        return False

    def test_get_bins(self):
        """Test getting all bins (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Bins (Authenticated)",
            "GET",
            "bins",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} bins")
        return success

    def test_get_bins_filtered(self):
        """Test getting bins filtered by warehouse (requires auth)"""
        if not self.warehouse_id or not self.session_token:
            print("⚠️  Skipping - No warehouse ID or session token available")
            return False
            
        success, response = self.run_test(
            "Get Bins Filtered (Authenticated)",
            "GET",
            "bins",
            200,
            params={"warehouse_id": self.warehouse_id},
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} bins for warehouse")
        return success

    def test_stock_receipt(self):
        """Test creating a stock receipt (requires auth) - using regular user token"""
        if not self.product_id or not self.warehouse_id or not self.session_token:
            print("⚠️  Skipping - Missing product/warehouse ID or session token")
            return False
        
        # First check current user to see the role
        print(f"   User role from login: {self.user_data.get('role') if self.user_data else 'Unknown'}")
            
        success, response = self.run_test(
            "Create Stock Receipt (Inventory Officer)",
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
            },
            auth_token=self.session_token
        )
        return success

    def test_get_inventory(self):
        """Test getting inventory (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Inventory (Authenticated)",
            "GET",
            "inventory",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} inventory items")
            for item in response:
                if item.get('product_id') == self.product_id:
                    print(f"   Test product quantity: {item.get('quantity')}")
        return success

    def test_get_inventory_filtered_by_product(self):
        """Test getting inventory filtered by product (requires auth)"""
        if not self.product_id or not self.session_token:
            print("⚠️  Skipping - No product ID or session token available")
            return False
            
        success, response = self.run_test(
            "Get Inventory Filtered by Product (Authenticated)",
            "GET",
            "inventory",
            200,
            params={"product_id": self.product_id},
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} inventory items for product")
        return success

    def test_get_inventory_filtered_by_warehouse(self):
        """Test getting inventory filtered by warehouse (requires auth)"""
        if not self.warehouse_id or not self.session_token:
            print("⚠️  Skipping - No warehouse ID or session token available")
            return False
            
        success, response = self.run_test(
            "Get Inventory Filtered by Warehouse (Authenticated)",
            "GET",
            "inventory",
            200,
            params={"warehouse_id": self.warehouse_id},
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} inventory items for warehouse")
        return success

    def test_stock_issue(self):
        """Test creating a stock issue (requires auth) - using regular user token"""
        if not self.product_id or not self.warehouse_id or not self.session_token:
            print("⚠️  Skipping - Missing product/warehouse ID or session token")
            return False
            
        success, response = self.run_test(
            "Create Stock Issue (Inventory Officer)",
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
            },
            auth_token=self.session_token
        )
        return success

    def test_inventory_adjustment(self):
        """Test creating an inventory adjustment (requires auth) - using regular user token"""
        if not self.product_id or not self.warehouse_id or not self.session_token:
            print("⚠️  Skipping - Missing product/warehouse ID or session token")
            return False
            
        success, response = self.run_test(
            "Create Inventory Adjustment (Inventory Officer)",
            "POST",
            "adjustments",
            200,
            data={
                "product_id": self.product_id,
                "warehouse_id": self.warehouse_id,
                "bin_id": self.bin_id,
                "quantity_change": 5,
                "reason": "Physical count correction"
            },
            auth_token=self.session_token
        )
        return success

    def test_get_stock_moves(self):
        """Test getting stock moves (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Stock Moves (Authenticated)",
            "GET",
            "stock-moves",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} stock moves")
        return success

    def test_get_adjustments(self):
        """Test getting adjustments (requires auth)"""
        if not self.session_token:
            print("⚠️  Skipping - No session token available")
            return False
            
        success, response = self.run_test(
            "Get Adjustments (Authenticated)",
            "GET",
            "adjustments",
            200,
            auth_token=self.session_token
        )
        if success:
            print(f"   Found {len(response)} adjustments")
        return success

    def verify_inventory_calculation(self):
        """Verify that inventory is correctly calculated after all operations (requires auth)"""
        if not self.product_id or not self.session_token:
            print("⚠️  Skipping - No product ID or session token available")
            return False
            
        print(f"\n🔍 Verifying Inventory Calculation...")
        success, response = self.run_test(
            "Verify Final Inventory (Authenticated)",
            "GET",
            "inventory",
            200,
            params={"product_id": self.product_id},
            auth_token=self.session_token
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
    print("=" * 80)
    print("INVENTORY MANAGEMENT SYSTEM WITH AUTHENTICATION - API TESTING")
    print("=" * 80)
    
    tester = AuthInventoryAPITester()
    
    # ========== AUTHENTICATION TESTS ==========
    print("\n🔐 TESTING AUTHENTICATION & AUTHORIZATION")
    print("-" * 80)
    
    # Test user registration and login
    tester.test_register_user()
    tester.test_register_admin_user()
    tester.test_login_user()
    tester.test_login_admin_user()
    
    # Test authentication validation
    tester.test_get_current_user()
    tester.test_protected_route_without_auth()
    
    # Test role-based access control
    tester.test_user_management_access_denied()
    tester.test_user_management_admin_access()
    tester.test_audit_logs_access()
    tester.test_role_update()
    
    # ========== INVENTORY TESTS (WITH AUTH) ==========
    print("\n📦 TESTING PRODUCTS (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_create_product()
    tester.test_get_products()
    
    print("\n🏢 TESTING WAREHOUSES (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_create_warehouse()
    tester.test_get_warehouses()
    
    print("\n📍 TESTING BINS (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_create_bin()
    tester.test_get_bins()
    tester.test_get_bins_filtered()
    
    print("\n📥 TESTING STOCK RECEIPT (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_stock_receipt()
    
    print("\n📊 TESTING INVENTORY RETRIEVAL (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_get_inventory()
    tester.test_get_inventory_filtered_by_product()
    tester.test_get_inventory_filtered_by_warehouse()
    
    print("\n📤 TESTING STOCK ISSUE (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_stock_issue()
    
    print("\n🔧 TESTING INVENTORY ADJUSTMENT (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_inventory_adjustment()
    
    print("\n📜 TESTING HISTORY (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.test_get_stock_moves()
    tester.test_get_adjustments()
    
    print("\n✓ VERIFYING INVENTORY CALCULATIONS (WITH AUTHENTICATION)")
    print("-" * 80)
    tester.verify_inventory_calculation()
    
    print("\n🔓 TESTING LOGOUT")
    print("-" * 80)
    tester.test_logout()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Print detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 80)
    for result in tester.test_results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
