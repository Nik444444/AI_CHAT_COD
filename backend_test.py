#!/usr/bin/env python3
"""
ChatDev Web API Testing Suite
Tests all backend endpoints and WebSocket functionality
"""

import asyncio
import json
import requests
import websockets
import uuid
import time
from datetime import datetime
import sys
import os

# Test configuration - Use public endpoint from frontend/.env
import os
from pathlib import Path

# Read backend URL from frontend/.env
frontend_env_path = Path("/app/frontend/.env")
BACKEND_URL = "http://localhost:8001"  # fallback
if frontend_env_path.exists():
    with open(frontend_env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break
            elif line.startswith('VITE_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break

WS_URL = BACKEND_URL.replace('http', 'ws')
API_KEY = "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"

class ChatDevAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_sessions = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_health_check(self):
        """Test GET /api/health endpoint"""
        print("\n🔍 Testing Health Check Endpoint...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/api/health", timeout=10)
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Health Check", False, f"Expected 200, got {response.status_code}")
                return False
                
            # Check response format
            data = response.json()
            if "status" not in data:
                self.log_test("Health Check", False, "Missing 'status' field in response")
                return False
                
            if data["status"] != "healthy":
                self.log_test("Health Check", False, f"Expected status 'healthy', got '{data['status']}'")
                return False
                
            # Check CORS headers
            cors_headers = response.headers.get('Access-Control-Allow-Origin')
            if cors_headers != '*':
                self.log_test("Health Check CORS", False, f"CORS header missing or incorrect: {cors_headers}")
            else:
                self.log_test("Health Check CORS", True, "CORS headers present")
                
            self.log_test("Health Check", True, f"Status: {data['status']}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, f"Request failed: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            self.log_test("Health Check", False, f"Invalid JSON response: {str(e)}")
            return False
            
    def test_get_sessions_empty(self):
        """Test GET /api/sessions when no sessions exist"""
        print("\n🔍 Testing Get Sessions (Empty)...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/api/sessions", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Get Sessions Empty", False, f"Expected 200, got {response.status_code}")
                return False
                
            data = response.json()
            if "sessions" not in data:
                self.log_test("Get Sessions Empty", False, "Missing 'sessions' field in response")
                return False
                
            if not isinstance(data["sessions"], list):
                self.log_test("Get Sessions Empty", False, "Sessions field is not a list")
                return False
                
            self.log_test("Get Sessions Empty", True, f"Found {len(data['sessions'])} sessions")
            return True
            
        except Exception as e:
            self.log_test("Get Sessions Empty", False, f"Error: {str(e)}")
            return False
            
    def test_create_session(self):
        """Test POST /api/sessions endpoint"""
        print("\n🔍 Testing Create Session...")
        
        test_data = {
            "task": "Create a simple calculator web application with basic arithmetic operations",
            "project_name": f"TestCalculator_{int(time.time())}",
            "model_type": "gpt-4o-mini",
            "api_key": API_KEY,
            "provider": "openai"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/sessions",
                json=test_data,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Create Session", False, f"Expected 200, got {response.status_code}")
                return None
                
            data = response.json()
            required_fields = ["session_id", "status", "message"]
            
            for field in required_fields:
                if field not in data:
                    self.log_test("Create Session", False, f"Missing '{field}' field in response")
                    return None
                    
            session_id = data["session_id"]
            
            # Validate UUID format
            try:
                uuid.UUID(session_id)
            except ValueError:
                self.log_test("Create Session", False, f"Invalid session_id format: {session_id}")
                return None
                
            self.created_sessions.append(session_id)
            self.log_test("Create Session", True, f"Session created: {session_id}")
            return session_id
            
        except Exception as e:
            self.log_test("Create Session", False, f"Error: {str(e)}")
            return None
            
    def test_create_session_invalid_model(self):
        """Test POST /api/sessions with invalid model type"""
        print("\n🔍 Testing Create Session (Invalid Model)...")
        
        test_data = {
            "task": "Test task",
            "project_name": "TestProject",
            "model_type": "invalid-model",
            "api_key": API_KEY,
            "provider": "openai"
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/api/sessions",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Create Session Invalid Model", True, "Correctly rejected invalid model")
                return True
            else:
                self.log_test("Create Session Invalid Model", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Create Session Invalid Model", False, f"Error: {str(e)}")
            return False
            
    def test_get_sessions_with_data(self):
        """Test GET /api/sessions when sessions exist"""
        print("\n🔍 Testing Get Sessions (With Data)...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/api/sessions", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Get Sessions With Data", False, f"Expected 200, got {response.status_code}")
                return False
                
            data = response.json()
            sessions = data.get("sessions", [])
            
            if len(sessions) == 0:
                self.log_test("Get Sessions With Data", False, "No sessions found after creating one")
                return False
                
            # Validate session structure
            session = sessions[0]
            required_fields = ["session_id", "project_name", "task", "status", "created_at", "model_type", "provider"]
            
            for field in required_fields:
                if field not in session:
                    self.log_test("Get Sessions With Data", False, f"Missing '{field}' field in session")
                    return False
                    
            self.log_test("Get Sessions With Data", True, f"Found {len(sessions)} sessions with correct structure")
            return True
            
        except Exception as e:
            self.log_test("Get Sessions With Data", False, f"Error: {str(e)}")
            return False
            
    def test_get_session_files_nonexistent(self):
        """Test GET /api/sessions/{id}/files for non-existent session"""
        print("\n🔍 Testing Get Session Files (Non-existent)...")
        
        fake_session_id = str(uuid.uuid4())
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/sessions/{fake_session_id}/files",
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Get Session Files Non-existent", True, "Correctly returned 404 for non-existent session")
                return True
            else:
                self.log_test("Get Session Files Non-existent", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Session Files Non-existent", False, f"Error: {str(e)}")
            return False
            
    def test_get_session_files_existing(self, session_id):
        """Test GET /api/sessions/{id}/files for existing session"""
        print("\n🔍 Testing Get Session Files (Existing)...")
        
        if not session_id:
            self.log_test("Get Session Files Existing", False, "No session_id provided")
            return False
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/api/sessions/{session_id}/files",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Get Session Files Existing", False, f"Expected 200, got {response.status_code}")
                return False
                
            data = response.json()
            
            if "files" not in data:
                self.log_test("Get Session Files Existing", False, "Missing 'files' field in response")
                return False
                
            if not isinstance(data["files"], list):
                self.log_test("Get Session Files Existing", False, "Files field is not a list")
                return False
                
            # Note: Files might be empty if ChatDev hasn't generated anything yet
            self.log_test("Get Session Files Existing", True, f"Found {len(data['files'])} files")
            return True
            
        except Exception as e:
            self.log_test("Get Session Files Existing", False, f"Error: {str(e)}")
            return False
            
    async def test_websocket_connection(self, session_id):
        """Test WebSocket connection and communication"""
        print("\n🔍 Testing WebSocket Connection...")
        
        if not session_id:
            self.log_test("WebSocket Connection", False, "No session_id provided")
            return False
            
        try:
            uri = f"{WS_URL}/api/sessions/{session_id}/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                self.log_test("WebSocket Connection", True, "Successfully connected to WebSocket")
                
                # Wait for initial messages
                messages_received = 0
                start_time = time.time()
                
                try:
                    while time.time() - start_time < 15:  # Wait up to 15 seconds
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                            data = json.loads(message)
                            messages_received += 1
                            
                            print(f"📨 Received message {messages_received}: {data.get('type', 'unknown')}")
                            
                            # Validate message structure
                            if "type" not in data:
                                self.log_test("WebSocket Message Structure", False, "Missing 'type' field in message")
                                continue
                                
                            if "data" not in data:
                                self.log_test("WebSocket Message Structure", False, "Missing 'data' field in message")
                                continue
                                
                        except asyncio.TimeoutError:
                            # No more messages, break
                            break
                            
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed by server")
                    
                if messages_received > 0:
                    self.log_test("WebSocket Messages", True, f"Received {messages_received} messages")
                    return True
                else:
                    self.log_test("WebSocket Messages", False, "No messages received")
                    return False
                    
        except websockets.exceptions.InvalidStatusCode as e:
            if e.status_code == 404:
                self.log_test("WebSocket Connection", False, "Session not found (404)")
            else:
                self.log_test("WebSocket Connection", False, f"Connection failed with status {e.status_code}")
            return False
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Error: {str(e)}")
            return False
            
    async def test_websocket_nonexistent_session(self):
        """Test WebSocket connection to non-existent session"""
        print("\n🔍 Testing WebSocket (Non-existent Session)...")
        
        fake_session_id = str(uuid.uuid4())
        
        try:
            uri = f"{WS_URL}/api/sessions/{fake_session_id}/ws"
            
            async with websockets.connect(uri, timeout=5) as websocket:
                self.log_test("WebSocket Non-existent Session", False, "Should not connect to non-existent session")
                return False
                
        except websockets.exceptions.InvalidStatusCode as e:
            if e.status_code == 404:
                self.log_test("WebSocket Non-existent Session", True, "Correctly rejected non-existent session")
                return True
            else:
                self.log_test("WebSocket Non-existent Session", False, f"Unexpected status code: {e.status_code}")
                return False
        except Exception as e:
            self.log_test("WebSocket Non-existent Session", False, f"Unexpected error: {str(e)}")
            return False
            
    def test_delete_session(self, session_id):
        """Test DELETE /api/sessions/{id} endpoint"""
        print("\n🔍 Testing Delete Session...")
        
        if not session_id:
            self.log_test("Delete Session", False, "No session_id provided")
            return False
            
        try:
            response = self.session.delete(
                f"{BACKEND_URL}/api/sessions/{session_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Delete Session", False, f"Expected 200, got {response.status_code}")
                return False
                
            data = response.json()
            
            if "message" not in data:
                self.log_test("Delete Session", False, "Missing 'message' field in response")
                return False
                
            # Remove from our tracking list
            if session_id in self.created_sessions:
                self.created_sessions.remove(session_id)
                
            self.log_test("Delete Session", True, "Session deleted successfully")
            return True
            
        except Exception as e:
            self.log_test("Delete Session", False, f"Error: {str(e)}")
            return False
            
    def test_delete_nonexistent_session(self):
        """Test DELETE /api/sessions/{id} for non-existent session"""
        print("\n🔍 Testing Delete Non-existent Session...")
        
        fake_session_id = str(uuid.uuid4())
        
        try:
            response = self.session.delete(
                f"{BACKEND_URL}/api/sessions/{fake_session_id}",
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Delete Non-existent Session", True, "Correctly returned 404 for non-existent session")
                return True
            else:
                self.log_test("Delete Non-existent Session", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Delete Non-existent Session", False, f"Error: {str(e)}")
            return False
            
    def cleanup_sessions(self):
        """Clean up any remaining test sessions"""
        print("\n🧹 Cleaning up test sessions...")
        
        for session_id in self.created_sessions[:]:
            try:
                response = self.session.delete(f"{BACKEND_URL}/api/sessions/{session_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up session: {session_id}")
                    self.created_sessions.remove(session_id)
                else:
                    print(f"⚠️ Failed to clean up session: {session_id}")
            except Exception as e:
                print(f"⚠️ Error cleaning up session {session_id}: {str(e)}")
                
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 CHATDEV WEB API TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
                    
        print("\n" + "="*60)
        
        return failed_tests == 0

async def main():
    """Main test execution"""
    print("🚀 Starting ChatDev Web API Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"WebSocket URL: {WS_URL}")
    
    tester = ChatDevAPITester()
    
    try:
        # Test sequence
        print("\n📋 Test Sequence:")
        print("1. Health Check")
        print("2. Sessions Management (CRUD)")
        print("3. File Operations")
        print("4. WebSocket Communication")
        print("5. Error Handling")
        
        # 1. Health Check
        tester.test_health_check()
        
        # 2. Sessions Management
        tester.test_get_sessions_empty()
        session_id = tester.test_create_session()
        tester.test_create_session_invalid_model()
        tester.test_get_sessions_with_data()
        
        # 3. File Operations
        tester.test_get_session_files_nonexistent()
        if session_id:
            tester.test_get_session_files_existing(session_id)
        
        # 4. WebSocket Communication
        await tester.test_websocket_nonexistent_session()
        if session_id:
            await tester.test_websocket_connection(session_id)
        
        # 5. Error Handling & Cleanup
        tester.test_delete_nonexistent_session()
        if session_id:
            tester.test_delete_session(session_id)
            
        # Final cleanup
        tester.cleanup_sessions()
        
        # Print summary
        success = tester.print_summary()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        tester.cleanup_sessions()
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        tester.cleanup_sessions()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)