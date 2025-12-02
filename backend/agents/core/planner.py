"""
📋 Planner - Task Decomposition & Planning
==========================================

The Planner breaks complex tasks into manageable subtasks.
This is crucial for handling multi-step problems like:
- "Solve this JEE problem and explain each step"
- "Compare these two concepts and give examples"
- "Help me understand and then test me"

Planning Process:
1. Analyze the query complexity
2. Identify required subtasks
3. Determine dependencies between tasks
4. Create execution order
5. Track progress

This enables agents to handle complex requests systematically.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a subtask"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """Types of subtasks"""
    UNDERSTAND = "understand"  # Parse and understand the question
    RESEARCH = "research"      # Look up information
    CALCULATE = "calculate"    # Perform calculations
    EXPLAIN = "explain"        # Generate explanation
    VERIFY = "verify"          # Verify correctness
    EXAMPLE = "example"        # Provide examples
    VISUALIZE = "visualize"    # Create visualization
    QUIZ = "quiz"              # Generate quiz question
    SUMMARIZE = "summarize"    # Summarize findings


@dataclass
class SubTask:
    """A single subtask in the plan"""
    id: str
    task_type: TaskType
    description: str
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    tools_needed: List[str] = field(default_factory=list)
    priority: int = 1  # 1 = highest
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.task_type.value,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "tools_needed": self.tools_needed,
            "priority": self.priority
        }


@dataclass
class TaskPlan:
    """A complete plan for handling a request"""
    query: str
    complexity: str  # simple, moderate, complex
    subtasks: List[SubTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_task(self, task: SubTask) -> None:
        """Add a subtask to the plan"""
        self.subtasks.append(task)
    
    def get_next_task(self) -> Optional[SubTask]:
        """Get the next task to execute based on dependencies"""
        for task in self.subtasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if dependencies are met
            deps_met = all(
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if self.get_task(dep_id)
            )
            
            if deps_met:
                return task
        
        return None
    
    def get_task(self, task_id: str) -> Optional[SubTask]:
        """Get a task by ID"""
        for task in self.subtasks:
            if task.id == task_id:
                return task
        return None
    
    def mark_complete(self, task_id: str, result: str) -> None:
        """Mark a task as complete"""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.result = result
    
    def mark_failed(self, task_id: str, error: str) -> None:
        """Mark a task as failed"""
        task = self.get_task(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.result = f"Error: {error}"
    
    def is_complete(self) -> bool:
        """Check if all tasks are complete"""
        return all(
            t.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED]
            for t in self.subtasks
        )
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress statistics"""
        total = len(self.subtasks)
        completed = sum(1 for t in self.subtasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.subtasks if t.status == TaskStatus.FAILED)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "remaining": total - completed - failed,
            "progress_pct": (completed / total * 100) if total > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "complexity": self.complexity,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "progress": self.get_progress()
        }


class Planner:
    """
    Creates execution plans for complex requests.
    
    Usage:
        planner = Planner()
        plan = planner.create_plan(
            query="Solve this physics problem and explain each step",
            context={"subject": "Physics"}
        )
        
        while not plan.is_complete():
            task = plan.get_next_task()
            # Execute task...
            plan.mark_complete(task.id, result)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def create_plan(self, query: str, context: Dict[str, Any] = None) -> TaskPlan:
        """
        Create an execution plan for the given query.
        
        Args:
            query: The user's request
            context: Context including subject, student profile, etc.
        
        Returns:
            TaskPlan with ordered subtasks
        """
        context = context or {}
        
        # Analyze query complexity
        complexity = self._analyze_complexity(query)
        
        # Create plan
        plan = TaskPlan(query=query, complexity=complexity)
        
        # Generate subtasks based on query type
        subtasks = self._generate_subtasks(query, context, complexity)
        
        for task in subtasks:
            plan.add_task(task)
        
        logger.info(f"📋 Created plan with {len(subtasks)} tasks (complexity: {complexity})")
        
        return plan
    
    def _analyze_complexity(self, query: str) -> str:
        """Analyze query complexity"""
        query_lower = query.lower()
        
        # Complex indicators
        complex_indicators = [
            'step by step', 'explain each', 'compare and',
            'multiple', 'several', 'first then', 'also',
            'prove that', 'derive', 'solve and explain'
        ]
        
        # Simple indicators
        simple_indicators = [
            'what is', 'define', 'quick', 'simple',
            'just', 'only', 'brief'
        ]
        
        complex_count = sum(1 for ind in complex_indicators if ind in query_lower)
        simple_count = sum(1 for ind in simple_indicators if ind in query_lower)
        
        if complex_count >= 2 or len(query.split()) > 30:
            return "complex"
        elif simple_count > 0 or len(query.split()) < 10:
            return "simple"
        else:
            return "moderate"
    
    def _generate_subtasks(
        self, 
        query: str, 
        context: Dict[str, Any],
        complexity: str
    ) -> List[SubTask]:
        """Generate subtasks based on query analysis"""
        query_lower = query.lower()
        tasks = []
        task_id = 0
        
        def new_id():
            nonlocal task_id
            task_id += 1
            return f"task_{task_id}"
        
        # Always start with understanding
        understand_id = new_id()
        tasks.append(SubTask(
            id=understand_id,
            task_type=TaskType.UNDERSTAND,
            description="Parse and understand the student's question",
            priority=1
        ))
        
        # Check for calculation needs
        if any(w in query_lower for w in ['solve', 'calculate', 'find', 'compute', 'evaluate']):
            calc_id = new_id()
            tasks.append(SubTask(
                id=calc_id,
                task_type=TaskType.CALCULATE,
                description="Perform required calculations",
                dependencies=[understand_id],
                tools_needed=["calculator", "code_executor"],
                priority=2
            ))
            
            # Add verification for calculations
            tasks.append(SubTask(
                id=new_id(),
                task_type=TaskType.VERIFY,
                description="Verify calculation results",
                dependencies=[calc_id],
                tools_needed=["fact_checker"],
                priority=3
            ))
        
        # Check for research/lookup needs
        if any(w in query_lower for w in ['what is', 'explain', 'define', 'how does', 'why']):
            research_id = new_id()
            tasks.append(SubTask(
                id=research_id,
                task_type=TaskType.RESEARCH,
                description="Look up relevant information and concepts",
                dependencies=[understand_id],
                tools_needed=["knowledge_search", "formula_lookup"],
                priority=2
            ))
        
        # Check for comparison needs
        if any(w in query_lower for w in ['compare', 'difference', 'vs', 'versus', 'contrast']):
            tasks.append(SubTask(
                id=new_id(),
                task_type=TaskType.RESEARCH,
                description="Research both concepts for comparison",
                dependencies=[understand_id],
                tools_needed=["knowledge_search"],
                priority=2
            ))
        
        # Check for example needs
        if any(w in query_lower for w in ['example', 'show me', 'demonstrate', 'practice']):
            tasks.append(SubTask(
                id=new_id(),
                task_type=TaskType.EXAMPLE,
                description="Generate relevant examples",
                dependencies=[understand_id],
                priority=3
            ))
        
        # Always end with explanation
        explain_deps = [t.id for t in tasks if t.id != understand_id]
        tasks.append(SubTask(
            id=new_id(),
            task_type=TaskType.EXPLAIN,
            description="Generate clear explanation for student",
            dependencies=explain_deps if explain_deps else [understand_id],
            priority=4
        ))
        
        # For complex queries, add summary
        if complexity == "complex":
            tasks.append(SubTask(
                id=new_id(),
                task_type=TaskType.SUMMARIZE,
                description="Summarize key points",
                dependencies=[t.id for t in tasks],
                priority=5
            ))
        
        return tasks
    
    def get_plan_description(self, plan: TaskPlan) -> str:
        """Get a human-readable description of the plan"""
        lines = [f"📋 Plan for: {plan.query[:50]}...", f"Complexity: {plan.complexity}", ""]
        lines.append("Steps:")
        
        for i, task in enumerate(plan.subtasks, 1):
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.SKIPPED: "⏭️"
            }.get(task.status, "⏳")
            
            lines.append(f"{i}. {status_icon} {task.description}")
            if task.tools_needed:
                lines.append(f"   Tools: {', '.join(task.tools_needed)}")
        
        progress = plan.get_progress()
        lines.append(f"\nProgress: {progress['completed']}/{progress['total']} ({progress['progress_pct']:.0f}%)")
        
        return "\n".join(lines)

