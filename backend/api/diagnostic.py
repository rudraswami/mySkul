"""
Visual Generation Diagnostic Tool (V3.0)
Tests visual pipeline end-to-end using Whiteboard Engine
"""
import base64
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
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
    Generate visual for a question using Whiteboard Engine V3.0.
    """
    try:
        from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine
        import re as _re

        # Extract marks from question
        marks = 3
        m = _re.search(r"(\d+)\s*marks?", req.question.lower())
        if m:
            try:
                marks = int(m.group(1))
            except Exception:
                marks = 3

        # Extract concept from question
        concept = whiteboard_engine.extract_concept(req.question)
        
        if not concept:
            return {
                "success": False,
                "question": req.question,
                "marks": marks,
                "error": "No visual concept detected for this question",
                "source": "whiteboard_engine"
            }

        # Generate visual using whiteboard engine
        subject = req.student_dna.get("subject", "physics") if req.student_dna else "physics"
        result = generate_whiteboard_visual(
            concept=concept,
            subject=subject,
            question=req.question
        )

        return {
            "success": True,
            "question": req.question,
            "marks": marks,
            "concept": concept,
            "visual": result,
            "beats": len(result.get("beats", [])),
            "title": result.get("title", ""),
            "title_hindi": result.get("title_hindi", ""),
            "source": "whiteboard_engine",
            "validated": True
        }

    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"blended-sketch failed: {str(e)}\n{traceback.format_exc()}"
        )


@router.get("/visual-test")
async def test_visual_generation(
    concept: str = "force",
    subject: str = "physics"
):
    """
    Test visual generation pipeline with whiteboard engine.
    Returns diagnostic info + visual blueprint.
    """
    try:
        from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine
        
        # Generate visual
        result = generate_whiteboard_visual(
            concept=concept,
            subject=subject
        )
        
        return {
            "success": True,
            "concept": concept,
            "subject": subject,
            "visual": result,
            "beats_count": len(result.get("beats", [])),
            "total_duration_ms": result.get("total_duration_ms", 0),
            "stats": whiteboard_engine.get_stats(),
            "test": "Whiteboard Engine V3.0 is working"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test": "Whiteboard Engine FAILED"
        }


@router.get("/concepts-stats")
async def get_concepts_stats(subject: str | None = None):
    """
    Get Visual Concepts statistics.
    Shows available concepts by subject.
    """
    try:
        from services.whiteboard_engine import whiteboard_engine

        stats = whiteboard_engine.get_stats()
        concepts = whiteboard_engine.get_available_concepts(subject)

        return {
            "success": True,
            "subject": subject or "all",
            "stats": stats,
            "concepts": concepts,
            "total": len(concepts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"concepts-stats failed: {str(e)}")


@router.get("/visual-render-test")
async def visual_render_test():
    """
    Returns HTML page to test visual rendering in browser.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visual Rendering Test - Whiteboard Engine V3.0</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            .test-container { margin: 20px 0; padding: 20px; border: 1px solid #ccc; background: white; border-radius: 8px; }
            .success { color: green; }
            .error { color: red; }
            pre { background: #f0f0f0; padding: 10px; overflow-x: auto; border-radius: 4px; }
            button { padding: 10px 20px; background: #FF9933; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #e68a00; }
        </style>
    </head>
    <body>
        <h1>🎨 Whiteboard Engine V3.0 - Diagnostic</h1>
        
        <div class="test-container">
            <h2>Test: Generate Visual Blueprint</h2>
            <label>Concept: <input id="concept" value="force" style="padding: 5px;"></label>
            <label>Subject: <input id="subject" value="physics" style="padding: 5px;"></label>
            <button onclick="testGeneration()">Generate Visual</button>
            <pre id="result">Click "Generate Visual" to test</pre>
        </div>
        
        <div class="test-container">
            <h2>Available Concepts</h2>
            <button onclick="loadStats()">Load Statistics</button>
            <pre id="stats">Click "Load Statistics" to view</pre>
        </div>
        
        <script>
            async function testGeneration() {
                const concept = document.getElementById('concept').value;
                const subject = document.getElementById('subject').value;
                document.getElementById('result').textContent = 'Loading...';
                
                try {
                    const res = await fetch(`/diagnostic/visual-test?concept=${concept}&subject=${subject}`);
                    const data = await res.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('result').textContent = 'Error: ' + e.message;
                }
            }
            
            async function loadStats() {
                document.getElementById('stats').textContent = 'Loading...';
                
                try {
                    const res = await fetch('/diagnostic/concepts-stats');
                    const data = await res.json();
                    document.getElementById('stats').textContent = JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('stats').textContent = 'Error: ' + e.message;
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


class TeachingVisualRequest(BaseModel):
    question: str
    subject: str | None = None


@router.post("/teaching-visual")
async def teaching_visual(req: TeachingVisualRequest):
    """
    Generate teaching visual using Whiteboard Engine.
    """
    try:
        from services.whiteboard_engine import generate_whiteboard_visual, whiteboard_engine

        concept = whiteboard_engine.extract_concept(req.question)
        subject = req.subject or "physics"
        
        if concept:
            visual = generate_whiteboard_visual(concept, subject, req.question)
            return {
                "success": True,
                "source": "whiteboard_engine",
                "concept": concept,
                "visual": visual,
            }
        else:
            return {
                "success": False,
                "source": "whiteboard_engine",
                "error": "No concept detected",
                "available_concepts": whiteboard_engine.get_available_concepts(subject)[:10]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"teaching-visual failed: {e}")
