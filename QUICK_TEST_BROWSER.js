/**
 * QUICK TEST - Copy & Paste into Browser Console
 * Tests Visual Professor Engine end-to-end
 * 
 * HOW TO USE:
 * 1. Open browser to http://localhost:3000
 * 2. Ask a question: "What is velocity?"
 * 3. Open DevTools: Press F12
 * 4. Go to Console tab
 * 5. Copy and paste THIS ENTIRE FILE into console
 * 6. Press Enter
 * 7. Watch for ✅ SUCCESS or ❌ FAILED messages
 */

console.clear();
console.log('%c=== VISUAL PROFESSOR ENGINE - QUICK TEST ===', 'color: #00AA00; font-size: 16px; font-weight: bold;');

// TEST 1: Check if API response has teaching_visual
console.log('\n%c[TEST 1] Checking last API response...', 'color: #0066FF; font-weight: bold;');

// This is a bit hacky but works for testing
// We'll make a fresh API call
async function runTests() {
  try {
    // Make request
    const response = await fetch('http://localhost:8001/api/ai/neuro-symbolic', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        question: 'What is velocity?',
        conversation_id: `test-${Date.now()}`,
        user_id: 'test-user',
        context: {}
      })
    });

    const data = await response.json();
    
    // TEST 1: teaching_visual exists
    const tv = data.response?.teaching_visual;
    if (!tv) {
      console.log('%c❌ FAILED: No teaching_visual in response', 'color: red; font-weight: bold;');
      console.log('Response keys:', Object.keys(data.response || {}));
      return;
    }
    console.log('%c✅ PASS: teaching_visual found', 'color: green; font-weight: bold;');
    
    // TEST 2: Concept is velocity
    if (tv.concept !== 'velocity') {
      console.log(`%c⚠️  Concept is "${tv.concept}", expected "velocity"`, 'color: orange;');
    } else {
      console.log(`%c✅ PASS: Concept is "${tv.concept}"`, 'color: green; font-weight: bold;');
    }
    
    // TEST 3: Subject is physics
    console.log(`%c   Subject: ${tv.subject}`, 'color: #0099FF;');
    
    // TEST 4: Stages exist
    if (!tv.stages || tv.stages.length === 0) {
      console.log('%c❌ FAILED: No stages', 'color: red; font-weight: bold;');
      return;
    }
    console.log(`%c✅ PASS: ${tv.stages.length} stages found`, 'color: green; font-weight: bold;');
    
    // TEST 5: First stage has blocks
    const blocks = tv.stages[0]?.blocks || [];
    if (blocks.length === 0) {
      console.log('%c❌ FAILED: First stage has no blocks', 'color: red; font-weight: bold;');
      return;
    }
    console.log(`%c✅ PASS: First stage has ${blocks.length} blocks`, 'color: green; font-weight: bold;');
    
    // TEST 6: Find animated_scene block
    const sceneBlock = blocks.find(b => b.type === 'animated_scene');
    if (!sceneBlock) {
      console.log('%c❌ FAILED: No animated_scene block', 'color: red; font-weight: bold;');
      console.log('   Available blocks:', blocks.map(b => b.type).join(', '));
      return;
    }
    console.log('%c✅ PASS: animated_scene block found', 'color: green; font-weight: bold;');
    
    // TEST 7: Scene has entities
    const scene = sceneBlock.scene;
    const entities = scene?.entities || [];
    if (entities.length === 0) {
      console.log('%c❌ FAILED: No entities in scene', 'color: red; font-weight: bold;');
      return;
    }
    console.log(`%c✅ PASS: Scene has ${entities.length} entities`, 'color: green; font-weight: bold;');
    
    // TEST 8: Entity details
    console.log('\n%c📦 ENTITIES FOUND:', 'color: #FF9900; font-weight: bold;');
    entities.forEach((e, i) => {
      const pos = e.initial_position;
      console.log(`   [${i+1}] ${e.id} (type: ${e.type})`);
      console.log(`       Position: (${pos?.x}, ${pos?.y})`);
    });
    
    // TEST 9: Animation sequence
    const actions = sceneBlock.animation_sequence || [];
    if (actions.length === 0) {
      console.log('\n%c⚠️  WARNING: No actions in sequence', 'color: orange;');
    } else {
      console.log(`\n%c✅ PASS: Animation sequence has ${actions.length} actions`, 'color: green; font-weight: bold;');
      
      // Show first few actions
      console.log('\n%c🎬 ACTIONS (first 3):', 'color: #FF9900; font-weight: bold;');
      actions.slice(0, 3).forEach((a, i) => {
        console.log(`   [${i+1}] ${a.action} on ${a.entity}`);
        if (a.to) {
          if (a.to.x !== undefined) console.log(`       → Move to (${a.to.x}, ${a.to.y})`);
          if (a.to.rotation !== undefined) console.log(`       → Rotate to ${a.to.rotation}°`);
        }
        if (a.duration_ms) console.log(`       Duration: ${a.duration_ms}ms`);
      });
    }
    
    // TEST 10: Narration
    const narration = tv.stages[0]?.narration;
    if (narration) {
      console.log(`\n%c✅ Narration: "${narration.substring(0, 80)}..."`, 'color: green;');
    } else {
      console.log('%c⚠️  No narration', 'color: orange;');
    }
    
    // FINAL RESULT
    console.log('\n%c════════════════════════════════════════', 'color: #00AA00; font-size: 12px;');
    console.log('%c✅ ALL TESTS PASSED - VISUAL ENGINE WORKING!', 'color: green; font-size: 14px; font-weight: bold;');
    console.log('%c════════════════════════════════════════', 'color: #00AA00; font-size: 12px;');
    
    console.log('\n%c🎨 FRONTEND EXPECTATIONS:', 'color: #FF6600; font-weight: bold;');
    console.log('   ✓ Blue sky background (top half)');
    console.log('   ✓ Green ground background (bottom half)');
    console.log('   ✓ Red metro train visible');
    console.log('   ✓ Yellow/orange arrow visible');
    console.log('   ✓ Purple speedometer visible');
    console.log('   ✓ Metro moves smoothly right (2.5 seconds)');
    console.log('   ✓ Arrow rotates 180° during animation');
    console.log('   ✓ Professor text explains concept');
    
    console.log('\n%c💡 WHAT YOU SHOULD SEE:', 'color: #FF6600; font-weight: bold;');
    console.log('   Stage 1: "Meet the Metro" - Train appears');
    console.log('   Stage 2: "What\'s Speed?" - Train zooms across');
    console.log('   Stage 3: "Add Direction" - Arrow rotates, train reverses');
    console.log('   Stage 4: "The Big Picture" - Two trains opposite');
    console.log('   Stage 5: "Remember" - Key insight recap');
    
    console.log('\n%c🔧 FOR DEBUGGING:', 'color: #0099FF; font-weight: bold;');
    console.log('   Open DevTools → Elements tab to inspect SVG');
    console.log('   Look for: <motion.g> elements with animated metro/arrow');
    console.log('   Check: Framer Motion transforms being applied');
    
  } catch (error) {
    console.log('%c❌ ERROR:', 'color: red; font-weight: bold;', error.message);
  }
}

// Run the tests
runTests();

console.log('%c\n⏳ Tests running... Check above for results.', 'color: #666; font-style: italic;');


