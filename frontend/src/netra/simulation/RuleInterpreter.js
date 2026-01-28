/**
 * 📜 RULE INTERPRETER
 * ===================
 * 
 * Parses and executes simulation rules from SimulationScript.
 * Rules are event/state-driven, not time-delay based.
 * 
 * Rule syntax:
 * - when: "state == 'moving' && velocity > 0"
 * - then: ["velocity -= friction * dt", "emit('moving')"]
 */

/**
 * Compile a rule condition into an executable function
 */
export function compileCondition(conditionStr) {
  // Convert string condition to function
  // Supports: ==, !=, >, <, >=, <=, &&, ||
  
  return (state, constants) => {
    try {
      // Create evaluation context
      const context = {
        state: state.current,
        ...state.variables,
        ...constants,
        dt: state.dt || 0.016  // Delta time (60fps default)
      };
      
      // Replace variable names with context lookups
      let evalStr = conditionStr;
      
      // Handle state comparison
      evalStr = evalStr.replace(/state\s*==\s*'(\w+)'/g, (_, s) => `state === '${s}'`);
      evalStr = evalStr.replace(/state\s*!=\s*'(\w+)'/g, (_, s) => `state !== '${s}'`);
      
      // Create function with context variables in scope
      const fn = new Function(...Object.keys(context), `return ${evalStr}`);
      return fn(...Object.values(context));
    } catch (e) {
      console.warn(`[RuleInterpreter] Condition parse error: ${conditionStr}`, e);
      return false;
    }
  };
}

/**
 * Compile a rule action into an executable function
 */
export function compileAction(actionStr) {
  // Parse action string into executable
  
  // Variable assignment: "velocity -= friction * dt"
  const assignMatch = actionStr.match(/^(\w+)\s*([+\-*/]?=)\s*(.+)$/);
  if (assignMatch) {
    const [_, variable, operator, expression] = assignMatch;
    return (state, constants, runtime) => {
      try {
        const context = {
          ...state.variables,
          ...constants,
          dt: state.dt || 0.016
        };
        
        const fn = new Function(...Object.keys(context), `return ${expression}`);
        const value = fn(...Object.values(context));
        
        switch (operator) {
          case '=':
            state.variables[variable] = value;
            break;
          case '+=':
            state.variables[variable] = (state.variables[variable] || 0) + value;
            break;
          case '-=':
            state.variables[variable] = (state.variables[variable] || 0) - value;
            break;
          case '*=':
            state.variables[variable] = (state.variables[variable] || 1) * value;
            break;
          case '/=':
            state.variables[variable] = (state.variables[variable] || 1) / value;
            break;
        }
        
        return { type: 'assignment', variable, value: state.variables[variable] };
      } catch (e) {
        console.warn(`[RuleInterpreter] Assignment error: ${actionStr}`, e);
        return null;
      }
    };
  }
  
  // State change: "state = 'stopped'"
  const stateMatch = actionStr.match(/^state\s*=\s*'(\w+)'$/);
  if (stateMatch) {
    const [_, newState] = stateMatch;
    return (state, constants, runtime) => {
      const oldState = state.current;
      state.current = newState;
      runtime.emit('state_change', { from: oldState, to: newState });
      return { type: 'state_change', from: oldState, to: newState };
    };
  }
  
  // Emit event: "emit('motion_started')"
  const emitMatch = actionStr.match(/^emit\s*\(\s*'(\w+)'\s*\)$/);
  if (emitMatch) {
    const [_, eventName] = emitMatch;
    return (state, constants, runtime) => {
      runtime.emit(eventName, { state: state.current, variables: { ...state.variables } });
      return { type: 'emit', event: eventName };
    };
  }
  
  // Show entity: "show(entity_id)"
  const showMatch = actionStr.match(/^show\s*\(\s*(\w+)\s*\)$/);
  if (showMatch) {
    const [_, entityId] = showMatch;
    return (state, constants, runtime) => {
      runtime.showEntity(entityId);
      return { type: 'show', entity: entityId };
    };
  }
  
  // Hide entity: "hide(entity_id)"
  const hideMatch = actionStr.match(/^hide\s*\(\s*(\w+)\s*\)$/);
  if (hideMatch) {
    const [_, entityId] = hideMatch;
    return (state, constants, runtime) => {
      runtime.hideEntity(entityId);
      return { type: 'hide', entity: entityId };
    };
  }
  
  // Highlight entity: "highlight(entity_id)"
  const highlightMatch = actionStr.match(/^highlight\s*\(\s*(\w+)\s*\)$/);
  if (highlightMatch) {
    const [_, entityId] = highlightMatch;
    return (state, constants, runtime) => {
      runtime.highlightEntity(entityId);
      return { type: 'highlight', entity: entityId };
    };
  }
  
  // Unhighlight entity: "unhighlight(entity_id)"
  const unhighlightMatch = actionStr.match(/^unhighlight\s*\(\s*(\w+)\s*\)$/);
  if (unhighlightMatch) {
    const [_, entityId] = unhighlightMatch;
    return (state, constants, runtime) => {
      runtime.unhighlightEntity(entityId);
      return { type: 'unhighlight', entity: entityId };
    };
  }
  
  // Move entity: "move(entity_id, dx)"
  const moveMatch = actionStr.match(/^move\s*\(\s*(\w+)\s*,\s*(.+)\s*\)$/);
  if (moveMatch) {
    const [_, entityId, expression] = moveMatch;
    return (state, constants, runtime) => {
      try {
        const context = { ...state.variables, ...constants, dt: state.dt || 0.016 };
        const fn = new Function(...Object.keys(context), `return ${expression}`);
        const delta = fn(...Object.values(context));
        runtime.moveEntity(entityId, delta, 0);
        return { type: 'move', entity: entityId, delta };
      } catch (e) {
        console.warn(`[RuleInterpreter] Move error: ${actionStr}`, e);
        return null;
      }
    };
  }
  
  // Unknown action - log warning
  console.warn(`[RuleInterpreter] Unknown action: ${actionStr}`);
  return () => ({ type: 'unknown', action: actionStr });
}

/**
 * Compile a complete rule
 */
export function compileRule(rule) {
  const condition = compileCondition(rule.when);
  const actions = rule.then.map(actionStr => compileAction(actionStr));
  
  return {
    id: rule.id,
    condition,
    actions,
    lastFired: null,
    fireCount: 0
  };
}

/**
 * Compile all rules from a SimulationScript
 */
export function compileRules(rules) {
  return rules.map(rule => compileRule(rule));
}

/**
 * Rule execution engine
 */
export class RuleEngine {
  constructor() {
    this.rules = [];
    this.firedEvents = new Set();
  }
  
  loadRules(ruleDefinitions) {
    this.rules = compileRules(ruleDefinitions);
  }
  
  /**
   * Evaluate and execute all applicable rules
   */
  tick(state, constants, runtime) {
    const results = [];
    
    for (const rule of this.rules) {
      // Check condition
      if (rule.condition(state, constants)) {
        // Execute actions
        for (const action of rule.actions) {
          const result = action(state, constants, runtime);
          if (result) {
            results.push({ ruleId: rule.id, ...result });
          }
        }
        
        rule.lastFired = Date.now();
        rule.fireCount++;
      }
    }
    
    return results;
  }
  
  /**
   * Reset rule state
   */
  reset() {
    for (const rule of this.rules) {
      rule.lastFired = null;
      rule.fireCount = 0;
    }
    this.firedEvents.clear();
  }
}

export default RuleEngine;
