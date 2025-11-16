/**
 * Visual Pipeline Test
 * Tests the complete flow from backend generation to frontend rendering
 */

const testVisualPipeline = async () => {
  console.log('\n=== VISUAL PIPELINE TEST ===\n');

  try {
    // Step 1: Send question to backend
    console.log('[TEST] 1. Sending question to backend...');
    const response = await fetch('http://localhost:8001/api/ai/neuro-symbolic', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: 'What is velocity?',
        conversation_id: 'test-session-' + Date.now(),
        user_id: 'test-user',
        context: {}
      })
    });

    const data = await response.json();
    console.log('[TEST] 2. Backend response received');
    console.log('[TEST] - Response fields:', Object.keys(data.response || {}));

    // Step 2: Check for teaching_visual
    const teaching_visual = data.response?.teaching_visual;
    if (!teaching_visual) {
      console.error('[TEST] ❌ FAILED: No teaching_visual in response!');
      console.log('[TEST] Full response:', JSON.stringify(data, null, 2));
      return;
    }

    console.log('[TEST] 3. Teaching visual found');
    console.log('[TEST] - Concept:', teaching_visual.concept);
    console.log('[TEST] - Subject:', teaching_visual.subject);
    console.log('[TEST] - Stages:', teaching_visual.stages?.length || 0);

    // Step 3: Check first stage
    if (!teaching_visual.stages || teaching_visual.stages.length === 0) {
      console.error('[TEST] ❌ FAILED: No stages in teaching visual!');
      return;
    }

    const firstStage = teaching_visual.stages[0];
    console.log('[TEST] 4. First stage analyzed:');
    console.log('[TEST] - Blocks:', firstStage.blocks?.length || 0);

    // Step 4: Find animated_scene block
    const sceneBlock = firstStage.blocks?.find(b => b.type === 'animated_scene');
    if (!sceneBlock) {
      console.error('[TEST] ❌ FAILED: No animated_scene block in first stage!');
      console.log('[TEST] Available block types:', firstStage.blocks?.map(b => b.type) || []);
      return;
    }

    console.log('[TEST] 5. Animated scene block found');
    console.log('[TEST] - Scene background:', sceneBlock.scene?.background);
    console.log('[TEST] - Entities:', sceneBlock.scene?.entities?.length || 0);
    if (sceneBlock.scene?.entities) {
      sceneBlock.scene.entities.forEach((entity, i) => {
        console.log(`[TEST]   Entity ${i+1}: ${entity.id} (type: ${entity.type})`);
        console.log(`[TEST]     Position: (${entity.initial_position?.x}, ${entity.initial_position?.y})`);
      });
    }
    console.log('[TEST] - Animation sequence:', sceneBlock.animation_sequence?.length || 0);
    if (sceneBlock.animation_sequence) {
      sceneBlock.animation_sequence.slice(0, 3).forEach((action, i) => {
        console.log(`[TEST]   Action ${i+1}: ${action.action} on ${action.entity}`);
      });
    }

    console.log('[TEST] ✅ SUCCESS: Complete visual pipeline working!');
    console.log('[TEST] Frontend should now render entities with animations');

  } catch (error) {
    console.error('[TEST] ❌ ERROR:', error);
  }
};

// Run test
testVisualPipeline();


