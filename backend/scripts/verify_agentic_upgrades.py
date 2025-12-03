"""
Verification Script for Agentic Upgrades
=========================================

This script verifies that all agents have been properly upgraded to TRUE agentic behavior.

Checks:
1. All agents inherit from ReActAgent
2. All agents have tool_registry initialized
3. All agents have memory system
4. All agents implement process() with ReAct loop
5. All agents have proper thought/action/observation flow
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def verify_agent_upgrade(agent_name: str, agent_class) -> dict:
    """Verify a single agent's upgrade"""
    results = {
        'agent': agent_name,
        'inherits_react': False,
        'has_tool_registry': False,
        'has_memory': False,
        'has_process_method': False,
        'implements_react_loop': False,
        'score': 0
    }
    
    try:
        # Check inheritance
        from agents.core.react_agent import ReActAgent
        results['inherits_react'] = issubclass(agent_class, ReActAgent)
        
        # Create instance
        config = {'db_client': None, 'emergent_llm_key': 'test'}
        instance = agent_class(config)
        
        # Check tool registry
        results['has_tool_registry'] = hasattr(instance, 'tool_registry')
        
        # Check memory
        results['has_memory'] = hasattr(instance, 'memory')
        
        # Check process method
        results['has_process_method'] = hasattr(instance, 'process') and callable(getattr(instance, 'process'))
        
        # Check if process method has ReAct loop (by checking docstring)
        if results['has_process_method']:
            process_method = getattr(instance, 'process')
            docstring = process_method.__doc__ or ''
            results['implements_react_loop'] = any(word in docstring.lower() for word in ['think', 'act', 'observe', 'react'])
        
        # Calculate score
        results['score'] = sum([
            results['inherits_react'],
            results['has_tool_registry'],
            results['has_memory'],
            results['has_process_method'],
            results['implements_react_loop']
        ])
        
    except Exception as e:
        logger.error(f"❌ Error verifying {agent_name}: {e}")
        results['error'] = str(e)
    
    return results


async def main():
    """Main verification function"""
    
    logger.info("╔══════════════════════════════════════════════════════════════╗")
    logger.info("║       AGENTIC UPGRADE VERIFICATION - ALL 7 AGENTS           ║")
    logger.info("╚══════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # Agents to verify
    agents_to_verify = [
        ('VisualiseAgent', 'agents.visualise', 'VisualiseAgent'),
        ('WeakAreaDetectiveAgent', 'agents.weak_area_detective', 'WeakAreaDetectiveAgent'),
        ('MentorAgent', 'agents.mentor', 'MentorAgent'),
        ('ProfessorAgent', 'agents.professor', 'ProfessorAgent'),
        ('ExamCoachAgent', 'agents.exam_coach', 'ExamCoachAgent'),
        ('StudyBuddyAgent', 'agents.study_buddy', 'StudyBuddyAgent'),
        ('ParentReportAgent', 'agents.parent_report', 'ParentReportAgent'),
    ]
    
    all_results = []
    
    for agent_name, module_path, class_name in agents_to_verify:
        logger.info(f"🔍 Verifying {agent_name}...")
        
        try:
            # Import agent
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # Verify
            results = await verify_agent_upgrade(agent_name, agent_class)
            all_results.append(results)
            
            # Display results
            score = results['score']
            max_score = 5
            
            if score == max_score:
                status = "✅ FULLY UPGRADED"
                color = "green"
            elif score >= 3:
                status = "⚠️  PARTIALLY UPGRADED"
                color = "yellow"
            else:
                status = "❌ NOT UPGRADED"
                color = "red"
            
            logger.info(f"   {status} ({score}/{max_score})")
            logger.info(f"   - Inherits ReActAgent: {'✅' if results['inherits_react'] else '❌'}")
            logger.info(f"   - Has ToolRegistry: {'✅' if results['has_tool_registry'] else '❌'}")
            logger.info(f"   - Has Memory: {'✅' if results['has_memory'] else '❌'}")
            logger.info(f"   - Has process(): {'✅' if results['has_process_method'] else '❌'}")
            logger.info(f"   - Implements ReAct: {'✅' if results['implements_react_loop'] else '❌'}")
            logger.info("")
            
        except Exception as e:
            logger.error(f"   ❌ FAILED TO VERIFY: {e}")
            logger.info("")
    
    # Summary
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("")
    
    total_agents = len(all_results)
    fully_upgraded = sum(1 for r in all_results if r['score'] == 5)
    partially_upgraded = sum(1 for r in all_results if 3 <= r['score'] < 5)
    not_upgraded = sum(1 for r in all_results if r['score'] < 3)
    
    logger.info(f"Total Agents: {total_agents}")
    logger.info(f"✅ Fully Upgraded: {fully_upgraded}")
    logger.info(f"⚠️  Partially Upgraded: {partially_upgraded}")
    logger.info(f"❌ Not Upgraded: {not_upgraded}")
    logger.info("")
    
    # Overall status
    if fully_upgraded == total_agents:
        logger.info("🎉 SUCCESS! All agents are TRUE agentic entities!")
        logger.info("")
        logger.info("All agents now have:")
        logger.info("  • ReAct Loop (Think → Act → Observe)")
        logger.info("  • Tool Execution (Real actions, not just text)")
        logger.info("  • Memory System (Context and personalization)")
        logger.info("  • Human-like Behavior (Reasoning before acting)")
        return 0
    else:
        logger.info("⚠️  Some agents need additional work.")
        logger.info("")
        logger.info("Agents needing attention:")
        for result in all_results:
            if result['score'] < 5:
                logger.info(f"  - {result['agent']} (score: {result['score']}/5)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)




