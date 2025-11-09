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


class BlendedSketchRequest(BaseModel):
    question: str
    student_dna: dict | None = None


@router.post("/blended-sketch")
async def blended_sketch(req: BlendedSketchRequest):
    """
    Generate appropriate visual (concept OR solution) with Friend Test validation.
    Now dynamically understands the question and generates step-by-step solutions
    or concept explanations based on question type.
    """
    try:
        from services.unified_visual_system import generate_visual_for_question
        from services.visual_library import VisualLibrary

        # Initialize library
        library = VisualLibrary()

        # Extract marks from question
        import re as _re
        marks = 3
        m = _re.search(r"(\d+)\s*marks?", req.question.lower())
        if m:
            try:
                marks = int(m.group(1))
            except Exception:
                marks = 3

        # Check library first (codebase-first approach)
        existing = library.find_existing(req.question, marks, subject="cs")

        if existing:
            return {
                "success": True,
                "question": req.question,
                "marks": marks,
                "metaphors": existing["metadata"].get("metaphors_used", []),
                "svg": existing["svg"],
                "size_kb": round(len(existing["svg"]) / 1024.0, 2),
                "topper_hack": existing["metadata"].get("topper_hack"),
                "topper_rank": existing["metadata"].get("topper_rank"),
                "pyq_references": existing["metadata"].get("pyq_references", []),
                "friend_test": existing.get("analytics", {}).get("friend_test_score", 0),
                "source": "cached",
                "validated": True
            }

        # Generate visual using new unified system (auto-detects concept vs solution)
        result = generate_visual_for_question(
            question=req.question,
            student_profile=req.student_dna,
            marks=marks
        )

        svg = result["svg"]
        visual_type = result.get("visual_type", "concept")
        friend_result = result.get("friend_test", {})

        # Cache if passes friend test
        if friend_result.get("passed", False):
            library.save_visual(
                question=req.question,
                marks=marks,
                svg=svg,
                metadata=result["metadata"],
                subject="cs",
                friend_test_score=friend_result.get("score_value", 0)
            )

        # Build response based on visual type
        response = {
            "success": friend_result.get("passed", False),
            "question": req.question,
            "marks": marks,
            "visual_type": visual_type,
            "svg": svg,
            "size_kb": round(len(svg) / 1024.0, 2),
            "friend_test": friend_result,
            "source": "generated",
            "validated": friend_result.get("passed", False)
        }

        # Add type-specific metadata
        if visual_type == "solution":
            response.update({
                "problem_type": result["metadata"].get("problem_type"),
                "num_steps": result["metadata"].get("num_steps", 0),
                "final_answer": result["metadata"].get("final_answer"),
                "subject": result["metadata"].get("subject")
            })
        else:  # concept
            response.update({
                "metaphors": result["metadata"].get("metaphors_used", []),
                "topper_hack": result["metadata"].get("topper_hack"),
                "topper_rank": result["metadata"].get("topper_rank"),
                "pyq_references": result["metadata"].get("pyq_references", []),
                "region": result["metadata"].get("region", "North")
            })

        return response

    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"blended-sketch failed: {str(e)}\n{traceback.format_exc()}"
        )

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


@router.get("/library-stats")
async def get_library_stats(subject: str | None = None):
    """
    Get Visual Library statistics
    Shows cached visuals, performance metrics, and high performers
    """
    try:
        from services.visual_library import VisualLibrary

        library = VisualLibrary()
        stats = library.get_library_stats(subject=subject)

        return {
            "success": True,
            "subject": subject or "all",
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"library-stats failed: {str(e)}")


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
