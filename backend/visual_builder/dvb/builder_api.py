"""
Druv Visual Builder - API Endpoints
REST API for the Visual Builder interface
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from .config_generator import ConfigGenerator, VisualConfig
from .copilot_ai import CopilotAI
from ..bal.asset_schema import Asset
from ..vge.grammar_parser import GrammarParser, GrammarDefinition
from ..vge.grammar_validator import GrammarValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/visual-builder", tags=["Visual Builder"])

# Initialize components
config_generator = ConfigGenerator()
copilot_ai = CopilotAI()
grammar_parser = GrammarParser()
grammar_validator = GrammarValidator()


class CreateVisualRequest(BaseModel):
    """Request to create visual"""
    concept: str
    subject: str
    grammar_id: Optional[str] = None
    assets: Dict[str, str]  # Parameter name -> Asset ID
    parameters: Dict[str, Any]  # Parameter values
    cultural_hook: Optional[str] = None
    created_by: str


class CopilotSuggestionRequest(BaseModel):
    """Request for copilot suggestions"""
    concept: str
    subject: str


@router.post("/create", response_model=Dict[str, Any])
async def create_visual(request: CreateVisualRequest) -> Dict[str, Any]:
    """
    Create visual config from builder inputs
    
    Enforces core principles:
    - Value-First: Validates grammar has value proposition
    - Cultural Relatability: Checks assets are culturally relevant
    - Interactive Depth: Validates parameters enable exploration
    """
    try:
        # Load grammar
        if not request.grammar_id:
            raise HTTPException(status_code=400, detail="Grammar ID required")
        
        grammar = grammar_parser.get_grammar(request.grammar_id)
        if not grammar:
            raise HTTPException(status_code=404, detail=f"Grammar {request.grammar_id} not found")
        
        # Validate grammar against core principles
        validation = grammar_validator.validate(grammar)
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Grammar validation failed: {validation['errors']}"
            )
        
        # Generate config
        config = config_generator.generate_config(
            grammar_id=request.grammar_id,
            grammar_version=grammar.version,
            assets=request.assets,
            parameters=request.parameters,
            cultural_hook=request.cultural_hook,
            created_by=request.created_by
        )
        
        # Validate config
        config_validation = config_generator.validate_config(config)
        if not config_validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Config validation failed: {config_validation['errors']}"
            )
        
        return {
            'success': True,
            'config_id': config.config_id,
            'config': config.dict(),
            'validation': config_validation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating visual: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/suggest-grammar", response_model=List[Dict[str, Any]])
async def suggest_grammar(request: CopilotSuggestionRequest) -> List[Dict[str, Any]]:
    """
    Get copilot suggestions for grammar
    
    Only suggests from available grammars (no hallucination)
    """
    try:
        # Get available grammars
        available_grammars = grammar_parser.list_grammars(subject=request.subject)
        grammar_dicts = [
            {
                'grammar_id': g.grammar_id,
                'description': g.description,
                'value_proposition': g.value_proposition
            }
            for g in available_grammars
        ]
        
        # Get suggestions
        suggestions = copilot_ai.suggest_grammar(
            concept=request.concept,
            subject=request.subject,
            available_grammars=grammar_dicts
        )
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting grammar suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/suggest-assets", response_model=List[Dict[str, Any]])
async def suggest_assets(
    grammar_id: str,
    parameter_name: str,
    parameter_tag: str
) -> List[Dict[str, Any]]:
    """
    Get copilot suggestions for assets
    
    Only suggests from BAL (no hallucination)
    """
    try:
        # TODO: Load available assets from BAL
        # For now, return empty list
        available_assets = []
        
        suggestions = copilot_ai.suggest_assets(
            grammar_id=grammar_id,
            parameter_name=parameter_name,
            parameter_tag=parameter_tag,
            available_assets=available_assets
        )
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting asset suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/suggest-hook", response_model=Dict[str, str])
async def suggest_cultural_hook(
    grammar_id: str,
    assets: Dict[str, str],
    concept: str
) -> Dict[str, str]:
    """
    Get copilot suggestion for cultural hook
    
    Returns Hinglish hook text
    """
    try:
        hook = copilot_ai.suggest_cultural_hook(
            grammar_id=grammar_id,
            assets=assets,
            concept=concept
        )
        
        return {'hook': hook or ''}
        
    except Exception as e:
        logger.error(f"Error suggesting cultural hook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{config_id}", response_model=Dict[str, Any])
async def get_config(config_id: str) -> Dict[str, Any]:
    """Get visual config by ID"""
    config = config_generator.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    return config.dict()


@router.get("/grammars", response_model=List[Dict[str, Any]])
async def list_grammars(subject: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available grammars"""
    grammars = grammar_parser.list_grammars(subject=subject)
    return [
        {
            'grammar_id': g.grammar_id,
            'name': g.name,
            'description': g.description,
            'subject': g.subject,
            'value_proposition': g.value_proposition
        }
        for g in grammars
    ]









