"""
Druv Visual Builder - Config Generator
Generates JSON/Protobuf configs for Satya Runtime
"""

from typing import Dict, Any, List, Optional
import json
import hashlib
from datetime import datetime
from pydantic import BaseModel, Field


class VisualConfig(BaseModel):
    """Visual configuration for Satya Runtime"""
    
    # Identity
    config_id: str
    visual_name: str
    description: str
    
    # Grammar reference
    grammar_id: str
    grammar_version: str
    
    # Asset references
    assets: Dict[str, str]  # Parameter name -> Asset ID
    
    # Parameter values
    parameters: Dict[str, Any]  # Parameter name -> Value
    
    # Cultural context
    cultural_hook: Optional[str] = None  # e.g., "How many Dabbawalas to push your auto?"
    
    # Metadata
    created_by: str  # SME/Teacher ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    
    # Validation
    is_validated: bool = False
    validation_hash: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return self.json(indent=2, exclude_none=True)
    
    def to_protobuf(self) -> bytes:
        """
        Convert to Protobuf for size optimization
        
        Returns:
            Protobuf binary
        """
        # TODO: Implement Protobuf serialization
        # For now, return JSON as bytes
        return self.to_json().encode('utf-8')
    
    def calculate_hash(self) -> str:
        """Calculate hash for validation"""
        config_dict = self.dict(exclude={'validation_hash', 'created_at'})
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_json.encode()).hexdigest()


class ConfigGenerator:
    """Generates visual configs from builder inputs"""
    
    def __init__(self):
        self.configs: Dict[str, VisualConfig] = {}
    
    def generate_config(
        self,
        grammar_id: str,
        grammar_version: str,
        assets: Dict[str, str],
        parameters: Dict[str, Any],
        cultural_hook: Optional[str] = None,
        created_by: str = "unknown"
    ) -> VisualConfig:
        """
        Generate visual config from builder inputs
        
        Args:
            grammar_id: Grammar to use
            grammar_version: Grammar version
            assets: Parameter name -> Asset ID mapping
            parameters: Parameter values
            cultural_hook: Optional cultural hook text
            created_by: Creator ID
        
        Returns:
            Generated VisualConfig
        """
        config_id = self._generate_config_id(grammar_id, assets, parameters)
        
        config = VisualConfig(
            config_id=config_id,
            visual_name=f"{grammar_id}_{config_id[:8]}",
            description=f"Visual for {grammar_id}",
            grammar_id=grammar_id,
            grammar_version=grammar_version,
            assets=assets,
            parameters=parameters,
            cultural_hook=cultural_hook,
            created_by=created_by
        )
        
        # Calculate validation hash
        config.validation_hash = config.calculate_hash()
        
        self.configs[config_id] = config
        
        return config
    
    def _generate_config_id(
        self,
        grammar_id: str,
        assets: Dict[str, str],
        parameters: Dict[str, Any]
    ) -> str:
        """Generate unique config ID"""
        data = {
            'grammar_id': grammar_id,
            'assets': sorted(assets.items()),
            'parameters': sorted(parameters.items())
        }
        json_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(json_str.encode())
        return hash_obj.hexdigest()[:16]
    
    def get_config(self, config_id: str) -> Optional[VisualConfig]:
        """Get config by ID"""
        return self.configs.get(config_id)
    
    def validate_config(self, config: VisualConfig) -> Dict[str, Any]:
        """
        Validate config before publishing
        
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        # Check hash integrity
        calculated_hash = config.calculate_hash()
        if config.validation_hash != calculated_hash:
            errors.append("Config hash mismatch - may have been tampered with")
        
        # Check required fields
        if not config.assets:
            errors.append("No assets specified")
        
        if not config.parameters:
            errors.append("No parameters specified")
        
        # Check cultural hook
        if not config.cultural_hook:
            warnings.append("No cultural hook specified - may reduce relatability")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }























