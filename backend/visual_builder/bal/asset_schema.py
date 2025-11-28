"""
Bharat Asset Library - Asset Schema
Pydantic models for asset metadata and validation
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class CulturalRegion(str, Enum):
    """Indian cultural regions"""
    NORTH_INDIA = "north_india"
    SOUTH_INDIA = "south_india"
    EAST_INDIA = "east_india"
    WEST_INDIA = "west_india"
    NORTHEAST_INDIA = "northeast_india"
    CENTRAL_INDIA = "central_india"
    PAN_INDIA = "pan_india"


class AssetFormat(str, Enum):
    """Supported asset formats"""
    GLTF = "gltf"  # 3D (WebGL)
    LOTTIE = "lottie"  # 2D animations
    SVG = "svg"  # Vector graphics
    PNG = "png"  # Raster images
    WEBP = "webp"  # Modern raster


class LODLevel(str, Enum):
    """Level of Detail"""
    HIGH = "high"  # WebGL, full detail
    MEDIUM = "medium"  # Canvas 2D, optimized
    LOW = "low"  # SVG, minimal detail


class AssetLOD(BaseModel):
    """Level of Detail variant"""
    level: LODLevel
    format: AssetFormat
    url: str  # CDN URL
    size_bytes: int
    compressed: bool = True
    compression_ratio: Optional[float] = None  # e.g., 0.3 means 70% compression


class PhysicsBehavior(BaseModel):
    """Physics properties for interactive simulations"""
    mass: Optional[float] = None  # kg
    friction_coefficient: Optional[float] = None  # 0-1
    density: Optional[float] = None  # kg/m³
    elasticity: Optional[float] = None  # 0-1
    pressure: Optional[float] = None  # bar/Pa
    temperature: Optional[float] = None  # Celsius
    # Add more as needed


class AssetMetadata(BaseModel):
    """Metadata for each asset"""
    # Cultural context
    cultural_region: List[CulturalRegion] = Field(default_factory=list)
    regional_variants: Dict[str, str] = Field(default_factory=dict)  # e.g., {"tamil": "தானியங்கி", "hindi": "ऑटो"}
    
    # Educational context
    syllabus_topic: List[str] = Field(default_factory=list)  # e.g., ["physics.friction", "physics.motion"]
    ncert_reference: Optional[str] = None  # e.g., "Class 11, Chapter 5, Page 102"
    exam_relevance: List[str] = Field(default_factory=list)  # e.g., ["JEE", "NEET", "CBSE"]
    
    # Physics/Real-world properties
    physics_behavior: Optional[PhysicsBehavior] = None
    real_world_measurement: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"diameter_cm": 7.2, "weight_kg": 0.16}
    
    # Citations and validation
    citation_url: Optional[str] = None
    source: Optional[str] = None  # e.g., "NCERT", "Wikipedia", "SME Research"
    
    # Tags for search
    tags: List[str] = Field(default_factory=list)  # e.g., ["cricket", "sports", "sphere"]
    
    # Creator info
    created_by: str  # Teacher/SME ID
    approved_by: List[str] = Field(default_factory=list)  # List of teacher IDs who approved
    approval_date: Optional[datetime] = None
    
    # Version control
    version: str = "1.0.0"
    changelog: List[str] = Field(default_factory=list)


class Asset(BaseModel):
    """Complete asset definition"""
    # Core identity
    asset_id: str = Field(..., description="Unique asset identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this asset represents")
    
    # Asset files (multiple LODs)
    lods: List[AssetLOD] = Field(..., min_items=1, description="At least one LOD required")
    
    # Metadata
    metadata: AssetMetadata
    
    # Validation status
    is_validated: bool = False
    validation_hash: Optional[str] = None  # Cryptographic hash for integrity
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('lods')
    def validate_lods(cls, v):
        """Ensure at least one LOD exists"""
        if not v:
            raise ValueError("At least one LOD required")
        return v
    
    @validator('asset_id')
    def validate_asset_id(cls, v):
        """Asset ID must be lowercase, alphanumeric with underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError("Asset ID must be alphanumeric with underscores only")
        return v.lower()
    
    def get_best_lod(self, device_capability: str = "medium", bandwidth_kbps: int = 1000) -> AssetLOD:
        """
        Select best LOD based on device and bandwidth
        
        Args:
            device_capability: "high" (flagship), "medium" (mid-range), "low" (budget)
            bandwidth_kbps: Available bandwidth in kbps
        
        Returns:
            Best matching AssetLOD
        """
        # Low bandwidth (< 50kbps) → always use LOW
        if bandwidth_kbps < 50:
            return next((lod for lod in self.lods if lod.level == LODLevel.LOW), self.lods[0])
        
        # High-end device + good bandwidth → HIGH
        if device_capability == "high" and bandwidth_kbps > 1000:
            return next((lod for lod in self.lods if lod.level == LODLevel.HIGH), self.lods[-1])
        
        # Default to MEDIUM
        return next((lod for lod in self.lods if lod.level == LODLevel.MEDIUM), self.lods[0])
    
    def matches_query(self, query: Dict[str, Any]) -> bool:
        """
        Check if asset matches search query
        
        Args:
            query: Dict with keys like 'tags', 'syllabus_topic', 'cultural_region', etc.
        
        Returns:
            True if asset matches query
        """
        # Check tags
        if 'tags' in query:
            query_tags = set(query['tags'])
            asset_tags = set(self.metadata.tags)
            if not query_tags.intersection(asset_tags):
                return False
        
        # Check syllabus topic
        if 'syllabus_topic' in query:
            query_topics = set(query['syllabus_topic'])
            asset_topics = set(self.metadata.syllabus_topic)
            if not query_topics.intersection(asset_topics):
                return False
        
        # Check cultural region
        if 'cultural_region' in query:
            query_regions = set(query['cultural_region'])
            asset_regions = set(self.metadata.cultural_region)
            if not query_regions.intersection(asset_regions) and CulturalRegion.PAN_INDIA not in asset_regions:
                return False
        
        return True


# Example assets for reference
EXAMPLE_ASSETS = {
    "auto_rickshaw": Asset(
        asset_id="auto_rickshaw",
        name="Auto Rickshaw",
        description="Three-wheeled motorized vehicle common in Indian cities",
        lods=[
            AssetLOD(
                level=LODLevel.HIGH,
                format=AssetFormat.GLTF,
                url="https://cdn.druvai.com/assets/auto_rickshaw_h.gltf",
                size_bytes=250000,
                compressed=True,
                compression_ratio=0.3
            ),
            AssetLOD(
                level=LODLevel.MEDIUM,
                format=AssetFormat.LOTTIE,
                url="https://cdn.druvai.com/assets/auto_rickshaw_m.json",
                size_bytes=50000,
                compressed=True,
                compression_ratio=0.5
            ),
            AssetLOD(
                level=LODLevel.LOW,
                format=AssetFormat.SVG,
                url="https://cdn.druvai.com/assets/auto_rickshaw_l.svg",
                size_bytes=5000,
                compressed=False
            )
        ],
        metadata=AssetMetadata(
            cultural_region=[CulturalRegion.PAN_INDIA],
            syllabus_topic=["physics.friction", "physics.motion", "physics.force"],
            ncert_reference="Class 11, Chapter 5, Page 102",
            exam_relevance=["JEE", "NEET", "CBSE"],
            physics_behavior=PhysicsBehavior(
                mass=450.0,  # kg
                friction_coefficient=0.7
            ),
            real_world_measurement={
                "length_m": 2.5,
                "width_m": 1.2,
                "height_m": 1.8,
                "weight_kg": 450
            },
            tags=["vehicle", "transport", "urban", "friction", "motion"],
            created_by="sme_physics_001",
            approved_by=["teacher_cbse_001", "teacher_iit_001"],
            version="1.0.0"
        ),
        is_validated=True
    ),
    "cricket_ball": Asset(
        asset_id="cricket_ball",
        name="Cricket Ball",
        description="Standard cricket ball used in matches",
        lods=[
            AssetLOD(
                level=LODLevel.MEDIUM,
                format=AssetFormat.SVG,
                url="https://cdn.druvai.com/assets/cricket_ball.svg",
                size_bytes=3000,
                compressed=False
            )
        ],
        metadata=AssetMetadata(
            cultural_region=[CulturalRegion.PAN_INDIA],
            syllabus_topic=["physics.circular_motion", "physics.projectile"],
            ncert_reference="Class 11, Chapter 4, Page 78",
            exam_relevance=["JEE", "CBSE"],
            physics_behavior=PhysicsBehavior(
                mass=0.16,  # kg
                diameter=0.072  # m (7.2 cm)
            ),
            real_world_measurement={
                "diameter_cm": 7.2,
                "circumference_cm": 22.6,
                "weight_kg": 0.16
            },
            tags=["sports", "cricket", "sphere", "projectile", "circular_motion"],
            created_by="sme_physics_002",
            approved_by=["teacher_cbse_002"],
            version="1.0.0"
        ),
        is_validated=True
    )
}






