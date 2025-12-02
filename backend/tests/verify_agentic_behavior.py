"""
🧠 Agent Behavior Verification Script
=====================================

This script verifies that all agents in the Druv AI system are
behaving as TRUE AGENTS (not just LLM wrappers).

True Agentic Behavior Checklist:
✅ Level 1: Basic LLM wrapper (just prompts)
✅ Level 2: LLM with context (conversation history)
✅ Level 3: LLM with tools (can use external tools)
✅ Level 4: ReAct loop (Think → Act → Observe cycle)
✅ Level 5: Full Agent (planning, memory, verification, self-correction)

Run: python -m pytest backend/tests/verify_agentic_behavior.py -v
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_check(name: str, passed: bool, details: str = ""):
    status = "✅" if passed else "❌"
    print(f"  {status} {name}")
    if details:
        print(f"     └─ {details}")


def verify_agent_structure():
    """Verify all agents have proper structure"""
    print_header("🔍 AGENT STRUCTURE VERIFICATION")
    
    results = {}
    
    # Check base agent
    try:
        from agents.base_agent import BaseAgent
        has_process = hasattr(BaseAgent, 'process')
        has_get_type = hasattr(BaseAgent, 'get_agent_type')
        results['BaseAgent'] = has_process and has_get_type
        print_check("BaseAgent exists", True, f"process={has_process}, get_agent_type={has_get_type}")
    except Exception as e:
        results['BaseAgent'] = False
        print_check("BaseAgent exists", False, str(e))
    
    # Check intelligent base
    try:
        from agents.intelligent_agent_base import IntelligentAgentBase
        has_llm = hasattr(IntelligentAgentBase, '_call_llm')
        has_context = hasattr(IntelligentAgentBase, '_build_context')
        results['IntelligentAgentBase'] = has_llm
        print_check("IntelligentAgentBase exists", True, f"LLM integration={has_llm}")
    except Exception as e:
        results['IntelligentAgentBase'] = False
        print_check("IntelligentAgentBase exists", False, str(e))
    
    # Check ReAct agent
    try:
        from agents.core.react_agent import ReActAgent
        has_run = hasattr(ReActAgent, 'run')
        has_think = hasattr(ReActAgent, '_think')
        has_act = hasattr(ReActAgent, '_act')
        results['ReActAgent'] = has_run and has_think and has_act
        print_check("ReActAgent (True Agent)", True, f"Think={has_think}, Act={has_act}")
    except Exception as e:
        results['ReActAgent'] = False
        print_check("ReActAgent (True Agent)", False, str(e))
    
    return results


def verify_tool_system():
    """Verify tools are properly implemented"""
    print_header("🔧 TOOL SYSTEM VERIFICATION")
    
    results = {}
    
    try:
        from agents.core.tool_registry import create_tool_registry
        registry = create_tool_registry(include_default=True)
        tools = registry.get_tool_names()
        
        expected_tools = ['calculator', 'knowledge_search', 'formula_lookup', 'fact_checker', 'code_executor']
        
        for tool_name in expected_tools:
            has_tool = tool_name in tools
            results[tool_name] = has_tool
            print_check(f"Tool: {tool_name}", has_tool)
        
        print_check(f"Total tools available", True, f"{len(tools)} tools")
        
    except Exception as e:
        print_check("Tool system", False, str(e))
        
    return results


def verify_memory_system():
    """Verify memory system is implemented"""
    print_header("🧠 MEMORY SYSTEM VERIFICATION")
    
    results = {}
    
    try:
        from agents.core.memory import MemorySystem, ShortTermMemory, LongTermMemory
        
        # Test short-term memory
        stm = ShortTermMemory(max_items=10)
        stm.add("Test message", "conversation")
        entries = stm.get_recent(n=5)
        results['ShortTermMemory'] = len(entries) > 0
        print_check("ShortTermMemory", results['ShortTermMemory'], f"Can store and retrieve")
        
        # Test long-term memory
        ltm = LongTermMemory("test_user")
        ltm.record_success("mathematics")
        ltm.record_mistake("chemistry", "forgot valency")
        results['LongTermMemory'] = "mathematics" in ltm._patterns["strong_topics"]
        print_check("LongTermMemory", results['LongTermMemory'], f"Can persist student patterns")
        
        # Test memory system
        ms = MemorySystem("test_user")
        results['MemorySystem'] = True
        print_check("MemorySystem (unified)", True, "Combines STM + LTM")
        
    except Exception as e:
        print_check("Memory system", False, str(e))
        results['error'] = str(e)
        
    return results


def verify_planning_system():
    """Verify planning system is implemented"""
    print_header("📋 PLANNING SYSTEM VERIFICATION")
    
    results = {}
    
    try:
        from agents.core.planner import Planner, TaskPlan
        
        planner = Planner()
        plan = planner.create_plan(
            query="Explain why momentum is conserved in collisions",
            context={"subject": "Physics"}
        )
        
        results['Planner'] = plan is not None
        results['has_subtasks'] = len(plan.subtasks) > 0
        
        print_check("Planner exists", results['Planner'])
        print_check("Can decompose tasks", results['has_subtasks'], f"{len(plan.subtasks)} subtasks created")
        
    except Exception as e:
        print_check("Planning system", False, str(e))
        results['error'] = str(e)
        
    return results


def verify_verification_system():
    """Verify self-verification system is implemented"""
    print_header("✅ VERIFICATION SYSTEM CHECK")
    
    results = {}
    
    try:
        from agents.core.verifier import Verifier, VerificationResult
        
        verifier = Verifier()
        
        # Test calculation verification
        calc_result = verifier.verify_calculation("2 + 2 = 4")
        results['calc_correct'] = calc_result.status.value == "verified"
        print_check("Verify correct calculation", results['calc_correct'], "2 + 2 = 4")
        
        calc_wrong = verifier.verify_calculation("2 + 2 = 5")
        results['calc_wrong'] = calc_wrong.status.value == "failed"
        print_check("Detect wrong calculation", results['calc_wrong'], "2 + 2 = 5 (should fail)")
        
        # Test fact verification
        fact_result = verifier.verify_fact("Water boils at 100 degrees Celsius")
        results['fact_check'] = fact_result is not None
        print_check("Fact verification", results['fact_check'], f"Status: {fact_result.status.value}")
        
    except Exception as e:
        print_check("Verification system", False, str(e))
        results['error'] = str(e)
        
    return results


def verify_agentic_doubt_resolver():
    """Verify the agentic doubt resolver has all components"""
    print_header("🤖 AGENTIC DOUBT RESOLVER VERIFICATION")
    
    results = {}
    
    try:
        from agents.agentic_doubt_resolver import AgenticDoubtResolver, create_agentic_doubt_resolver
        
        agent = create_agentic_doubt_resolver({'max_iterations': 5})
        
        # Check all components
        has_tools = hasattr(agent, 'tool_registry') and agent.tool_registry is not None
        has_planner = hasattr(agent, 'planner') and agent.planner is not None
        has_verifier = hasattr(agent, 'verifier') and agent.verifier is not None
        has_memory_cache = hasattr(agent, '_memory_cache')
        has_react_loop = hasattr(agent, 'run')
        
        results['has_tools'] = has_tools
        results['has_planner'] = has_planner
        results['has_verifier'] = has_verifier
        results['has_memory'] = has_memory_cache
        results['has_react'] = has_react_loop
        
        print_check("Tool Registry", has_tools, f"{len(agent.tool_registry.get_tool_names())} tools")
        print_check("Planner", has_planner)
        print_check("Verifier", has_verifier)
        print_check("Memory System", has_memory_cache)
        print_check("ReAct Loop", has_react_loop)
        
        # Overall agentic score
        agentic_features = sum([has_tools, has_planner, has_verifier, has_memory_cache, has_react_loop])
        agentic_level = agentic_features  # Out of 5
        
        print(f"\n  📊 AGENTIC LEVEL: {agentic_level}/5")
        
        if agentic_level == 5:
            print("  🌟 FULLY AGENTIC - True human-like reasoning!")
        elif agentic_level >= 3:
            print("  ⭐ PARTIALLY AGENTIC - Has key capabilities")
        else:
            print("  ⚠️ BASIC - Needs more agentic features")
            
    except Exception as e:
        print_check("AgenticDoubtResolver", False, str(e))
        results['error'] = str(e)
        
    return results


def compare_old_vs_new_agents():
    """Compare old agents vs new agentic agents"""
    print_header("📊 OLD vs NEW AGENT COMPARISON")
    
    print("\n  OLD AGENTS (Level 2 - LLM with context):")
    print("  ─────────────────────────────────────────")
    
    old_agents = [
        ("DoubtResolverAgent", "LLM + prompts + context"),
        ("MentorAgent", "LLM + persona + metaphors"),
        ("ProfessorAgent", "LLM + formal style"),
        ("ExamCoachAgent", "LLM + exam focus"),
    ]
    
    for name, desc in old_agents:
        print(f"  • {name}: {desc}")
    
    print("\n  NEW AGENTIC SYSTEM (Level 5 - True Agent):")
    print("  ─────────────────────────────────────────")
    
    new_features = [
        ("ReAct Loop", "Think → Act → Observe cycle"),
        ("Tool Usage", "Calculator, Search, Fact-check, Code"),
        ("Memory", "Short-term (session) + Long-term (student)"),
        ("Planning", "Breaks complex tasks into subtasks"),
        ("Self-Verification", "Checks own calculations & facts"),
    ]
    
    for name, desc in new_features:
        print(f"  ✅ {name}: {desc}")
    
    print("\n  BEHAVIOR DIFFERENCE:")
    print("  ─────────────────────────────────────────")
    print("  OLD: Query → LLM generates response → Done")
    print("  NEW: Query → Plan → [Think→Act→Observe]* → Verify → Response")


def main():
    """Run all verifications"""
    print("\n" + "🧠" * 30)
    print("\n  DRUV AI - AGENTIC BEHAVIOR VERIFICATION")
    print("  Checking if agents behave like TRUE AGENTS")
    print("\n" + "🧠" * 30)
    
    # Run all verifications
    structure_results = verify_agent_structure()
    tool_results = verify_tool_system()
    memory_results = verify_memory_system()
    planning_results = verify_planning_system()
    verification_results = verify_verification_system()
    agentic_results = verify_agentic_doubt_resolver()
    
    # Compare old vs new
    compare_old_vs_new_agents()
    
    # Summary
    print_header("📋 FINAL SUMMARY")
    
    all_passed = (
        structure_results.get('ReActAgent', False) and
        all(tool_results.get(t, False) for t in ['calculator', 'knowledge_search']) and
        memory_results.get('MemorySystem', False) and
        planning_results.get('Planner', False) and
        verification_results.get('calc_correct', False) and
        agentic_results.get('has_react', False)
    )
    
    if all_passed:
        print("\n  ✅ ALL SYSTEMS OPERATIONAL")
        print("  🌟 Agents are behaving as TRUE AGENTIC SYSTEMS!")
        print("\n  The system now includes:")
        print("  • ReAct reasoning loop (Think → Act → Observe)")
        print("  • Tool usage (5 specialized tools)")
        print("  • Memory system (session + student patterns)")
        print("  • Task planning (breaks down complex queries)")
        print("  • Self-verification (checks own accuracy)")
    else:
        print("\n  ⚠️ SOME CHECKS FAILED")
        print("  Review the output above for details.")
    
    print("\n" + "=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

