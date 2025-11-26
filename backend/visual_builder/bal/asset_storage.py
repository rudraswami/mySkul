"""
Bharat Asset Library - Asset Storage
S3/CloudFront integration for asset storage and CDN delivery
"""

import os
import hashlib
from typing import Optional, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class AssetStorage:
    """
    Handles asset storage in S3 and CDN delivery via CloudFront
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        cloudfront_distribution_id: Optional[str] = None,
        region: str = "ap-south-1"  # Mumbai region for India
    ):
        """
        Initialize asset storage
        
        Args:
            bucket_name: S3 bucket name (defaults to env var)
            cloudfront_distribution_id: CloudFront distribution ID (defaults to env var)
            region: AWS region (defaults to Mumbai for India)
        """
        self.bucket_name = bucket_name or os.getenv("BAL_S3_BUCKET", "druv-bal-assets")
        self.cloudfront_distribution_id = cloudfront_distribution_id or os.getenv("BAL_CLOUDFRONT_ID")
        self.region = region
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3', region_name=region)
        
        # CloudFront base URL (will be set if distribution ID provided)
        self.cdn_base_url = None
        if self.cloudfront_distribution_id:
            # In production, fetch from CloudFront API
            self.cdn_base_url = f"https://{self.cloudfront_distribution_id}.cloudfront.net"
        else:
            # Fallback to S3 URL
            self.cdn_base_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com"
    
    def upload_asset(
        self,
        asset_id: str,
        file_path: str,
        lod_level: str,
        content_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload asset file to S3
        
        Args:
            asset_id: Unique asset identifier
            file_path: Local file path to upload
            lod_level: Level of detail (high/medium/low)
            content_type: MIME type
            metadata: Additional S3 metadata
        
        Returns:
            CDN URL of uploaded asset
        """
        # Construct S3 key: assets/{asset_id}/{lod_level}/filename
        file_name = os.path.basename(file_path)
        s3_key = f"assets/{asset_id}/{lod_level}/{file_name}"
        
        try:
            # Upload to S3
            extra_args = {
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000',  # 1 year cache
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Return CDN URL
            cdn_url = f"{self.cdn_base_url}/{s3_key}"
            logger.info(f"✅ Uploaded asset {asset_id} ({lod_level}) to {cdn_url}")
            
            return cdn_url
            
        except ClientError as e:
            logger.error(f"❌ Failed to upload asset {asset_id}: {e}")
            raise
    
    def get_asset_url(self, asset_id: str, lod_level: str, file_name: str) -> str:
        """
        Get CDN URL for an asset (without uploading)
        
        Args:
            asset_id: Asset identifier
            lod_level: Level of detail
            file_name: File name
        
        Returns:
            CDN URL
        """
        s3_key = f"assets/{asset_id}/{lod_level}/{file_name}"
        return f"{self.cdn_base_url}/{s3_key}"
    
    def delete_asset(self, asset_id: str, lod_level: Optional[str] = None) -> bool:
        """
        Delete asset(s) from S3
        
        Args:
            asset_id: Asset identifier
            lod_level: If provided, delete only this LOD; otherwise delete all
        
        Returns:
            True if successful
        """
        try:
            if lod_level:
                # Delete specific LOD
                prefix = f"assets/{asset_id}/{lod_level}/"
                self._delete_prefix(prefix)
            else:
                # Delete all LODs
                prefix = f"assets/{asset_id}/"
                self._delete_prefix(prefix)
            
            logger.info(f"✅ Deleted asset {asset_id} ({lod_level or 'all'})")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to delete asset {asset_id}: {e}")
            return False
    
    def _delete_prefix(self, prefix: str):
        """Delete all objects with given prefix"""
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
        for page in pages:
            if 'Contents' in page:
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects}
                )
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file for integrity verification
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex digest of SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def invalidate_cache(self, asset_id: str, lod_level: Optional[str] = None):
        """
        Invalidate CloudFront cache for asset
        
        Args:
            asset_id: Asset identifier
            lod_level: Optional LOD level
        """
        if not self.cloudfront_distribution_id:
            logger.warning("CloudFront distribution ID not configured, skipping cache invalidation")
            return
        
        try:
            cloudfront = boto3.client('cloudfront')
            
            if lod_level:
                paths = [f"/assets/{asset_id}/{lod_level}/*"]
            else:
                paths = [f"/assets/{asset_id}/*"]
            
            cloudfront.create_invalidation(
                DistributionId=self.cloudfront_distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"{asset_id}_{lod_level or 'all'}_{datetime.utcnow().isoformat()}"
                }
            )
            
            logger.info(f"✅ Invalidated CloudFront cache for {asset_id}")
            
        except ClientError as e:
            logger.error(f"❌ Failed to invalidate cache: {e}")


