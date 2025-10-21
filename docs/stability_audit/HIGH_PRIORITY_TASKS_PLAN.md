# High-Priority Tasks - Implementation Plan

**Status**: Ready for Implementation
**Created**: January 2025
**Priority**: P0 - CRITICAL

---

## TASK 1: MongoDB _id to UUID Migration 🔴 CRITICAL

### Problem Statement
MongoDB's default `_id` field uses ObjectId, which is not JSON serializable. This causes:
- Manual deletion of `_id` in 750+ code locations
- Potential data inconsistencies
- API serialization issues
- Debugging difficulties (ObjectId vs UUID confusion)

### Current State Analysis
**Models Already Use UUIDs**: ✅
- User: `user_id` (UUID)
- ChatSession: `session_id` (UUID)
- MockTest: `test_id` (UUID)
- Subscription: `subscription_id` (UUID)
- All other models: Already have UUID primary keys

**The Problem**: MongoDB still creates `_id` ObjectId field automatically
**Current Workaround**: 750+ instances of manual `_id` deletion

### Solution Strategy

**Phase 1: Preparation** (1-2 hours)
1. Create database backup script
2. Create UUID-MongoDB adapter utility
3. Test adapter in development

**Phase 2: Implementation** (2-3 hours)
1. Create `MongoUUIDAdapter` class
2. Modify database initialization to disable auto `_id`
3. Set UUID fields as `_id` in MongoDB
4. Update all collection insertions
5. Create migration script for existing data

**Phase 3: Testing** (1-2 hours)
1. Test all CRUD operations
2. Verify no `_id` deletion code needed
3. Test serialization
4. Performance testing

**Phase 4: Cleanup** (1 hour)
1. Remove all `del doc['_id']` statements
2. Update documentation
3. Final testing

### Technical Implementation

**1. UUID-MongoDB Adapter**
```python
# /app/backend/utils/mongo_uuid.py

import uuid
from typing import Any, Dict
from datetime import datetime

class MongoUUIDAdapter:
    """Adapter to use UUIDs as MongoDB _id field"""
    
    @staticmethod
    def prepare_for_insert(doc: Dict[str, Any], id_field: str = None) -> Dict[str, Any]:
        """
        Prepare document for MongoDB insertion with UUID as _id
        
        Args:
            doc: Document dictionary (from Pydantic .dict())
            id_field: Name of UUID field (e.g., 'user_id', 'session_id')
        
        Returns:
            Document ready for MongoDB with _id set to UUID
        """
        doc_copy = doc.copy()
        
        # If id_field specified, use it as _id
        if id_field and id_field in doc_copy:
            doc_copy['_id'] = doc_copy[id_field]
            # Keep the original field for backward compatibility
            # del doc_copy[id_field]  # Optional: remove duplicate
        
        # Convert datetime objects to ISO strings
        for key, value in doc_copy.items():
            if isinstance(value, datetime):
                doc_copy[key] = value.isoformat()
        
        return doc_copy
    
    @staticmethod
    def prepare_from_mongo(doc: Dict[str, Any], id_field: str = None) -> Dict[str, Any]:
        """
        Prepare document retrieved from MongoDB for API response
        
        Args:
            doc: Document from MongoDB
            id_field: Name of UUID field to restore from _id
        
        Returns:
            Clean document without _id, with UUID field restored
        """
        if not doc:
            return doc
        
        doc_copy = doc.copy()
        
        # Restore UUID field from _id
        if '_id' in doc_copy and id_field:
            if id_field not in doc_copy:
                doc_copy[id_field] = doc_copy['_id']
            del doc_copy['_id']
        
        return doc_copy
    
    @staticmethod
    def convert_query(query: Dict[str, Any], id_field: str = None) -> Dict[str, Any]:
        """
        Convert query with UUID field to use _id
        
        Example:
            {'user_id': 'uuid-123'} -> {'_id': 'uuid-123'}
        """
        query_copy = query.copy()
        
        if id_field and id_field in query_copy:
            query_copy['_id'] = query_copy[id_field]
            del query_copy[id_field]
        
        return query_copy
```

**2. Usage Pattern**
```python
# INSERT Example
user = User(user_id=str(uuid.uuid4()), email="test@example.com", ...)
doc = MongoUUIDAdapter.prepare_for_insert(user.dict(), id_field='user_id')
await db.users.insert_one(doc)

# QUERY Example
query = MongoUUIDAdapter.convert_query({'user_id': user_id}, id_field='user_id')
user_doc = await db.users.find_one(query)
user_clean = MongoUUIDAdapter.prepare_from_mongo(user_doc, id_field='user_id')

# UPDATE Example
query = MongoUUIDAdapter.convert_query({'user_id': user_id}, id_field='user_id')
await db.users.update_one(query, {'$set': {'email': 'new@example.com'}})
```

**3. Migration Script**
```python
# /app/backend/scripts/migrate_to_uuid_ids.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
sys.path.append('/app/backend')
from core.config import settings

async def migrate_collection(db, collection_name: str, id_field: str):
    """Migrate a collection to use UUID as _id"""
    
    print(f"Migrating {collection_name}...")
    collection = db[collection_name]
    
    # 1. Backup collection
    backup_name = f"{collection_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating backup: {backup_name}")
    await db[backup_name].insert_many(await collection.find().to_list(None))
    
    # 2. Create temporary collection with UUID _id
    temp_name = f"{collection_name}_temp"
    
    # 3. Copy documents with UUID as _id
    cursor = collection.find()
    migrated = 0
    async for doc in cursor:
        if id_field in doc:
            doc['_id'] = doc[id_field]
            # Remove old MongoDB ObjectId if present
            if '_id' in doc and hasattr(doc['_id'], '__class__') and doc['_id'].__class__.__name__ == 'ObjectId':
                doc['_id'] = doc[id_field]
            
            await db[temp_name].insert_one(doc)
            migrated += 1
    
    print(f"Migrated {migrated} documents")
    
    # 4. Drop old collection and rename temp
    await collection.drop()
    await db[temp_name].rename(collection_name)
    
    print(f"✅ {collection_name} migration complete")

async def main():
    """Run migration for all collections"""
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.dhruv_ai
    
    collections_to_migrate = [
        ('users', 'user_id'),
        ('chat_sessions', 'session_id'),
        ('chat_messages', 'message_id'),
        ('mock_tests', 'test_id'),
        ('test_attempts', 'attempt_id'),
        ('subscriptions', 'subscription_id'),
        ('payment_transactions', 'transaction_id'),
        ('usage_tracking', 'usage_id'),
        ('study_progress', 'progress_id'),
        ('auto_note_sessions', 'session_id'),
    ]
    
    for collection_name, id_field in collections_to_migrate:
        try:
            await migrate_collection(db, collection_name, id_field)
        except Exception as e:
            print(f"❌ Error migrating {collection_name}: {e}")
            print("Rollback available from backup collection")
    
    print("\n✅ All migrations complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Rollback Plan

**If Migration Fails:**
```python
# Rollback script
async def rollback_migration(db, collection_name: str):
    """Rollback to backup"""
    backups = await db.list_collection_names()
    latest_backup = sorted([b for b in backups if b.startswith(f"{collection_name}_backup_")])[-1]
    
    await db[collection_name].drop()
    await db[latest_backup].rename(collection_name)
    print(f"✅ Rolled back to {latest_backup}")
```

### Success Criteria
- ✅ No `del doc['_id']` statements needed
- ✅ All API endpoints return clean JSON
- ✅ All tests passing
- ✅ No performance degradation
- ✅ Backup available for rollback

### Estimated Time: 5-8 hours

---

## TASK 2: Database Migration System 🔴 CRITICAL

### Problem Statement
No systematic way to handle schema changes:
- Manual database updates required
- No version control for schema
- No rollback capability
- Risk of inconsistent state across environments

### Solution Strategy

**Approach: Custom Migration System** (Lighter than Alembic for MongoDB)

### Implementation

**1. Migration Framework**
```python
# /app/backend/migrations/migration_base.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase

class Migration(ABC):
    """Base class for all migrations"""
    
    version: str  # "001", "002", etc.
    description: str
    
    @abstractmethod
    async def up(self, db: AsyncIOMotorDatabase) -> None:
        """Apply migration"""
        pass
    
    @abstractmethod
    async def down(self, db: AsyncIOMotorDatabase) -> None:
        """Rollback migration"""
        pass
    
    async def log_migration(self, db: AsyncIOMotorDatabase, direction: str) -> None:
        """Log migration execution"""
        await db.migrations.insert_one({
            'version': self.version,
            'description': self.description,
            'direction': direction,  # 'up' or 'down'
            'executed_at': datetime.utcnow(),
            'status': 'completed'
        })

class MigrationRunner:
    """Runs migrations in order"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_current_version(self) -> str:
        """Get latest applied migration version"""
        latest = await self.db.migrations.find_one(
            {'direction': 'up', 'status': 'completed'},
            sort=[('version', -1)]
        )
        return latest['version'] if latest else '000'
    
    async def run_migrations(self, target_version: str = None) -> None:
        """Run all pending migrations up to target version"""
        current = await self.get_current_version()
        
        # Import all migration files
        from migrations import migration_registry
        
        for migration in migration_registry.get_pending(current, target_version):
            print(f"Running migration {migration.version}: {migration.description}")
            await migration.up(self.db)
            await migration.log_migration(self.db, 'up')
            print(f"✅ Migration {migration.version} complete")
    
    async def rollback(self, steps: int = 1) -> None:
        """Rollback last N migrations"""
        # Get last N applied migrations
        applied = await self.db.migrations.find(
            {'direction': 'up', 'status': 'completed'}
        ).sort('version', -1).limit(steps).to_list(steps)
        
        from migrations import migration_registry
        
        for migration_doc in applied:
            migration = migration_registry.get(migration_doc['version'])
            print(f"Rolling back {migration.version}: {migration.description}")
            await migration.down(self.db)
            await migration.log_migration(self.db, 'down')
            print(f"✅ Rollback {migration.version} complete")
```

**2. Example Migration**
```python
# /app/backend/migrations/001_add_user_timezone.py

from migrations.migration_base import Migration
from motor.motor_asyncio import AsyncIOMotorDatabase

class Migration001(Migration):
    version = "001"
    description = "Add timezone field to users"
    
    async def up(self, db: AsyncIOMotorDatabase) -> None:
        """Add timezone field with default value"""
        await db.users.update_many(
            {'timezone': {'$exists': False}},
            {'$set': {'timezone': 'UTC'}}
        )
        print(f"Updated {await db.users.count_documents({})} users")
    
    async def down(self, db: AsyncIOMotorDatabase) -> None:
        """Remove timezone field"""
        await db.users.update_many(
            {},
            {'$unset': {'timezone': ''}}
        )
```

**3. Migration Registry**
```python
# /app/backend/migrations/__init__.py

from typing import List, Optional
from migrations.migration_base import Migration

class MigrationRegistry:
    """Registry of all migrations"""
    
    def __init__(self):
        self._migrations: Dict[str, Migration] = {}
    
    def register(self, migration: Migration):
        """Register a migration"""
        self._migrations[migration.version] = migration
    
    def get(self, version: str) -> Optional[Migration]:
        """Get migration by version"""
        return self._migrations.get(version)
    
    def get_pending(self, current_version: str, target_version: str = None) -> List[Migration]:
        """Get migrations between current and target version"""
        all_versions = sorted(self._migrations.keys())
        
        pending = [
            self._migrations[v] 
            for v in all_versions 
            if v > current_version
        ]
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        return pending

# Global registry
migration_registry = MigrationRegistry()

# Import and register all migrations
from migrations.migration_001_add_user_timezone import Migration001
# ... import others

migration_registry.register(Migration001())
```

**4. CLI Tool**
```python
# /app/backend/scripts/migrate.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from migrations import MigrationRunner
from core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client.dhruv_ai
    runner = MigrationRunner(db)
    
    import sys
    command = sys.argv[1] if len(sys.argv) > 1 else 'status'
    
    if command == 'status':
        version = await runner.get_current_version()
        print(f"Current migration version: {version}")
    
    elif command == 'up':
        target = sys.argv[2] if len(sys.argv) > 2 else None
        await runner.run_migrations(target)
    
    elif command == 'down':
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        await runner.rollback(steps)
    
    else:
        print("Usage: python migrate.py [status|up|down] [version|steps]")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

**Usage:**
```bash
# Check current version
python /app/backend/scripts/migrate.py status

# Run all pending migrations
python /app/backend/scripts/migrate.py up

# Run migrations up to version 005
python /app/backend/scripts/migrate.py up 005

# Rollback last migration
python /app/backend/scripts/migrate.py down

# Rollback last 3 migrations
python /app/backend/scripts/migrate.py down 3
```

### Success Criteria
- ✅ Migration history tracked in database
- ✅ Easy to create new migrations
- ✅ Rollback capability
- ✅ Safe execution (transaction-like for critical migrations)
- ✅ CLI tool for easy execution

### Estimated Time: 3-4 hours

---

## TASK 3: Automated Index Creation on Startup 🔴 CRITICAL

### Problem Statement
Database indexes are not created automatically:
- Manual script execution required after deployment
- Risk of performance degradation if indexes missing
- No guarantee indexes exist across environments

### Current State
- Manual script: `/app/backend/scripts/init_indexes.py`
- Must be run manually after deployment
- 63 indexes across 9 collections

### Solution Strategy

**Integrate index creation into application startup**

### Implementation

**1. Index Manager**
```python
# /app/backend/core/indexes.py

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class IndexManager:
    """Manages database indexes with safe creation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_index_safe(self, collection_name: str, keys: List[Tuple], unique: bool = False, name: str = None) -> None:
        """Create index only if it doesn't exist"""
        collection = self.db[collection_name]
        
        # Check if index exists
        existing_indexes = await collection.index_information()
        index_name = name or '_'.join([f"{k}_{v}" for k, v in keys])
        
        if index_name in existing_indexes:
            logger.debug(f"Index {index_name} already exists on {collection_name}")
            return
        
        # Create index
        try:
            await collection.create_index(keys, unique=unique, name=name)
            logger.info(f"✅ Created index {index_name} on {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to create index {index_name}: {e}")
    
    async def ensure_all_indexes(self) -> None:
        """Create all required indexes"""
        logger.info("Ensuring database indexes...")
        
        # Users indexes
        await self.create_index_safe('users', [('user_id', 1)], unique=True)
        await self.create_index_safe('users', [('email', 1)], unique=True)
        await self.create_index_safe('users', [('google_id', 1)])
        await self.create_index_safe('users', [('subscription_type', 1)])
        await self.create_index_safe('users', [('created_at', -1)])
        
        # Chat sessions indexes
        await self.create_index_safe('chat_sessions', [('session_id', 1)], unique=True)
        await self.create_index_safe('chat_sessions', [('user_id', 1)])
        await self.create_index_safe('chat_sessions', [('user_id', 1), ('last_updated', -1)])
        
        # Chat messages indexes
        await self.create_index_safe('chat_messages', [('message_id', 1)], unique=True)
        await self.create_index_safe('chat_messages', [('session_id', 1)])
        await self.create_index_safe('chat_messages', [('user_id', 1)])
        await self.create_index_safe('chat_messages', [('session_id', 1), ('timestamp', -1)])
        
        # Mock tests indexes
        await self.create_index_safe('mock_tests', [('test_id', 1)], unique=True)
        await self.create_index_safe('mock_tests', [('student_id', 1)])
        await self.create_index_safe('mock_tests', [('status', 1)])
        await self.create_index_safe('mock_tests', [('student_id', 1), ('status', 1)])
        await self.create_index_safe('mock_tests', [('student_id', 1), ('generated_at', -1)])
        
        # Test attempts indexes
        await self.create_index_safe('test_attempts', [('attempt_id', 1)], unique=True)
        await self.create_index_safe('test_attempts', [('test_id', 1)])
        await self.create_index_safe('test_attempts', [('student_id', 1)])
        await self.create_index_safe('test_attempts', [('student_id', 1), ('submitted_at', -1)])
        
        # Subscriptions indexes
        await self.create_index_safe('subscriptions', [('subscription_id', 1)], unique=True)
        await self.create_index_safe('subscriptions', [('user_id', 1)])
        await self.create_index_safe('subscriptions', [('status', 1)])
        await self.create_index_safe('subscriptions', [('current_period_end', 1)])
        
        # Usage tracking indexes
        await self.create_index_safe('usage_tracking', [('usage_id', 1)], unique=True)
        await self.create_index_safe('usage_tracking', [('user_id', 1), ('feature_name', 1)])
        await self.create_index_safe('usage_tracking', [('usage_date', 1)])
        
        # Payment transactions indexes
        await self.create_index_safe('payment_transactions', [('transaction_id', 1)], unique=True)
        await self.create_index_safe('payment_transactions', [('user_id', 1)])
        await self.create_index_safe('payment_transactions', [('status', 1)])
        
        logger.info("✅ All database indexes ensured")
```

**2. Integration in main.py**
```python
# /app/backend/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.indexes import IndexManager
from core.database import get_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("Starting Dhruv AI application...")
    
    # Ensure database indexes
    db = await get_database()
    index_manager = IndexManager(db)
    await index_manager.ensure_all_indexes()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dhruv AI application...")

app = FastAPI(lifespan=lifespan, ...)
```

**3. Startup Verification**
```python
# Add to IndexManager
async def verify_indexes(self) -> Dict[str, int]:
    """Verify all indexes are created"""
    collection_names = await self.db.list_collection_names()
    
    index_counts = {}
    for collection_name in collection_names:
        indexes = await self.db[collection_name].index_information()
        index_counts[collection_name] = len(indexes) - 1  # Exclude default _id index
    
    total = sum(index_counts.values())
    logger.info(f"Total indexes across all collections: {total}")
    
    return index_counts
```

### Success Criteria
- ✅ Indexes created automatically on startup
- ✅ Safe existence checks (no duplicate creation errors)
- ✅ Startup logs show index creation
- ✅ No performance impact on startup (<5 seconds)
- ✅ Works across all environments

### Estimated Time: 2-3 hours

---

## IMPLEMENTATION ORDER

### Phase 1: Database Migration System (Day 1, 3-4 hours)
**Why First**: Needed for UUID migration and future schema changes

### Phase 2: Automated Index Creation (Day 1, 2-3 hours)
**Why Second**: Quick win, improves reliability immediately

### Phase 3: UUID Migration (Day 2, 5-8 hours)
**Why Last**: Most complex, requires migration system and testing

---

## TOTAL ESTIMATED TIME: 10-15 hours (2 days)

---

## RISK MITIGATION

### Backups
- Database backup before each migration
- Code backup (git tags)
- Environment variable backup

### Testing
- Test in development first
- Comprehensive backend testing after each task
- Performance benchmarking

### Rollback Plans
- Documented rollback procedures for each task
- Backup collections available
- Git revert strategy

### Monitoring
- Watch error logs during migration
- Monitor performance metrics
- Track API response times

---

## SUCCESS METRICS

### Technical
- ✅ Zero `del doc['_id']` statements
- ✅ Database migration system functional
- ✅ Indexes created automatically on every deployment
- ✅ All tests passing
- ✅ No performance degradation

### Operational
- ✅ Deployments faster (no manual index creation)
- ✅ Schema changes easier (migration system)
- ✅ Better debugging (UUID everywhere)
- ✅ Production-ready database layer

---

**Document Version**: 1.0
**Status**: Ready for Implementation
**Next Action**: Begin with Database Migration System (Phase 1)
