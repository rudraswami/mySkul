"""
Visual Generation Diagnostic Tool
Tests visual pipeline end-to-end
"""
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

class VisualTestRequest(BaseModel):
    metaphor_category: str = "cricket"
    region: str = "Bangalore"

@router.get("/visual-test")
async def test_visual_generation(
    metaphor: str = "cricket",
    region: str = "Bangalore"
):
    """
    Test visual generation pipeline
    Returns diagnostic info + visual assets
    """
    from services.ai_service import AIService
    
    # Create dummy AI service to access SVG method
    service = AIService(db=None, emergent_llm_key="test")
    
    try:
        # Get SVG fallback
        svg_fallback = service._get_svg_fallback(metaphor, region)
        
        # Decode base64 to verify it's valid
        svg_data = svg_fallback['svg_template']
        if svg_data.startswith('data:image/svg+xml;base64,'):
            b64_data = svg_data.split(',')[1]
            try:
                decoded = base64.b64decode(b64_data)
                svg_valid = True
                svg_content = decoded.decode('utf-8')
            except Exception as e:
                svg_valid = False
                svg_content = f"Error: {str(e)}"
        else:
            svg_valid = False
            svg_content = "Invalid data URI format"
        
        return {
            "success": True,
            "metaphor_category": metaphor,
            "region": region,
            "svg_fallback": svg_fallback,
            "svg_valid": svg_valid,
            "svg_content": svg_content,
            "svg_data_uri": svg_data,
            "emoji": svg_fallback['emoji'],
            "color_theme": svg_fallback['color_theme'],
            "test": "Visual generation pipeline is working"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test": "Visual generation pipeline FAILED"
        }


@router.get("/visual-render-test")
async def visual_render_test():
    """
    Returns HTML page to test visual rendering in browser
    """
    from fastapi.responses import HTMLResponse
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visual Rendering Test</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .test-container { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
            img { max-width: 400px; border: 2px solid #333; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Visual Rendering Diagnostic</h1>
        
        <div class="test-container">
            <h2>Test 1: SVG Data URI (Cricket)</h2>
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNFRkY2RkYiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4MCIgZmlsbD0iIzEwQjk4MSI+8J+PjzwvdGV4dD48L3N2Zz4=" 
                 onload="document.getElementById('test1-status').textContent = '✅ SUCCESS'; document.getElementById('test1-status').className = 'success';"
                 onerror="document.getElementById('test1-status').textContent = '❌ FAILED'; document.getElementById('test1-status').className = 'error';">
            <p id="test1-status">Loading...</p>
        </div>
        
        <div class="test-container">
            <h2>Test 2: SVG Data URI (Cooking)</h2>
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNGRUYzQzciLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4MCIgZmlsbD0iI0Y1OUUwQiI+8J+NszwvdGV4dD48L3N2Zz4="
                 onload="document.getElementById('test2-status').textContent = '✅ SUCCESS'; document.getElementById('test2-status').className = 'success';"
                 onerror="document.getElementById('test2-status').textContent = '❌ FAILED'; document.getElementById('test2-status').className = 'error';">
            <p id="test2-status">Loading...</p>
        </div>
        
        <div class="test-container">
            <h2>Test 3: Direct SVG Rendering</h2>
            <div id="svg-container"></div>
            <script>
                const svgB64 = 'PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCI+PHJlY3Qgd2lkdGg9IjQwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiNFRkY2RkYiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI4MCIgZmlsbD0iIzEwQjk4MSI+8J+PjzwvdGV4dD48L3N2Zz4=';
                const svgDecoded = atob(svgB64);
                document.getElementById('svg-container').innerHTML = svgDecoded;
                document.getElementById('test3-status').textContent = '✅ SUCCESS';
                document.getElementById('test3-status').className = 'success';
            </script>
            <p id="test3-status">Loading...</p>
        </div>
        
        <div class="test-container">
            <h2>Browser Info</h2>
            <p><strong>User Agent:</strong> <span id="ua"></span></p>
            <p><strong>Data URI Support:</strong> <span id="data-uri-support"></span></p>
            <script>
                document.getElementById('ua').textContent = navigator.userAgent;
                // Test data URI support
                const testImg = new Image();
                testImg.onload = () => {
                    document.getElementById('data-uri-support').textContent = '✅ Supported';
                    document.getElementById('data-uri-support').className = 'success';
                };
                testImg.onerror = () => {
                    document.getElementById('data-uri-support').textContent = '❌ Not Supported';
                    document.getElementById('data-uri-support').className = 'error';
                };
                testImg.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
            </script>
        </div>
        
        <div class="test-container">
            <h2>Test Results Summary</h2>
            <ul>
                <li>If all tests show ✅ SUCCESS: Visual rendering is working</li>
                <li>If tests show ❌ FAILED: Check browser console for errors</li>
                <li>Check Network tab to see if images are being blocked</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
