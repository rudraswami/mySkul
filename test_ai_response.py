"""
Quick test script to verify AI Tutor 2.4 text cleaning and LaTeX preservation
"""
import asyncio
from backend.utils.response_parser import ResponseParser

async def test_cleaning():
    # Sample response with LaTeX and special characters
    sample_text = """
    **Key Trigonometric Identities**:
    
    ✅ **Pythagorean Identities**: 
    These arise from the Pythagorean Theorem applied to the unit circle.
    
    \\[
    \\sin^2 \\theta + \\cos^2 \\theta = 1 \\quad \\text{(Primary Identity)}
    \\]
    
    \\[
    1 + \\tan^2 \\theta = \\sec^2 \\theta \\quad \\text{(Derived by dividing the primary identity by )} \\cos^2 \\theta\\text{)}
    \\]
    
    ✅ **Reciprocal Identities** They often help to rewrite expressions in simpler terms: \\( \\sin \\theta = \\frac{1}{\\csc \\theta} \\)
    
    Remember, **practice** is key to becoming proficient with these identities. \\\\Apply them consistently.
    """
    
    parser = ResponseParser(emergent_llm_key="dummy")
    cleaned = parser.clean_text(sample_text)
    
    print("=" * 80)
    print("ORIGINAL TEXT:")
    print("=" * 80)
    print(sample_text)
    print("\n")
    print("=" * 80)
    print("CLEANED TEXT:")
    print("=" * 80)
    print(cleaned)
    print("\n")
    print("=" * 80)
    print("CHECKS:")
    print("=" * 80)
    latex_open = '\\['
    latex_close = '\\]'
    inline_open = '\\('
    inline_close = '\\)'
    bold = '**'
    check = '✅'
    dbl_slash = '\\\\'
    
    print(f"✅ LaTeX delimiters preserved: {latex_open} present = {latex_open in cleaned}")
    print(f"✅ LaTeX delimiters preserved: {latex_close} present = {latex_close in cleaned}")
    print(f"✅ LaTeX delimiters preserved: {inline_open} present = {inline_open in cleaned}")
    print(f"✅ LaTeX delimiters preserved: {inline_close} present = {inline_close in cleaned}")
    print(f"✅ Bold markers removed: {bold} not present = {bold not in cleaned}")
    print(f"✅ Checkmarks removed: {check} not present = {check not in cleaned}")
    print(f"✅ Double backslashes removed: {dbl_slash} not present = {dbl_slash not in cleaned}")

if __name__ == "__main__":
    asyncio.run(test_cleaning())
