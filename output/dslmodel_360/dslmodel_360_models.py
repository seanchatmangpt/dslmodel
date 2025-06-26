"""
DSLModel 360 Permutations
Auto-generated Python models for all DSLModel permutations
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dslmodel.mixins import JinjaMixin, ToolMixin, FileMixin, FSMMixin

# Base model types

@dataclass
class BaseNonePromptModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: prompt
    """
    name: str = Field(default="base_none_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseNoneSchemaModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: schema
    """
    name: str = Field(default="base_none_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseNoneApiModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: api
    """
    name: str = Field(default="base_none_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseNoneTemplateModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: template
    """
    name: str = Field(default="base_none_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseNoneWeaverModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: weaver
    """
    name: str = Field(default="base_none_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseNoneManualModel(BaseModel):
    """
    DSLModel Permutation: base with none mixins
    Generated from: manual
    """
    name: str = Field(default="base_none_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="base_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="base_jinja_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: api
    """
    name: str = Field(default="base_jinja_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: template
    """
    name: str = Field(default="base_jinja_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="base_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="base_jinja_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="base_tool_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: schema
    """
    name: str = Field(default="base_tool_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: api
    """
    name: str = Field(default="base_tool_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: template
    """
    name: str = Field(default="base_tool_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="base_tool_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with tool mixins
    Generated from: manual
    """
    name: str = Field(default="base_tool_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFilePromptModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: prompt
    """
    name: str = Field(default="base_file_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFileSchemaModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: schema
    """
    name: str = Field(default="base_file_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFileApiModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: api
    """
    name: str = Field(default="base_file_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFileTemplateModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: template
    """
    name: str = Field(default="base_file_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFileWeaverModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: weaver
    """
    name: str = Field(default="base_file_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFileManualModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: base with file mixins
    Generated from: manual
    """
    name: str = Field(default="base_file_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolPromptModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="base_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolSchemaModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="base_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolApiModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="base_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolTemplateModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="base_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolWeaverModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="base_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaToolManualModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: base with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="base_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFilePromptModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="base_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFileSchemaModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="base_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFileApiModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="base_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFileTemplateModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="base_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFileWeaverModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="base_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseJinjaFileManualModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: base with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="base_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFilePromptModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="base_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFileSchemaModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="base_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFileApiModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="base_tool_file_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFileTemplateModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="base_tool_file_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFileWeaverModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="base_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseToolFileManualModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: base with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="base_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllPromptModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: prompt
    """
    name: str = Field(default="base_all_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllSchemaModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: schema
    """
    name: str = Field(default="base_all_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllApiModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: api
    """
    name: str = Field(default="base_all_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllTemplateModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: template
    """
    name: str = Field(default="base_all_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllWeaverModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: weaver
    """
    name: str = Field(default="base_all_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseAllManualModel(BaseModel):
    """
    DSLModel Permutation: base with all mixins
    Generated from: manual
    """
    name: str = Field(default="base_all_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="base_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="base_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="base_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="base_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="base_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: base with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="base_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="base_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="base_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="base_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="base_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="base_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class BaseFsmToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: base with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="base_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="base", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNonePromptModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_none_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNoneSchemaModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_none_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNoneApiModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: api
    """
    name: str = Field(default="fsm_none_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNoneTemplateModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: template
    """
    name: str = Field(default="fsm_none_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNoneWeaverModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_none_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmNoneManualModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with none mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_none_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaPromptModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaSchemaModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaApiModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: api
    """
    name: str = Field(default="fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaTemplateModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: template
    """
    name: str = Field(default="fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaWeaverModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaManualModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolPromptModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolSchemaModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolApiModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: api
    """
    name: str = Field(default="fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolTemplateModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: template
    """
    name: str = Field(default="fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolWeaverModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolManualModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with tool mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFilePromptModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_file_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFileSchemaModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_file_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFileApiModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: api
    """
    name: str = Field(default="fsm_file_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFileTemplateModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: template
    """
    name: str = Field(default="fsm_file_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFileWeaverModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_file_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFileManualModel(BaseModel, FSMMixin, FileMixin):
    """
    DSLModel Permutation: fsm with file mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_file_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolPromptModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolSchemaModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolApiModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="fsm_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolTemplateModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="fsm_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolWeaverModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaToolManualModel(BaseModel, FSMMixin, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFilePromptModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFileSchemaModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFileApiModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="fsm_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFileTemplateModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="fsm_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFileWeaverModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmJinjaFileManualModel(BaseModel, FSMMixin, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: fsm with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFilePromptModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFileSchemaModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFileApiModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="fsm_tool_file_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFileTemplateModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="fsm_tool_file_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFileWeaverModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmToolFileManualModel(BaseModel, FSMMixin, ToolMixin, FileMixin):
    """
    DSLModel Permutation: fsm with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllPromptModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_all_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllSchemaModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_all_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllApiModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: api
    """
    name: str = Field(default="fsm_all_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllTemplateModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: template
    """
    name: str = Field(default="fsm_all_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllWeaverModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_all_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmAllManualModel(BaseModel, FSMMixin):
    """
    DSLModel Permutation: fsm with all mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_all_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaPromptModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaSchemaModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaApiModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="fsm_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaTemplateModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="fsm_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaWeaverModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmJinjaManualModel(BaseModel, FSMMixin, JinjaMixin):
    """
    DSLModel Permutation: fsm with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolPromptModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="fsm_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolSchemaModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="fsm_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolApiModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="fsm_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolTemplateModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="fsm_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolWeaverModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="fsm_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class FsmFsmToolManualModel(BaseModel, FSMMixin, ToolMixin):
    """
    DSLModel Permutation: fsm with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="fsm_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="fsm", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNonePromptModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_none_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNoneSchemaModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_none_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNoneApiModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: api
    """
    name: str = Field(default="workflow_none_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNoneTemplateModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: template
    """
    name: str = Field(default="workflow_none_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNoneWeaverModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_none_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowNoneManualModel(BaseModel):
    """
    DSLModel Permutation: workflow with none mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_none_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_jinja_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: api
    """
    name: str = Field(default="workflow_jinja_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: template
    """
    name: str = Field(default="workflow_jinja_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_jinja_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_tool_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_tool_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: api
    """
    name: str = Field(default="workflow_tool_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: template
    """
    name: str = Field(default="workflow_tool_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_tool_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with tool mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_tool_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFilePromptModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_file_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFileSchemaModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_file_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFileApiModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: api
    """
    name: str = Field(default="workflow_file_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFileTemplateModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: template
    """
    name: str = Field(default="workflow_file_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFileWeaverModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_file_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFileManualModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: workflow with file mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_file_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolPromptModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolSchemaModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolApiModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="workflow_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolTemplateModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="workflow_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolWeaverModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaToolManualModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: workflow with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFilePromptModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFileSchemaModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFileApiModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="workflow_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFileTemplateModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="workflow_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFileWeaverModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowJinjaFileManualModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: workflow with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFilePromptModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFileSchemaModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFileApiModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="workflow_tool_file_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFileTemplateModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="workflow_tool_file_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFileWeaverModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowToolFileManualModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: workflow with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllPromptModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_all_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllSchemaModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_all_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllApiModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: api
    """
    name: str = Field(default="workflow_all_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllTemplateModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: template
    """
    name: str = Field(default="workflow_all_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllWeaverModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_all_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowAllManualModel(BaseModel):
    """
    DSLModel Permutation: workflow with all mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_all_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="workflow_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="workflow_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: workflow with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="workflow_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="workflow_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="workflow_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="workflow_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="workflow_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class WorkflowFsmToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: workflow with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="workflow_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="workflow", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNonePromptModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_none_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNoneSchemaModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: schema
    """
    name: str = Field(default="agent_none_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNoneApiModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: api
    """
    name: str = Field(default="agent_none_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNoneTemplateModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: template
    """
    name: str = Field(default="agent_none_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNoneWeaverModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_none_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentNoneManualModel(BaseModel):
    """
    DSLModel Permutation: agent with none mixins
    Generated from: manual
    """
    name: str = Field(default="agent_none_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="agent_jinja_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: api
    """
    name: str = Field(default="agent_jinja_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: template
    """
    name: str = Field(default="agent_jinja_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="agent_jinja_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_tool_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: schema
    """
    name: str = Field(default="agent_tool_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: api
    """
    name: str = Field(default="agent_tool_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: template
    """
    name: str = Field(default="agent_tool_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_tool_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with tool mixins
    Generated from: manual
    """
    name: str = Field(default="agent_tool_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFilePromptModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_file_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFileSchemaModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: schema
    """
    name: str = Field(default="agent_file_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFileApiModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: api
    """
    name: str = Field(default="agent_file_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFileTemplateModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: template
    """
    name: str = Field(default="agent_file_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFileWeaverModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_file_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFileManualModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: agent with file mixins
    Generated from: manual
    """
    name: str = Field(default="agent_file_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolPromptModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolSchemaModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="agent_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolApiModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="agent_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolTemplateModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="agent_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolWeaverModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaToolManualModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: agent with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="agent_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFilePromptModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFileSchemaModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="agent_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFileApiModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="agent_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFileTemplateModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="agent_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFileWeaverModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentJinjaFileManualModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: agent with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="agent_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFilePromptModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFileSchemaModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="agent_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFileApiModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="agent_tool_file_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFileTemplateModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="agent_tool_file_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFileWeaverModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentToolFileManualModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: agent with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="agent_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllPromptModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_all_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllSchemaModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: schema
    """
    name: str = Field(default="agent_all_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllApiModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: api
    """
    name: str = Field(default="agent_all_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllTemplateModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: template
    """
    name: str = Field(default="agent_all_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllWeaverModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_all_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentAllManualModel(BaseModel):
    """
    DSLModel Permutation: agent with all mixins
    Generated from: manual
    """
    name: str = Field(default="agent_all_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="agent_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="agent_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="agent_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: agent with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="agent_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="agent_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="agent_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="agent_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="agent_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="agent_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class AgentFsmToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: agent with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="agent_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="agent", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNonePromptModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: prompt
    """
    name: str = Field(default="event_none_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNoneSchemaModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: schema
    """
    name: str = Field(default="event_none_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNoneApiModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: api
    """
    name: str = Field(default="event_none_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNoneTemplateModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: template
    """
    name: str = Field(default="event_none_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNoneWeaverModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: weaver
    """
    name: str = Field(default="event_none_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventNoneManualModel(BaseModel):
    """
    DSLModel Permutation: event with none mixins
    Generated from: manual
    """
    name: str = Field(default="event_none_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="event_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="event_jinja_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: api
    """
    name: str = Field(default="event_jinja_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: template
    """
    name: str = Field(default="event_jinja_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="event_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="event_jinja_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="event_tool_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: schema
    """
    name: str = Field(default="event_tool_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: api
    """
    name: str = Field(default="event_tool_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: template
    """
    name: str = Field(default="event_tool_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="event_tool_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with tool mixins
    Generated from: manual
    """
    name: str = Field(default="event_tool_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFilePromptModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: prompt
    """
    name: str = Field(default="event_file_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFileSchemaModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: schema
    """
    name: str = Field(default="event_file_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFileApiModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: api
    """
    name: str = Field(default="event_file_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFileTemplateModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: template
    """
    name: str = Field(default="event_file_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFileWeaverModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: weaver
    """
    name: str = Field(default="event_file_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFileManualModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: event with file mixins
    Generated from: manual
    """
    name: str = Field(default="event_file_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolPromptModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="event_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolSchemaModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="event_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolApiModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="event_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolTemplateModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="event_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolWeaverModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="event_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaToolManualModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: event with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="event_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFilePromptModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="event_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFileSchemaModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="event_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFileApiModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="event_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFileTemplateModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="event_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFileWeaverModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="event_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventJinjaFileManualModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: event with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="event_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFilePromptModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="event_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFileSchemaModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="event_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFileApiModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="event_tool_file_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFileTemplateModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="event_tool_file_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFileWeaverModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="event_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventToolFileManualModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: event with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="event_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllPromptModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: prompt
    """
    name: str = Field(default="event_all_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllSchemaModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: schema
    """
    name: str = Field(default="event_all_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllApiModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: api
    """
    name: str = Field(default="event_all_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllTemplateModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: template
    """
    name: str = Field(default="event_all_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllWeaverModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: weaver
    """
    name: str = Field(default="event_all_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventAllManualModel(BaseModel):
    """
    DSLModel Permutation: event with all mixins
    Generated from: manual
    """
    name: str = Field(default="event_all_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="event_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="event_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="event_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="event_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="event_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: event with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="event_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="event_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="event_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="event_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="event_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="event_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class EventFsmToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: event with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="event_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="event", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNonePromptModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: prompt
    """
    name: str = Field(default="template_none_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNoneSchemaModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: schema
    """
    name: str = Field(default="template_none_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNoneApiModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: api
    """
    name: str = Field(default="template_none_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNoneTemplateModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: template
    """
    name: str = Field(default="template_none_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNoneWeaverModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: weaver
    """
    name: str = Field(default="template_none_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateNoneManualModel(BaseModel):
    """
    DSLModel Permutation: template with none mixins
    Generated from: manual
    """
    name: str = Field(default="template_none_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="none", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="template_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: schema
    """
    name: str = Field(default="template_jinja_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: api
    """
    name: str = Field(default="template_jinja_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: template
    """
    name: str = Field(default="template_jinja_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="template_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with jinja mixins
    Generated from: manual
    """
    name: str = Field(default="template_jinja_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: prompt
    """
    name: str = Field(default="template_tool_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: schema
    """
    name: str = Field(default="template_tool_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: api
    """
    name: str = Field(default="template_tool_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: template
    """
    name: str = Field(default="template_tool_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: weaver
    """
    name: str = Field(default="template_tool_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with tool mixins
    Generated from: manual
    """
    name: str = Field(default="template_tool_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFilePromptModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: prompt
    """
    name: str = Field(default="template_file_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFileSchemaModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: schema
    """
    name: str = Field(default="template_file_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFileApiModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: api
    """
    name: str = Field(default="template_file_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFileTemplateModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: template
    """
    name: str = Field(default="template_file_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFileWeaverModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: weaver
    """
    name: str = Field(default="template_file_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFileManualModel(BaseModel, FileMixin):
    """
    DSLModel Permutation: template with file mixins
    Generated from: manual
    """
    name: str = Field(default="template_file_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolPromptModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="template_jinja_tool_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolSchemaModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: schema
    """
    name: str = Field(default="template_jinja_tool_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolApiModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: api
    """
    name: str = Field(default="template_jinja_tool_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolTemplateModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: template
    """
    name: str = Field(default="template_jinja_tool_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolWeaverModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="template_jinja_tool_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaToolManualModel(BaseModel, JinjaMixin, ToolMixin):
    """
    DSLModel Permutation: template with jinja_tool mixins
    Generated from: manual
    """
    name: str = Field(default="template_jinja_tool_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFilePromptModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: prompt
    """
    name: str = Field(default="template_jinja_file_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFileSchemaModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: schema
    """
    name: str = Field(default="template_jinja_file_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFileApiModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: api
    """
    name: str = Field(default="template_jinja_file_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFileTemplateModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: template
    """
    name: str = Field(default="template_jinja_file_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFileWeaverModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: weaver
    """
    name: str = Field(default="template_jinja_file_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateJinjaFileManualModel(BaseModel, JinjaMixin, FileMixin):
    """
    DSLModel Permutation: template with jinja_file mixins
    Generated from: manual
    """
    name: str = Field(default="template_jinja_file_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="jinja_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFilePromptModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: prompt
    """
    name: str = Field(default="template_tool_file_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFileSchemaModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: schema
    """
    name: str = Field(default="template_tool_file_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFileApiModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: api
    """
    name: str = Field(default="template_tool_file_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFileTemplateModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: template
    """
    name: str = Field(default="template_tool_file_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFileWeaverModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: weaver
    """
    name: str = Field(default="template_tool_file_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateToolFileManualModel(BaseModel, ToolMixin, FileMixin):
    """
    DSLModel Permutation: template with tool_file mixins
    Generated from: manual
    """
    name: str = Field(default="template_tool_file_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="tool_file", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllPromptModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: prompt
    """
    name: str = Field(default="template_all_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllSchemaModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: schema
    """
    name: str = Field(default="template_all_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllApiModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: api
    """
    name: str = Field(default="template_all_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllTemplateModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: template
    """
    name: str = Field(default="template_all_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllWeaverModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: weaver
    """
    name: str = Field(default="template_all_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateAllManualModel(BaseModel):
    """
    DSLModel Permutation: template with all mixins
    Generated from: manual
    """
    name: str = Field(default="template_all_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="all", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaPromptModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: prompt
    """
    name: str = Field(default="template_fsm_jinja_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaSchemaModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: schema
    """
    name: str = Field(default="template_fsm_jinja_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaApiModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: api
    """
    name: str = Field(default="template_fsm_jinja_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaTemplateModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: template
    """
    name: str = Field(default="template_fsm_jinja_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaWeaverModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: weaver
    """
    name: str = Field(default="template_fsm_jinja_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmJinjaManualModel(BaseModel, JinjaMixin):
    """
    DSLModel Permutation: template with fsm_jinja mixins
    Generated from: manual
    """
    name: str = Field(default="template_fsm_jinja_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_jinja", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolPromptModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: prompt
    """
    name: str = Field(default="template_fsm_tool_prompt", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="prompt", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolSchemaModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: schema
    """
    name: str = Field(default="template_fsm_tool_schema", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="schema", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolApiModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: api
    """
    name: str = Field(default="template_fsm_tool_api", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="api", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolTemplateModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: template
    """
    name: str = Field(default="template_fsm_tool_template", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="template", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolWeaverModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: weaver
    """
    name: str = Field(default="template_fsm_tool_weaver", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="weaver", description="Generation source")
    
    class Config:
        extra = "allow"

@dataclass
class TemplateFsmToolManualModel(BaseModel, ToolMixin):
    """
    DSLModel Permutation: template with fsm_tool mixins
    Generated from: manual
    """
    name: str = Field(default="template_fsm_tool_manual", description="Permutation name")
    model_type: str = Field(default="template", description="Model type")
    mixin_combo: str = Field(default="fsm_tool", description="Mixin combination")
    generation_source: str = Field(default="manual", description="Generation source")
    
    class Config:
        extra = "allow"


def create_dslmodel_permutation(
    model_type: str,
    mixin_combo: str, 
    generation_source: str,
    **kwargs
) -> BaseModel:
    """Factory function to create DSLModel permutation instances"""
    class_name = f"{model_type.title()}{mixin_combo.title().replace('_', '')}{generation_source.title()}Model"
    model_class = globals().get(class_name)
    
    if not model_class:
        raise ValueError(f"Unknown permutation: {model_type}_{mixin_combo}_{generation_source}")
    
    return model_class(**kwargs)

# Permutation registry
PERMUTATION_REGISTRY = {
    "base_none_prompt": BaseNonePromptModel,
    "base_none_schema": BaseNoneSchemaModel,
    "base_none_api": BaseNoneApiModel,
    "base_none_template": BaseNoneTemplateModel,
    "base_none_weaver": BaseNoneWeaverModel,
    "base_none_manual": BaseNoneManualModel,
    "base_jinja_prompt": BaseJinjaPromptModel,
    "base_jinja_schema": BaseJinjaSchemaModel,
    "base_jinja_api": BaseJinjaApiModel,
    "base_jinja_template": BaseJinjaTemplateModel,
    "base_jinja_weaver": BaseJinjaWeaverModel,
    "base_jinja_manual": BaseJinjaManualModel,
    "base_tool_prompt": BaseToolPromptModel,
    "base_tool_schema": BaseToolSchemaModel,
    "base_tool_api": BaseToolApiModel,
    "base_tool_template": BaseToolTemplateModel,
    "base_tool_weaver": BaseToolWeaverModel,
    "base_tool_manual": BaseToolManualModel,
    "base_file_prompt": BaseFilePromptModel,
    "base_file_schema": BaseFileSchemaModel,
    "base_file_api": BaseFileApiModel,
    "base_file_template": BaseFileTemplateModel,
    "base_file_weaver": BaseFileWeaverModel,
    "base_file_manual": BaseFileManualModel,
    "base_jinja_tool_prompt": BaseJinjaToolPromptModel,
    "base_jinja_tool_schema": BaseJinjaToolSchemaModel,
    "base_jinja_tool_api": BaseJinjaToolApiModel,
    "base_jinja_tool_template": BaseJinjaToolTemplateModel,
    "base_jinja_tool_weaver": BaseJinjaToolWeaverModel,
    "base_jinja_tool_manual": BaseJinjaToolManualModel,
    "base_jinja_file_prompt": BaseJinjaFilePromptModel,
    "base_jinja_file_schema": BaseJinjaFileSchemaModel,
    "base_jinja_file_api": BaseJinjaFileApiModel,
    "base_jinja_file_template": BaseJinjaFileTemplateModel,
    "base_jinja_file_weaver": BaseJinjaFileWeaverModel,
    "base_jinja_file_manual": BaseJinjaFileManualModel,
    "base_tool_file_prompt": BaseToolFilePromptModel,
    "base_tool_file_schema": BaseToolFileSchemaModel,
    "base_tool_file_api": BaseToolFileApiModel,
    "base_tool_file_template": BaseToolFileTemplateModel,
    "base_tool_file_weaver": BaseToolFileWeaverModel,
    "base_tool_file_manual": BaseToolFileManualModel,
    "base_all_prompt": BaseAllPromptModel,
    "base_all_schema": BaseAllSchemaModel,
    "base_all_api": BaseAllApiModel,
    "base_all_template": BaseAllTemplateModel,
    "base_all_weaver": BaseAllWeaverModel,
    "base_all_manual": BaseAllManualModel,
    "base_fsm_jinja_prompt": BaseFsmJinjaPromptModel,
    "base_fsm_jinja_schema": BaseFsmJinjaSchemaModel,
    "base_fsm_jinja_api": BaseFsmJinjaApiModel,
    "base_fsm_jinja_template": BaseFsmJinjaTemplateModel,
    "base_fsm_jinja_weaver": BaseFsmJinjaWeaverModel,
    "base_fsm_jinja_manual": BaseFsmJinjaManualModel,
    "base_fsm_tool_prompt": BaseFsmToolPromptModel,
    "base_fsm_tool_schema": BaseFsmToolSchemaModel,
    "base_fsm_tool_api": BaseFsmToolApiModel,
    "base_fsm_tool_template": BaseFsmToolTemplateModel,
    "base_fsm_tool_weaver": BaseFsmToolWeaverModel,
    "base_fsm_tool_manual": BaseFsmToolManualModel,
    "fsm_none_prompt": FsmNonePromptModel,
    "fsm_none_schema": FsmNoneSchemaModel,
    "fsm_none_api": FsmNoneApiModel,
    "fsm_none_template": FsmNoneTemplateModel,
    "fsm_none_weaver": FsmNoneWeaverModel,
    "fsm_none_manual": FsmNoneManualModel,
    "fsm_jinja_prompt": FsmJinjaPromptModel,
    "fsm_jinja_schema": FsmJinjaSchemaModel,
    "fsm_jinja_api": FsmJinjaApiModel,
    "fsm_jinja_template": FsmJinjaTemplateModel,
    "fsm_jinja_weaver": FsmJinjaWeaverModel,
    "fsm_jinja_manual": FsmJinjaManualModel,
    "fsm_tool_prompt": FsmToolPromptModel,
    "fsm_tool_schema": FsmToolSchemaModel,
    "fsm_tool_api": FsmToolApiModel,
    "fsm_tool_template": FsmToolTemplateModel,
    "fsm_tool_weaver": FsmToolWeaverModel,
    "fsm_tool_manual": FsmToolManualModel,
    "fsm_file_prompt": FsmFilePromptModel,
    "fsm_file_schema": FsmFileSchemaModel,
    "fsm_file_api": FsmFileApiModel,
    "fsm_file_template": FsmFileTemplateModel,
    "fsm_file_weaver": FsmFileWeaverModel,
    "fsm_file_manual": FsmFileManualModel,
    "fsm_jinja_tool_prompt": FsmJinjaToolPromptModel,
    "fsm_jinja_tool_schema": FsmJinjaToolSchemaModel,
    "fsm_jinja_tool_api": FsmJinjaToolApiModel,
    "fsm_jinja_tool_template": FsmJinjaToolTemplateModel,
    "fsm_jinja_tool_weaver": FsmJinjaToolWeaverModel,
    "fsm_jinja_tool_manual": FsmJinjaToolManualModel,
    "fsm_jinja_file_prompt": FsmJinjaFilePromptModel,
    "fsm_jinja_file_schema": FsmJinjaFileSchemaModel,
    "fsm_jinja_file_api": FsmJinjaFileApiModel,
    "fsm_jinja_file_template": FsmJinjaFileTemplateModel,
    "fsm_jinja_file_weaver": FsmJinjaFileWeaverModel,
    "fsm_jinja_file_manual": FsmJinjaFileManualModel,
    "fsm_tool_file_prompt": FsmToolFilePromptModel,
    "fsm_tool_file_schema": FsmToolFileSchemaModel,
    "fsm_tool_file_api": FsmToolFileApiModel,
    "fsm_tool_file_template": FsmToolFileTemplateModel,
    "fsm_tool_file_weaver": FsmToolFileWeaverModel,
    "fsm_tool_file_manual": FsmToolFileManualModel,
    "fsm_all_prompt": FsmAllPromptModel,
    "fsm_all_schema": FsmAllSchemaModel,
    "fsm_all_api": FsmAllApiModel,
    "fsm_all_template": FsmAllTemplateModel,
    "fsm_all_weaver": FsmAllWeaverModel,
    "fsm_all_manual": FsmAllManualModel,
    "fsm_fsm_jinja_prompt": FsmFsmJinjaPromptModel,
    "fsm_fsm_jinja_schema": FsmFsmJinjaSchemaModel,
    "fsm_fsm_jinja_api": FsmFsmJinjaApiModel,
    "fsm_fsm_jinja_template": FsmFsmJinjaTemplateModel,
    "fsm_fsm_jinja_weaver": FsmFsmJinjaWeaverModel,
    "fsm_fsm_jinja_manual": FsmFsmJinjaManualModel,
    "fsm_fsm_tool_prompt": FsmFsmToolPromptModel,
    "fsm_fsm_tool_schema": FsmFsmToolSchemaModel,
    "fsm_fsm_tool_api": FsmFsmToolApiModel,
    "fsm_fsm_tool_template": FsmFsmToolTemplateModel,
    "fsm_fsm_tool_weaver": FsmFsmToolWeaverModel,
    "fsm_fsm_tool_manual": FsmFsmToolManualModel,
    "workflow_none_prompt": WorkflowNonePromptModel,
    "workflow_none_schema": WorkflowNoneSchemaModel,
    "workflow_none_api": WorkflowNoneApiModel,
    "workflow_none_template": WorkflowNoneTemplateModel,
    "workflow_none_weaver": WorkflowNoneWeaverModel,
    "workflow_none_manual": WorkflowNoneManualModel,
    "workflow_jinja_prompt": WorkflowJinjaPromptModel,
    "workflow_jinja_schema": WorkflowJinjaSchemaModel,
    "workflow_jinja_api": WorkflowJinjaApiModel,
    "workflow_jinja_template": WorkflowJinjaTemplateModel,
    "workflow_jinja_weaver": WorkflowJinjaWeaverModel,
    "workflow_jinja_manual": WorkflowJinjaManualModel,
    "workflow_tool_prompt": WorkflowToolPromptModel,
    "workflow_tool_schema": WorkflowToolSchemaModel,
    "workflow_tool_api": WorkflowToolApiModel,
    "workflow_tool_template": WorkflowToolTemplateModel,
    "workflow_tool_weaver": WorkflowToolWeaverModel,
    "workflow_tool_manual": WorkflowToolManualModel,
    "workflow_file_prompt": WorkflowFilePromptModel,
    "workflow_file_schema": WorkflowFileSchemaModel,
    "workflow_file_api": WorkflowFileApiModel,
    "workflow_file_template": WorkflowFileTemplateModel,
    "workflow_file_weaver": WorkflowFileWeaverModel,
    "workflow_file_manual": WorkflowFileManualModel,
    "workflow_jinja_tool_prompt": WorkflowJinjaToolPromptModel,
    "workflow_jinja_tool_schema": WorkflowJinjaToolSchemaModel,
    "workflow_jinja_tool_api": WorkflowJinjaToolApiModel,
    "workflow_jinja_tool_template": WorkflowJinjaToolTemplateModel,
    "workflow_jinja_tool_weaver": WorkflowJinjaToolWeaverModel,
    "workflow_jinja_tool_manual": WorkflowJinjaToolManualModel,
    "workflow_jinja_file_prompt": WorkflowJinjaFilePromptModel,
    "workflow_jinja_file_schema": WorkflowJinjaFileSchemaModel,
    "workflow_jinja_file_api": WorkflowJinjaFileApiModel,
    "workflow_jinja_file_template": WorkflowJinjaFileTemplateModel,
    "workflow_jinja_file_weaver": WorkflowJinjaFileWeaverModel,
    "workflow_jinja_file_manual": WorkflowJinjaFileManualModel,
    "workflow_tool_file_prompt": WorkflowToolFilePromptModel,
    "workflow_tool_file_schema": WorkflowToolFileSchemaModel,
    "workflow_tool_file_api": WorkflowToolFileApiModel,
    "workflow_tool_file_template": WorkflowToolFileTemplateModel,
    "workflow_tool_file_weaver": WorkflowToolFileWeaverModel,
    "workflow_tool_file_manual": WorkflowToolFileManualModel,
    "workflow_all_prompt": WorkflowAllPromptModel,
    "workflow_all_schema": WorkflowAllSchemaModel,
    "workflow_all_api": WorkflowAllApiModel,
    "workflow_all_template": WorkflowAllTemplateModel,
    "workflow_all_weaver": WorkflowAllWeaverModel,
    "workflow_all_manual": WorkflowAllManualModel,
    "workflow_fsm_jinja_prompt": WorkflowFsmJinjaPromptModel,
    "workflow_fsm_jinja_schema": WorkflowFsmJinjaSchemaModel,
    "workflow_fsm_jinja_api": WorkflowFsmJinjaApiModel,
    "workflow_fsm_jinja_template": WorkflowFsmJinjaTemplateModel,
    "workflow_fsm_jinja_weaver": WorkflowFsmJinjaWeaverModel,
    "workflow_fsm_jinja_manual": WorkflowFsmJinjaManualModel,
    "workflow_fsm_tool_prompt": WorkflowFsmToolPromptModel,
    "workflow_fsm_tool_schema": WorkflowFsmToolSchemaModel,
    "workflow_fsm_tool_api": WorkflowFsmToolApiModel,
    "workflow_fsm_tool_template": WorkflowFsmToolTemplateModel,
    "workflow_fsm_tool_weaver": WorkflowFsmToolWeaverModel,
    "workflow_fsm_tool_manual": WorkflowFsmToolManualModel,
    "agent_none_prompt": AgentNonePromptModel,
    "agent_none_schema": AgentNoneSchemaModel,
    "agent_none_api": AgentNoneApiModel,
    "agent_none_template": AgentNoneTemplateModel,
    "agent_none_weaver": AgentNoneWeaverModel,
    "agent_none_manual": AgentNoneManualModel,
    "agent_jinja_prompt": AgentJinjaPromptModel,
    "agent_jinja_schema": AgentJinjaSchemaModel,
    "agent_jinja_api": AgentJinjaApiModel,
    "agent_jinja_template": AgentJinjaTemplateModel,
    "agent_jinja_weaver": AgentJinjaWeaverModel,
    "agent_jinja_manual": AgentJinjaManualModel,
    "agent_tool_prompt": AgentToolPromptModel,
    "agent_tool_schema": AgentToolSchemaModel,
    "agent_tool_api": AgentToolApiModel,
    "agent_tool_template": AgentToolTemplateModel,
    "agent_tool_weaver": AgentToolWeaverModel,
    "agent_tool_manual": AgentToolManualModel,
    "agent_file_prompt": AgentFilePromptModel,
    "agent_file_schema": AgentFileSchemaModel,
    "agent_file_api": AgentFileApiModel,
    "agent_file_template": AgentFileTemplateModel,
    "agent_file_weaver": AgentFileWeaverModel,
    "agent_file_manual": AgentFileManualModel,
    "agent_jinja_tool_prompt": AgentJinjaToolPromptModel,
    "agent_jinja_tool_schema": AgentJinjaToolSchemaModel,
    "agent_jinja_tool_api": AgentJinjaToolApiModel,
    "agent_jinja_tool_template": AgentJinjaToolTemplateModel,
    "agent_jinja_tool_weaver": AgentJinjaToolWeaverModel,
    "agent_jinja_tool_manual": AgentJinjaToolManualModel,
    "agent_jinja_file_prompt": AgentJinjaFilePromptModel,
    "agent_jinja_file_schema": AgentJinjaFileSchemaModel,
    "agent_jinja_file_api": AgentJinjaFileApiModel,
    "agent_jinja_file_template": AgentJinjaFileTemplateModel,
    "agent_jinja_file_weaver": AgentJinjaFileWeaverModel,
    "agent_jinja_file_manual": AgentJinjaFileManualModel,
    "agent_tool_file_prompt": AgentToolFilePromptModel,
    "agent_tool_file_schema": AgentToolFileSchemaModel,
    "agent_tool_file_api": AgentToolFileApiModel,
    "agent_tool_file_template": AgentToolFileTemplateModel,
    "agent_tool_file_weaver": AgentToolFileWeaverModel,
    "agent_tool_file_manual": AgentToolFileManualModel,
    "agent_all_prompt": AgentAllPromptModel,
    "agent_all_schema": AgentAllSchemaModel,
    "agent_all_api": AgentAllApiModel,
    "agent_all_template": AgentAllTemplateModel,
    "agent_all_weaver": AgentAllWeaverModel,
    "agent_all_manual": AgentAllManualModel,
    "agent_fsm_jinja_prompt": AgentFsmJinjaPromptModel,
    "agent_fsm_jinja_schema": AgentFsmJinjaSchemaModel,
    "agent_fsm_jinja_api": AgentFsmJinjaApiModel,
    "agent_fsm_jinja_template": AgentFsmJinjaTemplateModel,
    "agent_fsm_jinja_weaver": AgentFsmJinjaWeaverModel,
    "agent_fsm_jinja_manual": AgentFsmJinjaManualModel,
    "agent_fsm_tool_prompt": AgentFsmToolPromptModel,
    "agent_fsm_tool_schema": AgentFsmToolSchemaModel,
    "agent_fsm_tool_api": AgentFsmToolApiModel,
    "agent_fsm_tool_template": AgentFsmToolTemplateModel,
    "agent_fsm_tool_weaver": AgentFsmToolWeaverModel,
    "agent_fsm_tool_manual": AgentFsmToolManualModel,
    "event_none_prompt": EventNonePromptModel,
    "event_none_schema": EventNoneSchemaModel,
    "event_none_api": EventNoneApiModel,
    "event_none_template": EventNoneTemplateModel,
    "event_none_weaver": EventNoneWeaverModel,
    "event_none_manual": EventNoneManualModel,
    "event_jinja_prompt": EventJinjaPromptModel,
    "event_jinja_schema": EventJinjaSchemaModel,
    "event_jinja_api": EventJinjaApiModel,
    "event_jinja_template": EventJinjaTemplateModel,
    "event_jinja_weaver": EventJinjaWeaverModel,
    "event_jinja_manual": EventJinjaManualModel,
    "event_tool_prompt": EventToolPromptModel,
    "event_tool_schema": EventToolSchemaModel,
    "event_tool_api": EventToolApiModel,
    "event_tool_template": EventToolTemplateModel,
    "event_tool_weaver": EventToolWeaverModel,
    "event_tool_manual": EventToolManualModel,
    "event_file_prompt": EventFilePromptModel,
    "event_file_schema": EventFileSchemaModel,
    "event_file_api": EventFileApiModel,
    "event_file_template": EventFileTemplateModel,
    "event_file_weaver": EventFileWeaverModel,
    "event_file_manual": EventFileManualModel,
    "event_jinja_tool_prompt": EventJinjaToolPromptModel,
    "event_jinja_tool_schema": EventJinjaToolSchemaModel,
    "event_jinja_tool_api": EventJinjaToolApiModel,
    "event_jinja_tool_template": EventJinjaToolTemplateModel,
    "event_jinja_tool_weaver": EventJinjaToolWeaverModel,
    "event_jinja_tool_manual": EventJinjaToolManualModel,
    "event_jinja_file_prompt": EventJinjaFilePromptModel,
    "event_jinja_file_schema": EventJinjaFileSchemaModel,
    "event_jinja_file_api": EventJinjaFileApiModel,
    "event_jinja_file_template": EventJinjaFileTemplateModel,
    "event_jinja_file_weaver": EventJinjaFileWeaverModel,
    "event_jinja_file_manual": EventJinjaFileManualModel,
    "event_tool_file_prompt": EventToolFilePromptModel,
    "event_tool_file_schema": EventToolFileSchemaModel,
    "event_tool_file_api": EventToolFileApiModel,
    "event_tool_file_template": EventToolFileTemplateModel,
    "event_tool_file_weaver": EventToolFileWeaverModel,
    "event_tool_file_manual": EventToolFileManualModel,
    "event_all_prompt": EventAllPromptModel,
    "event_all_schema": EventAllSchemaModel,
    "event_all_api": EventAllApiModel,
    "event_all_template": EventAllTemplateModel,
    "event_all_weaver": EventAllWeaverModel,
    "event_all_manual": EventAllManualModel,
    "event_fsm_jinja_prompt": EventFsmJinjaPromptModel,
    "event_fsm_jinja_schema": EventFsmJinjaSchemaModel,
    "event_fsm_jinja_api": EventFsmJinjaApiModel,
    "event_fsm_jinja_template": EventFsmJinjaTemplateModel,
    "event_fsm_jinja_weaver": EventFsmJinjaWeaverModel,
    "event_fsm_jinja_manual": EventFsmJinjaManualModel,
    "event_fsm_tool_prompt": EventFsmToolPromptModel,
    "event_fsm_tool_schema": EventFsmToolSchemaModel,
    "event_fsm_tool_api": EventFsmToolApiModel,
    "event_fsm_tool_template": EventFsmToolTemplateModel,
    "event_fsm_tool_weaver": EventFsmToolWeaverModel,
    "event_fsm_tool_manual": EventFsmToolManualModel,
    "template_none_prompt": TemplateNonePromptModel,
    "template_none_schema": TemplateNoneSchemaModel,
    "template_none_api": TemplateNoneApiModel,
    "template_none_template": TemplateNoneTemplateModel,
    "template_none_weaver": TemplateNoneWeaverModel,
    "template_none_manual": TemplateNoneManualModel,
    "template_jinja_prompt": TemplateJinjaPromptModel,
    "template_jinja_schema": TemplateJinjaSchemaModel,
    "template_jinja_api": TemplateJinjaApiModel,
    "template_jinja_template": TemplateJinjaTemplateModel,
    "template_jinja_weaver": TemplateJinjaWeaverModel,
    "template_jinja_manual": TemplateJinjaManualModel,
    "template_tool_prompt": TemplateToolPromptModel,
    "template_tool_schema": TemplateToolSchemaModel,
    "template_tool_api": TemplateToolApiModel,
    "template_tool_template": TemplateToolTemplateModel,
    "template_tool_weaver": TemplateToolWeaverModel,
    "template_tool_manual": TemplateToolManualModel,
    "template_file_prompt": TemplateFilePromptModel,
    "template_file_schema": TemplateFileSchemaModel,
    "template_file_api": TemplateFileApiModel,
    "template_file_template": TemplateFileTemplateModel,
    "template_file_weaver": TemplateFileWeaverModel,
    "template_file_manual": TemplateFileManualModel,
    "template_jinja_tool_prompt": TemplateJinjaToolPromptModel,
    "template_jinja_tool_schema": TemplateJinjaToolSchemaModel,
    "template_jinja_tool_api": TemplateJinjaToolApiModel,
    "template_jinja_tool_template": TemplateJinjaToolTemplateModel,
    "template_jinja_tool_weaver": TemplateJinjaToolWeaverModel,
    "template_jinja_tool_manual": TemplateJinjaToolManualModel,
    "template_jinja_file_prompt": TemplateJinjaFilePromptModel,
    "template_jinja_file_schema": TemplateJinjaFileSchemaModel,
    "template_jinja_file_api": TemplateJinjaFileApiModel,
    "template_jinja_file_template": TemplateJinjaFileTemplateModel,
    "template_jinja_file_weaver": TemplateJinjaFileWeaverModel,
    "template_jinja_file_manual": TemplateJinjaFileManualModel,
    "template_tool_file_prompt": TemplateToolFilePromptModel,
    "template_tool_file_schema": TemplateToolFileSchemaModel,
    "template_tool_file_api": TemplateToolFileApiModel,
    "template_tool_file_template": TemplateToolFileTemplateModel,
    "template_tool_file_weaver": TemplateToolFileWeaverModel,
    "template_tool_file_manual": TemplateToolFileManualModel,
    "template_all_prompt": TemplateAllPromptModel,
    "template_all_schema": TemplateAllSchemaModel,
    "template_all_api": TemplateAllApiModel,
    "template_all_template": TemplateAllTemplateModel,
    "template_all_weaver": TemplateAllWeaverModel,
    "template_all_manual": TemplateAllManualModel,
    "template_fsm_jinja_prompt": TemplateFsmJinjaPromptModel,
    "template_fsm_jinja_schema": TemplateFsmJinjaSchemaModel,
    "template_fsm_jinja_api": TemplateFsmJinjaApiModel,
    "template_fsm_jinja_template": TemplateFsmJinjaTemplateModel,
    "template_fsm_jinja_weaver": TemplateFsmJinjaWeaverModel,
    "template_fsm_jinja_manual": TemplateFsmJinjaManualModel,
    "template_fsm_tool_prompt": TemplateFsmToolPromptModel,
    "template_fsm_tool_schema": TemplateFsmToolSchemaModel,
    "template_fsm_tool_api": TemplateFsmToolApiModel,
    "template_fsm_tool_template": TemplateFsmToolTemplateModel,
    "template_fsm_tool_weaver": TemplateFsmToolWeaverModel,
    "template_fsm_tool_manual": TemplateFsmToolManualModel,
}
