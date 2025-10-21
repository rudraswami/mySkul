"""
Security Headers Middleware
Adds essential security headers to all HTTP responses
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    
    Headers Added:
    - Strict-Transport-Security (HSTS): Force HTTPS
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: XSS filter (legacy browsers)
    - Referrer-Policy: Control referrer information
    - Content-Security-Policy: CSP for XSS prevention
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HSTS - Force HTTPS for 1 year (31536000 seconds)
        # includeSubDomains: Apply to all subdomains
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevent MIME type sniffing
        # Browsers must respect declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        # DENY: Page cannot be displayed in frame/iframe
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy header, but still useful for older browsers)
        # 1; mode=block: Enable XSS filter and block page if attack detected
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        # strict-origin-when-cross-origin: Send full URL for same-origin, only origin for cross-origin
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (CSP)
        # Strict policy to prevent XSS and data injection attacks
        # Note: Adjust based on your actual requirements
        csp_directives = [
            "default-src 'self'",  # Default: only same origin
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://checkout.razorpay.com",  # Allow Razorpay scripts
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (Tailwind, etc.)
            "img-src 'self' data: https:",  # Allow images from data URIs and HTTPS
            "font-src 'self' data:",  # Allow fonts from same origin and data URIs
            "connect-src 'self' https://seamless-auth-1.emergent.host https://api.openai.com",  # API endpoints
            "frame-src https://checkout.razorpay.com",  # Allow Razorpay iframe
            "object-src 'none'",  # Block <object>, <embed>, <applet>
            "base-uri 'self'",  # Restrict <base> tag
            "form-action 'self'",  # Forms can only submit to same origin
        ]
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Permissions Policy (formerly Feature-Policy)
        # Restrict powerful browser features
        permissions_policy = [
            "geolocation=()",  # Disable geolocation
            "microphone=(self)",  # Allow microphone only for same origin
            "camera=()",  # Disable camera
            "payment=(self)",  # Allow payment API only for same origin
            "usb=()",  # Disable USB
            "magnetometer=()",  # Disable magnetometer
        ]
        
        response.headers["Permissions-Policy"] = ", ".join(permissions_policy)
        
        return response
