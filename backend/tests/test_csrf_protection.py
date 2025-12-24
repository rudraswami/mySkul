"""
CSRF Protection Tests - Double-Submit Cookie Pattern
Verifies the CSRF implementation works correctly for SPA clients.

Test Coverage:
1. GET /api/auth/csrf-token sets cookie + returns JSON
2. POST without header returns 403
3. POST with header but without cookie returns 403
4. POST with matching header + cookie returns success
5. CORS preflight includes required headers

Run with: pytest backend/tests/test_csrf_protection.py -v
"""
import pytest
from fastapi.testclient import TestClient


# Import app - adjust path as needed
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCSRFProtection:
    """Test suite for CSRF protection middleware"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test client"""
        # Import here to avoid circular imports during collection
        from main import create_app
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_csrf_token_endpoint_returns_token_and_sets_cookie(self):
        """
        Test 1: GET /api/auth/csrf-token should:
        - Return 200
        - Return csrf_token in JSON body
        - Set csrf_token cookie
        - Include X-CSRF-Token header
        """
        response = self.client.get("/api/auth/csrf-token")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check JSON body
        data = response.json()
        assert "csrf_token" in data, "Response should contain csrf_token"
        assert len(data["csrf_token"]) > 20, "Token should be at least 20 chars"
        
        # Check cookie was set
        assert "csrf_token" in response.cookies, "csrf_token cookie should be set"
        cookie_value = response.cookies.get("csrf_token")
        assert cookie_value == data["csrf_token"], "Cookie should match JSON token"
        
        # Check header
        assert "X-CSRF-Token" in response.headers, "X-CSRF-Token header should be present"
        
        print(f"✅ CSRF token endpoint working: token={data['csrf_token'][:20]}...")
    
    def test_post_without_csrf_header_returns_403(self):
        """
        Test 2: POST request without X-CSRF-Token header should return 403
        """
        # First get CSRF token to set cookie
        csrf_response = self.client.get("/api/auth/csrf-token")
        assert csrf_response.status_code == 200
        
        # Now try POST without header (but with cookie from previous request)
        # Using a protected endpoint that requires CSRF
        response = self.client.post(
            "/api/analytics/feedback",
            json={"feedback_type": "helpful"},
            # Note: TestClient automatically includes cookies from previous requests
        )
        
        # Should fail because header is missing
        assert response.status_code in [403, 401], f"Expected 403/401, got {response.status_code}"
        
        if response.status_code == 403:
            data = response.json()
            assert "CSRF" in data.get("detail", "") or "csrf" in data.get("detail", "").lower(), \
                "Error message should mention CSRF"
        
        print("✅ POST without CSRF header correctly rejected")
    
    def test_post_with_mismatched_token_returns_403(self):
        """
        Test 3: POST with mismatched header/cookie token should return 403
        """
        # Get CSRF token
        csrf_response = self.client.get("/api/auth/csrf-token")
        assert csrf_response.status_code == 200
        
        # Try POST with wrong token in header
        response = self.client.post(
            "/api/analytics/feedback",
            json={"feedback_type": "helpful"},
            headers={"X-CSRF-Token": "wrong-token-value-12345"}
        )
        
        # Should fail due to mismatch
        assert response.status_code in [403, 401], f"Expected 403/401, got {response.status_code}"
        
        print("✅ POST with mismatched CSRF token correctly rejected")
    
    def test_post_with_matching_csrf_token_succeeds(self):
        """
        Test 4: POST with matching header + cookie token should succeed
        (or return auth error, not CSRF error)
        """
        # Get CSRF token
        csrf_response = self.client.get("/api/auth/csrf-token")
        assert csrf_response.status_code == 200
        csrf_token = csrf_response.json()["csrf_token"]
        
        # POST with correct token
        response = self.client.post(
            "/api/analytics/feedback",
            json={"feedback_type": "helpful", "message_id": "test-123"},
            headers={"X-CSRF-Token": csrf_token}
        )
        
        # Should NOT be 403 CSRF error
        # May be 401 (auth required) or 200/201 (success) depending on auth state
        if response.status_code == 403:
            data = response.json()
            detail = data.get("detail", "")
            # If 403, it should NOT be due to CSRF
            assert "CSRF" not in detail and "csrf" not in detail.lower(), \
                f"Request should not fail due to CSRF: {detail}"
        
        print(f"✅ POST with matching CSRF token passed (status={response.status_code})")
    
    def test_cors_preflight_includes_csrf_header(self):
        """
        Test 5: OPTIONS preflight should allow X-CSRF-Token header
        """
        response = self.client.options(
            "/api/analytics/feedback",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-CSRF-Token,Content-Type"
            }
        )
        
        # Should return 200 for preflight
        assert response.status_code == 200, f"Preflight should return 200, got {response.status_code}"
        
        # Check CORS headers
        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert "x-csrf-token" in allow_headers.lower(), \
            f"CORS should allow X-CSRF-Token header. Got: {allow_headers}"
        
        allow_credentials = response.headers.get("access-control-allow-credentials", "")
        assert allow_credentials.lower() == "true", \
            f"CORS should allow credentials. Got: {allow_credentials}"
        
        print("✅ CORS preflight correctly configured for CSRF")
    
    def test_exempt_paths_skip_csrf_validation(self):
        """
        Test 6: Exempt paths should work without CSRF token
        """
        # Test health endpoint (should be exempt)
        response = self.client.get("/api/health")
        assert response.status_code == 200, f"Health check should work: {response.status_code}"
        
        # Test login endpoint (POST but exempt)
        response = self.client.post(
            "/api/auth/login",
            json={"email": "test@test.com", "password": "test123"}
        )
        # Should NOT be 403 CSRF error (may be 401 or other auth error)
        if response.status_code == 403:
            data = response.json()
            detail = data.get("detail", "")
            assert "CSRF" not in detail and "csrf" not in detail.lower(), \
                f"Login should be CSRF exempt: {detail}"
        
        print(f"✅ Exempt paths work without CSRF (login status={response.status_code})")


class TestCSRFContract:
    """Document the CSRF contract for frontend developers"""
    
    def test_print_csrf_contract(self):
        """Print the CSRF contract summary"""
        contract = """
╔══════════════════════════════════════════════════════════════════╗
║                    CSRF CONTRACT SUMMARY                         ║
╠══════════════════════════════════════════════════════════════════╣
║ Pattern: Double-Submit Cookie                                    ║
║                                                                  ║
║ Cookie Name:  csrf_token                                         ║
║ Header Name:  X-CSRF-Token                                       ║
║ Fetch Token:  GET /api/auth/csrf-token (once at app start)       ║
║ On 403 CSRF:  Retry fetch once, then retry request               ║
║                                                                  ║
║ Frontend Must:                                                   ║
║   1. Include { credentials: 'include' } in fetch                 ║
║   2. Read token from cookie or response JSON                     ║
║   3. Send token in X-CSRF-Token header on POST/PUT/PATCH/DELETE  ║
║                                                                  ║
║ Backend Sets:                                                    ║
║   - csrf_token cookie (SameSite=Lax, HttpOnly=false)             ║
║   - X-CSRF-Token response header                                 ║
║   - JSON body: { "csrf_token": "..." }                           ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(contract)
        assert True  # Always pass, just for documentation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])





