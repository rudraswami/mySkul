# Architecture Cleanup & Modularization Plan
**Current Status**: server.py (11,410 lines) is active entry point
**Target**: Consolidate to main.py (modular architecture)

---

## Current Situation Analysis

### server.py (11,410 lines)
- ✅ **Active entry point** (configured in supervisor)
- ❌ **Monolithic structure** - all routes inline
- ❌ **Hard to maintain** - finding specific endpoints difficult
- ❌ **Code duplication** - likely has redundant logic
- ❌ **Testing challenges** - difficult to isolate components
- ✅ **Production-tested** - all current functionality works

### main.py (158 lines)
- ✅ **Modular architecture** - imports from api/ routers
- ✅ **Clean structure** - follows FastAPI best practices
- ✅ **Maintainable** - organized by feature domain
- ✅ **CSRF enabled** - enhanced security
- ❌ **Not active** - not used in production
- ⚠️  **Incomplete** - missing some server.py functionality

---

## Migration Strategy

### Option 1: Gradual Migration (Recommended)
**Duration**: 8-10 hours
**Risk**: Low
**Approach**: Incremental feature-by-feature migration

#### Steps:
1. **Audit** (1-2 hours)
   - Compare server.py vs main.py endpoints
   - Identify unique endpoints in server.py
   - Document missing functionality

2. **Create Missing Routers** (3-4 hours)
   - Extract inline routes from server.py
   - Create modular routers in api/
   - Add missing services to services/

3. **Testing Phase** (2-3 hours)
   - Test each migrated endpoint
   - Verify main.py handles all requests
   - Run comprehensive backend tests

4. **Cutover** (1 hour)
   - Update supervisor config
   - Switch to main.py
   - Monitor for issues
   - Keep server.py as backup

5. **Cleanup** (1 hour)
   - Remove server.py
   - Update documentation
   - Archive old code

### Option 2: Full Rewrite
**Duration**: 15-20 hours
**Risk**: High
**Not Recommended**: Too risky for production system

### Option 3: Keep Both (Current State)
**Duration**: 0 hours
**Risk**: Technical debt accumulation
**Drawback**: Confusion about which is authoritative

---

## Detailed Migration Checklist

### Phase 1: Audit & Documentation
- [ ] Export all routes from server.py (`grep -E "^@app\.(get|post|put|delete)" server.py`)
- [ ] Export all routes from main.py
- [ ] Create diff report
- [ ] Document missing endpoints
- [ ] Identify deprecated endpoints

### Phase 2: Router Creation
- [ ] Create `api/mock_tests.py` if missing
- [ ] Create `api/auto_notes.py` if missing
- [ ] Create `api/analytics.py` if missing
- [ ] Extract dashboard routes
- [ ] Extract chat routes
- [ ] Extract user profile routes
- [ ] Extract actions routes (practice, notes, flashcards)
- [ ] Extract guardrails routes
- [ ] Extract wellness routes

### Phase 3: Service Layer
- [ ] Extract business logic from inline routes
- [ ] Create service classes
- [ ] Add proper error handling
- [ ] Add logging
- [ ] Add type hints

### Phase 4: Testing
- [ ] Test all auth endpoints
- [ ] Test all subscription endpoints
- [ ] Test all AI endpoints
- [ ] Test all mock test endpoints
- [ ] Test all auto-notes endpoints
- [ ] Test all analytics endpoints
- [ ] Run integration tests

### Phase 5: Deployment
- [ ] Update supervisor config to use main.py
- [ ] Restart backend service
- [ ] Monitor logs for errors
- [ ] Run smoke tests
- [ ] Verify all features working

### Phase 6: Cleanup
- [ ] Archive server.py
- [ ] Update documentation
- [ ] Remove duplicate code
- [ ] Update README

---

## Code Standards for Modular Architecture

### Directory Structure
```
backend/
├── main.py                 # Entry point
├── dependencies.py         # Shared dependencies
├── api/                    # Route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── subscription.py
│   ├── ai.py
│   ├── mock_tests.py
│   ├── auto_notes.py
│   ├── analytics.py
│   └── actions.py
├── services/               # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── subscription_service.py
│   ├── ai_service.py
│   ├── mock_test_service.py
│   └── auto_notes_service.py
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── subscription.py
│   ├── ai.py
│   └── mock_tests.py
└── utils/                  # Helper functions
    ├── __init__.py
    ├── validators.py
    ├── formatters.py
    └── helpers.py
```

### Router Template
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from models.feature import FeatureRequest, FeatureResponse
from services.feature_service import FeatureService
from dependencies import get_current_user, get_feature_service

router = APIRouter(
    prefix="/feature",
    tags=["feature"]
)

@router.get("/items", response_model=List[FeatureResponse])
async def get_items(
    user = Depends(get_current_user),
    service: FeatureService = Depends(get_feature_service)
):
    """
    Get all items for current user
    
    Args:
        user: Authenticated user
        service: Feature service instance
        
    Returns:
        List of feature items
        
    Raises:
        HTTPException: If items cannot be retrieved
    """
    try:
        items = await service.get_items(user.user_id)
        return items
    except Exception as e:
        logger.error(f"Get items error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Service Template
```python
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.feature import Feature
import logging

logger = logging.getLogger(__name__)

class FeatureService:
    """Service for feature business logic"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.features
    
    async def get_items(self, user_id: str) -> List[Feature]:
        """
        Get all items for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of features
            
        Raises:
            Exception: If database query fails
        """
        try:
            items = await self.collection.find(
                {"user_id": user_id}
            ).to_list(length=None)
            
            return [Feature(**item) for item in items]
        except Exception as e:
            logger.error(f"Get items error for user {user_id}: {str(e)}")
            raise
```

### PEP 8 Standards
- **Line length**: Max 100 characters
- **Imports**: Standard library, third-party, local (grouped & sorted)
- **Naming**: 
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Docstrings**: Google style for all public functions
- **Type hints**: Required for all function signatures
- **Comments**: Explain "why", not "what"

---

## Risk Assessment

### High Risk Areas
1. **Authentication/Authorization** - Critical for security
2. **Subscription Logic** - Affects monetization
3. **AI Response Generation** - Core product feature
4. **Database Operations** - Data integrity

### Mitigation Strategies
1. **Comprehensive Testing** before cutover
2. **Backup server.py** for quick rollback
3. **Staged Rollout** - migrate non-critical endpoints first
4. **Monitoring** - watch logs during migration
5. **Rollback Plan** - documented steps to revert

---

## Success Criteria

### Must Have
- [ ] All existing endpoints functional
- [ ] No breaking changes to API
- [ ] All tests passing
- [ ] Response times similar to server.py
- [ ] Zero downtime migration

### Nice to Have
- [ ] Improved response times
- [ ] Better error messages
- [ ] Enhanced logging
- [ ] API documentation (Swagger)
- [ ] Performance metrics

---

## Timeline

### Recommended Schedule
- **Week 1**: Audit & documentation
- **Week 2-3**: Router & service creation
- **Week 4**: Testing & validation
- **Week 5**: Staged deployment
- **Week 6**: Monitoring & optimization

### Fast Track (If Urgent)
- **Days 1-2**: Critical endpoint migration
- **Days 3-4**: Testing
- **Day 5**: Deployment
- **Risk**: Higher chance of issues

---

## Decision Recommendation

**Recommended**: **Option 1 - Gradual Migration**

**Reasoning**:
1. Server.py is production-stable
2. main.py architecture is superior
3. Gradual migration minimizes risk
4. Can test incrementally
5. Easy rollback if issues arise

**When to Execute**:
- After critical features are stable
- When dedicated time available
- With full testing capability
- Not during peak usage period

---

## Immediate Actions (Today)

1. ✅ **Document current state** (this file)
2. ⏳ **Create audit script** to compare endpoints
3. ⏳ **Export route inventory** from both files
4. ⏳ **Identify must-migrate endpoints**
5. ⏳ **Schedule migration window**

---

## Long-term Vision

### Target Architecture (Post-Migration)
```
- Single entry point (main.py)
- 8-10 modular routers
- 5-7 service classes
- Comprehensive test coverage
- API documentation
- Performance monitoring
- Structured logging
- Type safety throughout
- Clear separation of concerns
```

### Benefits
- **Maintainability**: Easy to find and fix code
- **Scalability**: Add features without bloat
- **Testing**: Isolated unit tests
- **Collaboration**: Multiple devs can work in parallel
- **Documentation**: Auto-generated API docs
- **Performance**: Easier to optimize specific areas

---

## Conclusion

While server.py works, migrating to main.py's modular architecture is essential for long-term success. The recommended gradual migration approach balances risk and reward, allowing us to improve the codebase without disrupting production.

**Next Step**: Schedule dedicated time for migration with full testing support.
