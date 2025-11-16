"""
Lottie Asset Manager - Manages Lottie animation packs
Provides CDN URLs for Lottie animations with SVG fallback system
"""
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# LOTTIE ASSET PACK STRUCTURE
# ============================================================================

LOTTIE_CDN_BASE = "https://cdn.ai-tutor.in/lottie"

LOTTIE_PACKS: Dict[str, Dict[str, str]] = {
    # PHYSICS PACKS
    'physics/motion': {
        'intro': f'{LOTTIE_CDN_BASE}/physics/motion/intro.json',
        'metro_intro': f'{LOTTIE_CDN_BASE}/physics/motion/metro_intro.json',
        'metro_moves_north': f'{LOTTIE_CDN_BASE}/physics/motion/metro_moves_north.json',
        'metro_turns_south': f'{LOTTIE_CDN_BASE}/physics/motion/metro_turns_south.json',
        'vector_display': f'{LOTTIE_CDN_BASE}/physics/motion/vector_display.json',
        'summary_comparison': f'{LOTTIE_CDN_BASE}/physics/motion/summary_comparison.json',
        'process_intro': f'{LOTTIE_CDN_BASE}/physics/motion/process_intro.json',
        'process_step_1': f'{LOTTIE_CDN_BASE}/physics/motion/process_step_1.json',
        'process_step_2': f'{LOTTIE_CDN_BASE}/physics/motion/process_step_2.json',
        'process_step_3': f'{LOTTIE_CDN_BASE}/physics/motion/process_step_3.json',
        'process_step_4': f'{LOTTIE_CDN_BASE}/physics/motion/process_step_4.json',
        'process_summary': f'{LOTTIE_CDN_BASE}/physics/motion/process_summary.json',
    },
    
    'physics/projectile': {
        'intro': f'{LOTTIE_CDN_BASE}/physics/projectile/intro.json',
        'ball_launch': f'{LOTTIE_CDN_BASE}/physics/projectile/ball_launch.json',
        'velocity_decomposition': f'{LOTTIE_CDN_BASE}/physics/projectile/velocity_decomposition.json',
        'ball_flies_parabola': f'{LOTTIE_CDN_BASE}/physics/projectile/ball_flies_parabola.json',
        'horizontal_motion_analysis': f'{LOTTIE_CDN_BASE}/physics/projectile/horizontal_motion_analysis.json',
        'ball_lands': f'{LOTTIE_CDN_BASE}/physics/projectile/ball_lands.json',
    },
    
    'physics/forces': {
        'intro': f'{LOTTIE_CDN_BASE}/physics/forces/intro.json',
        'car_stationary': f'{LOTTIE_CDN_BASE}/physics/forces/car_stationary.json',
        'car_at_rest': f'{LOTTIE_CDN_BASE}/physics/forces/car_at_rest.json',
        'car_moving_constant': f'{LOTTIE_CDN_BASE}/physics/forces/car_moving_constant.json',
        'car_braking': f'{LOTTIE_CDN_BASE}/physics/forces/car_braking.json',
        'inertia_demo': f'{LOTTIE_CDN_BASE}/physics/forces/inertia_demo.json',
    },
    
    # CHEMISTRY PACKS
    'chemistry/bonding': {
        'intro': f'{LOTTIE_CDN_BASE}/chemistry/bonding/intro.json',
        'atom_intro': f'{LOTTIE_CDN_BASE}/chemistry/bonding/atom_intro.json',
        'shells_highlight': f'{LOTTIE_CDN_BASE}/chemistry/bonding/shells_highlight.json',
        'octet_demonstration': f'{LOTTIE_CDN_BASE}/chemistry/bonding/octet_demonstration.json',
        'carbon_bonding': f'{LOTTIE_CDN_BASE}/chemistry/bonding/carbon_bonding.json',
        'valency_chart': f'{LOTTIE_CDN_BASE}/chemistry/bonding/valency_chart.json',
        'atoms_separate': f'{LOTTIE_CDN_BASE}/chemistry/bonding/atoms_separate.json',
        'electron_share': f'{LOTTIE_CDN_BASE}/chemistry/bonding/electron_share.json',
        'bond_forms': f'{LOTTIE_CDN_BASE}/chemistry/bonding/bond_forms.json',
        'bond_types_demo': f'{LOTTIE_CDN_BASE}/chemistry/bonding/bond_types_demo.json',
        'molecule_formed': f'{LOTTIE_CDN_BASE}/chemistry/bonding/molecule_formed.json',
    },
    
    'chemistry/reactions': {
        'intro': f'{LOTTIE_CDN_BASE}/chemistry/reactions/intro.json',
        'acid_comparison': f'{LOTTIE_CDN_BASE}/chemistry/reactions/acid_comparison.json',
        'ph_scale_display': f'{LOTTIE_CDN_BASE}/chemistry/reactions/ph_scale_display.json',
        'h_ion_release': f'{LOTTIE_CDN_BASE}/chemistry/reactions/h_ion_release.json',
        'dissociation_comparison': f'{LOTTIE_CDN_BASE}/chemistry/reactions/dissociation_comparison.json',
        'ph_test_demo': f'{LOTTIE_CDN_BASE}/chemistry/reactions/ph_test_demo.json',
    },
    
    # BIOLOGY PACKS
    'biology/photosynthesis': {
        'intro': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/intro.json',
        'leaf_intro': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/leaf_intro.json',
        'inputs_arrive': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/inputs_arrive.json',
        'reaction_process': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/reaction_process.json',
        'outputs_produced': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/outputs_produced.json',
        'equation_display': f'{LOTTIE_CDN_BASE}/biology/photosynthesis/equation_display.json',
    },
    
    'biology/respiration': {
        'intro': f'{LOTTIE_CDN_BASE}/biology/respiration/intro.json',
        'mitochondria_intro': f'{LOTTIE_CDN_BASE}/biology/respiration/mitochondria_intro.json',
        'fuel_entry': f'{LOTTIE_CDN_BASE}/biology/respiration/fuel_entry.json',
        'glucose_breakdown': f'{LOTTIE_CDN_BASE}/biology/respiration/glucose_breakdown.json',
        'products_exit': f'{LOTTIE_CDN_BASE}/biology/respiration/products_exit.json',
        'equation_cycle': f'{LOTTIE_CDN_BASE}/biology/respiration/equation_cycle.json',
    },
    
    # MATHEMATICS PACKS
    'math/graphs': {
        'intro': f'{LOTTIE_CDN_BASE}/math/graphs/intro.json',
        'parabola_draw': f'{LOTTIE_CDN_BASE}/math/graphs/parabola_draw.json',
        'equation_display': f'{LOTTIE_CDN_BASE}/math/graphs/equation_display.json',
        'vertex_highlight': f'{LOTTIE_CDN_BASE}/math/graphs/vertex_highlight.json',
        'roots_display': f'{LOTTIE_CDN_BASE}/math/graphs/roots_display.json',
        'real_world_overlay': f'{LOTTIE_CDN_BASE}/math/graphs/real_world_overlay.json',
        'line_draw': f'{LOTTIE_CDN_BASE}/math/graphs/line_draw.json',
        'slope_demo': f'{LOTTIE_CDN_BASE}/math/graphs/slope_demo.json',
        'intercept_highlight': f'{LOTTIE_CDN_BASE}/math/graphs/intercept_highlight.json',
        'real_examples': f'{LOTTIE_CDN_BASE}/math/graphs/real_examples.json',
    },
    
    # GENERIC PACKS (fallback)
    'generic': {
        'intro': f'{LOTTIE_CDN_BASE}/generic/intro.json',
        'generic_intro': f'{LOTTIE_CDN_BASE}/generic/generic_intro.json',
        'generic_aspect_1': f'{LOTTIE_CDN_BASE}/generic/generic_aspect_1.json',
        'generic_aspect_2': f'{LOTTIE_CDN_BASE}/generic/generic_aspect_2.json',
        'generic_aspect_3': f'{LOTTIE_CDN_BASE}/generic/generic_aspect_3.json',
        'generic_aspect_4': f'{LOTTIE_CDN_BASE}/generic/generic_aspect_4.json',
        'generic_summary': f'{LOTTIE_CDN_BASE}/generic/generic_summary.json',
        'generic_detail_1': f'{LOTTIE_CDN_BASE}/generic/generic_detail_1.json',
        'generic_detail_2': f'{LOTTIE_CDN_BASE}/generic/generic_detail_2.json',
    }
}

# ============================================================================
# ASSET MANAGER CLASS
# ============================================================================

class LottieAssetManager:
    """Manages Lottie animation assets with fallback system"""
    
    def __init__(self):
        self.cdn_base = LOTTIE_CDN_BASE
        self.packs = LOTTIE_PACKS
        self.cache: Dict[str, Any] = {}
        self.fallback_enabled = True
    
    def get_asset_url(
        self,
        pack_name: str,
        animation_name: str
    ) -> Optional[str]:
        """
        Get Lottie asset URL
        
        Args:
            pack_name: Pack name (e.g., 'physics/motion')
            animation_name: Animation name (e.g., 'metro_intro')
        
        Returns:
            CDN URL for Lottie animation, or None if not found
        """
        pack = self.packs.get(pack_name)
        if not pack:
            logger.warning(f"⚠️ Lottie pack not found: {pack_name}, using generic")
            pack = self.packs.get('generic', {})
        
        url = pack.get(animation_name)
        if not url:
            logger.warning(f"⚠️ Lottie animation not found: {animation_name} in {pack_name}")
            # Try to get generic animation
            generic_pack = self.packs.get('generic', {})
            url = generic_pack.get('intro', f'{self.cdn_base}/generic/intro.json')
        
        return url
    
    def get_asset_for_stage(
        self,
        pack_name: str,
        stage_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get Lottie asset URL for a stage based on stage data
        
        Args:
            pack_name: Lottie pack name
            stage_data: Stage data from concept library
        
        Returns:
            CDN URL for appropriate Lottie animation
        """
        animation_name = stage_data.get('animation', '')
        stage_id = stage_data.get('stage_id', '')
        
        # Try to get animation by name first
        url = self.get_asset_url(pack_name, animation_name)
        
        if not url:
            # Fallback: try to infer from stage_id
            if stage_id == 'intro':
                url = self.get_asset_url(pack_name, 'intro')
            elif stage_id == 'summary':
                url = self.get_asset_url(pack_name, 'summary')
            elif stage_id.startswith('step_'):
                step_num = stage_id.split('_')[1] if '_' in stage_id else '1'
                url = self.get_asset_url(pack_name, f'process_step_{step_num}')
        
        return url
    
    def get_lottie_assets_for_stage(
        self,
        pack_name: str,
        stage_data: Dict[str, Any],
        stage_index: int
    ) -> List[Dict[str, Any]]:
        """
        Get list of Lottie assets for a stage
        
        Returns:
            List of Lottie asset configurations
        """
        url = self.get_asset_for_stage(pack_name, stage_data)
        
        if not url:
            return []
        
        return [{
            'url': url,
            'loop': stage_data.get('animation_loop', False),
            'autoplay': True,
            'speed': 1.0,
            'stage_index': stage_index
        }]
    
    def pack_exists(self, pack_name: str) -> bool:
        """Check if a Lottie pack exists"""
        return pack_name in self.packs
    
    def list_pack_animations(self, pack_name: str) -> List[str]:
        """List all animations in a pack"""
        pack = self.packs.get(pack_name, {})
        return list(pack.keys())
    
    def list_all_packs(self) -> List[str]:
        """List all available Lottie packs"""
        return list(self.packs.keys())
    
    def add_custom_animation(
        self,
        pack_name: str,
        animation_name: str,
        url: str
    ) -> None:
        """
        Add a custom Lottie animation to a pack
        
        Args:
            pack_name: Pack name
            animation_name: Animation name
            url: CDN URL for the Lottie file
        """
        if pack_name not in self.packs:
            self.packs[pack_name] = {}
        
        self.packs[pack_name][animation_name] = url
        logger.info(f"✅ Added custom Lottie animation: {pack_name}/{animation_name}")
    
    def enable_fallback(self, enabled: bool = True) -> None:
        """Enable or disable fallback to SVG animations"""
        self.fallback_enabled = enabled
    
    def should_use_svg_fallback(
        self,
        pack_name: str,
        animation_name: str
    ) -> bool:
        """
        Determine if SVG fallback should be used
        
        Returns:
            True if SVG fallback should be used instead of Lottie
        """
        if not self.fallback_enabled:
            return False
        
        # Always provide Lottie URL (placeholder)
        # Frontend will handle fallback to SVG if Lottie load fails
        return False

# ============================================================================
# ASSET VERIFICATION (for future use)
# ============================================================================

class LottieAssetVerifier:
    """Verifies Lottie assets are accessible (for production)"""
    
    def __init__(self, asset_manager: LottieAssetManager):
        self.asset_manager = asset_manager
        self.verified_urls: Dict[str, bool] = {}
    
    async def verify_asset(self, url: str) -> bool:
        """
        Verify that a Lottie asset is accessible
        
        Args:
            url: CDN URL to verify
        
        Returns:
            True if asset is accessible
        """
        # Check cache first
        if url in self.verified_urls:
            return self.verified_urls[url]
        
        # In production, this would make an actual HTTP request
        # For now, we assume all placeholder URLs are "valid"
        # This method is prepared for future implementation
        
        self.verified_urls[url] = True
        return True
    
    async def verify_pack(self, pack_name: str) -> Dict[str, bool]:
        """
        Verify all assets in a pack
        
        Returns:
            Dictionary mapping animation names to verification results
        """
        pack = self.asset_manager.packs.get(pack_name, {})
        results = {}
        
        for animation_name, url in pack.items():
            results[animation_name] = await self.verify_asset(url)
        
        return results

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_lottie_url(pack_name: str, animation_name: str) -> str:
    """Quick helper to get Lottie URL"""
    manager = LottieAssetManager()
    url = manager.get_asset_url(pack_name, animation_name)
    return url or f'{LOTTIE_CDN_BASE}/generic/intro.json'

def get_pack_for_subject(subject: str) -> str:
    """Get default Lottie pack name for a subject"""
    pack_map = {
        'physics': 'physics/motion',
        'chemistry': 'chemistry/bonding',
        'biology': 'biology/photosynthesis',
        'mathematics': 'math/graphs',
        'math': 'math/graphs'
    }
    return pack_map.get(subject.lower(), 'generic')

