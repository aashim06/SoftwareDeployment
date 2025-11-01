#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class GroupStudySchedulerTester:
    def __init__(self, base_url="https://timealign.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    self.log_test(name, True)
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    self.log_test(name, True)
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    error_msg = f"Expected {expected_status}, got {response.status_code}: {error_data}"
                except:
                    error_msg = f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}"
                
                print(f"   Error: {error_msg}")
                self.log_test(name, False, error_msg)
                return False, {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"   Exception: {error_msg}")
            self.log_test(name, False, error_msg)
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test("API Health Check", "GET", "", 200)

    def test_signup(self, email, password, name):
        """Test user signup"""
        success, response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            200,
            data={
                "email": email,
                "password": password,
                "name": name,
                "timezone": "UTC"
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   Stored token: {self.token[:20]}...")
            print(f"   User ID: {self.user_data['id']}")
            return True
        return False

    def test_login(self, email, password):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": email,
                "password": password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"   Stored token: {self.token[:20]}...")
            return True
        return False

    def test_get_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "me",
            200
        )
        return success and response.get('id') == self.user_data['id']

    def test_create_group(self, name):
        """Test group creation"""
        success, response = self.run_test(
            "Create Group",
            "POST",
            "groups",
            200,
            data={"name": name}
        )
        
        if success and 'id' in response:
            print(f"   Created group ID: {response['id']}")
            return response['id']
        return None

    def test_get_groups(self):
        """Test get user groups"""
        success, response = self.run_test(
            "Get User Groups",
            "GET",
            "groups",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} groups")
            return response
        return []

    def test_get_group_details(self, group_id):
        """Test get group details"""
        success, response = self.run_test(
            "Get Group Details",
            "GET",
            f"groups/{group_id}",
            200
        )
        
        if success:
            print(f"   Group: {response.get('name')}")
            print(f"   Members: {len(response.get('members', []))}")
            return response
        return None

    def test_invite_members(self, group_id, emails):
        """Test member invitation"""
        success, response = self.run_test(
            "Invite Group Members",
            "POST",
            f"groups/{group_id}/invite",
            200,
            data={"emails": emails}
        )
        return success

    def test_schedule_suggest(self, group_id):
        """Test schedule suggestions"""
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=7)
        
        success, response = self.run_test(
            "Schedule Suggestions",
            "POST",
            "schedule/suggest",
            200,
            data={
                "group_id": group_id,
                "range_start": start_date.isoformat(),
                "range_end": end_date.isoformat(),
                "duration_mins": 60,
                "granularity_mins": 15,
                "min_coverage": 0.7
            }
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} time suggestions")
            return response
        return []

    def test_create_event(self, group_id, start_time, end_time):
        """Test event creation"""
        success, response = self.run_test(
            "Create Event",
            "POST",
            "schedule/create",
            200,
            data={
                "group_id": group_id,
                "start": start_time,
                "end": end_time,
                "title": "Test Study Session",
                "description": "Automated test event",
                "location": "Test Room"
            }
        )
        
        if success and response.get('message'):
            print(f"   Event created: {response.get('event_id')}")
            return True
        return False

    def test_google_oauth_start(self):
        """Test Google OAuth start endpoint"""
        success, response = self.run_test(
            "Google OAuth Start",
            "GET",
            "auth/google/start",
            200
        )
        
        if success and 'auth_url' in response:
            print(f"   OAuth URL generated: {response['auth_url'][:50]}...")
            return True
        return False

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Group Study Scheduler API Tests")
        print("=" * 60)
        
        # Generate unique test data
        test_id = str(uuid.uuid4())[:8]
        test_email = f"test_{test_id}@example.com"
        test_password = "TestPass123!"
        test_name = f"Test User {test_id}"
        test_group_name = f"Test Group {test_id}"
        
        # Test 1: Health Check
        if not self.test_health_check()[0]:
            print("❌ API is not responding. Stopping tests.")
            return False
        
        # Test 2: User Signup
        if not self.test_signup(test_email, test_password, test_name):
            print("❌ Signup failed. Stopping tests.")
            return False
        
        # Test 3: Get Current User
        if not self.test_get_me():
            print("❌ Get current user failed. Stopping tests.")
            return False
        
        # Test 4: Create Group
        group_id = self.test_create_group(test_group_name)
        if not group_id:
            print("❌ Group creation failed. Stopping tests.")
            return False
        
        # Test 5: Get Groups
        groups = self.test_get_groups()
        if not groups:
            print("❌ Get groups failed. Stopping tests.")
            return False
        
        # Test 6: Get Group Details
        group_details = self.test_get_group_details(group_id)
        if not group_details:
            print("❌ Get group details failed. Stopping tests.")
            return False
        
        # Test 7: Invite Members (will fail for non-existent emails, but should return 200)
        self.test_invite_members(group_id, ["nonexistent@example.com"])
        
        # Test 8: Schedule Suggestions
        suggestions = self.test_schedule_suggest(group_id)
        
        # Test 9: Create Event (if we have suggestions)
        if suggestions:
            first_suggestion = suggestions[0]
            self.test_create_event(
                group_id,
                first_suggestion['start'],
                first_suggestion['end']
            )
        
        # Test 10: Google OAuth Start
        self.test_google_oauth_start()
        
        # Test 11: Test Login with created user
        # Clear token first to test login
        self.token = None
        if not self.test_login(test_email, test_password):
            print("❌ Login failed.")
            return False
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = GroupStudySchedulerTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        tester.print_summary()
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        tester.print_summary()
        return 1

if __name__ == "__main__":
    sys.exit(main())