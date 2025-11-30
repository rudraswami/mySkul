"""
Bharat Asset Library - Asset Validator
SME approval workflow and validation
"""

from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import json
from .asset_schema import Asset, AssetMetadata


class ValidationStatus:
    """Validation status constants"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


class AssetValidator:
    """
    Handles asset validation workflow
    Requires approval from SME + Teacher + Cultural Reviewer
    """
    
    def __init__(self):
        self.required_approvers = {
            "sme": 1,  # Subject Matter Expert (IIT professor)
            "teacher": 1,  # CBSE teacher
            "cultural_reviewer": 1  # Regional teacher
        }
    
    def validate_asset(self, asset: Asset) -> Dict[str, any]:
        """
        Validate asset structure and metadata
        
        Args:
            asset: Asset to validate
        
        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not asset.asset_id:
            errors.append("Asset ID is required")
        
        if not asset.name:
            errors.append("Asset name is required")
        
        if not asset.lods:
            errors.append("At least one LOD is required")
        
        # Check metadata completeness
        if not asset.metadata.syllabus_topic:
            warnings.append("No syllabus topics specified")
        
        if not asset.metadata.cultural_region:
            warnings.append("No cultural region specified")
        
        if not asset.metadata.tags:
            warnings.append("No tags specified (will affect searchability)")
        
        # Check physics behavior if applicable
        if asset.metadata.physics_behavior:
            pb = asset.metadata.physics_behavior
            if pb.mass and pb.mass <= 0:
                errors.append("Mass must be positive")
            if pb.friction_coefficient and (pb.friction_coefficient < 0 or pb.friction_coefficient > 1):
                errors.append("Friction coefficient must be between 0 and 1")
        
        # Check approval status
        if not asset.is_validated:
            warnings.append("Asset not yet validated by required approvers")
        
        # Check if all required approvers have approved
        required_count = sum(self.required_approvers.values())
        if len(asset.metadata.approved_by) < required_count:
            warnings.append(
                f"Only {len(asset.metadata.approved_by)}/{required_count} required approvers have approved"
            )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "can_publish": len(errors) == 0 and asset.is_validated
        }
    
    def add_approval(
        self,
        asset: Asset,
        approver_id: str,
        approver_type: str,  # "sme", "teacher", or "cultural_reviewer"
        notes: Optional[str] = None
    ) -> Asset:
        """
        Add approval from an approver
        
        Args:
            asset: Asset to approve
            approver_id: ID of approver
            approver_type: Type of approver
            notes: Optional approval notes
        
        Returns:
            Updated asset
        """
        if approver_id not in asset.metadata.approved_by:
            asset.metadata.approved_by.append(approver_id)
            asset.metadata.changelog.append(
                f"{datetime.utcnow().isoformat()}: Approved by {approver_type} ({approver_id})"
            )
            if notes:
                asset.metadata.changelog.append(f"  Notes: {notes}")
        
        # Check if all required approvers have approved
        if len(asset.metadata.approved_by) >= sum(self.required_approvers.values()):
            asset.is_validated = True
            asset.metadata.approval_date = datetime.utcnow()
            asset.validation_hash = self._calculate_validation_hash(asset)
        
        asset.updated_at = datetime.utcnow()
        return asset
    
    def reject_asset(
        self,
        asset: Asset,
        rejector_id: str,
        reason: str
    ) -> Asset:
        """
        Reject asset with reason
        
        Args:
            asset: Asset to reject
            rejector_id: ID of rejector
            reason: Rejection reason
        
        Returns:
            Updated asset
        """
        asset.is_validated = False
        asset.metadata.changelog.append(
            f"{datetime.utcnow().isoformat()}: Rejected by {rejector_id}"
        )
        asset.metadata.changelog.append(f"  Reason: {reason}")
        asset.updated_at = datetime.utcnow()
        return asset
    
    def _calculate_validation_hash(self, asset: Asset) -> str:
        """
        Calculate cryptographic hash for asset validation
        
        Args:
            asset: Asset to hash
        
        Returns:
            SHA-256 hash as hex string
        """
        # Create deterministic representation
        validation_data = {
            "asset_id": asset.asset_id,
            "version": asset.metadata.version,
            "approved_by": sorted(asset.metadata.approved_by),
            "approval_date": asset.metadata.approval_date.isoformat() if asset.metadata.approval_date else None,
            "metadata_hash": self._hash_metadata(asset.metadata)
        }
        
        json_str = json.dumps(validation_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _hash_metadata(self, metadata: AssetMetadata) -> str:
        """Calculate hash of metadata (excluding approval info)"""
        metadata_dict = metadata.dict(exclude={"approved_by", "approval_date", "changelog"})
        json_str = json.dumps(metadata_dict, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def verify_validation_hash(self, asset: Asset) -> bool:
        """
        Verify that validation hash matches current asset state
        
        Args:
            asset: Asset to verify
        
        Returns:
            True if hash matches
        """
        if not asset.validation_hash:
            return False
        
        current_hash = self._calculate_validation_hash(asset)
        return current_hash == asset.validation_hash












