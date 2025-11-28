from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class FilePrompt(BaseModel):
    prompt: str

class ColumnDefintion(BaseModel):
    name: str = Field(..., description="The name of the column.")
    description: Optional[str] = None
    data_type: Optional[str] = None
    data_tests: Optional[List[str]] = Field(None, description="Optional list of basic dbt tests (e.g., ['not_null', 'unique']).")

class TableDefinition(BaseModel):
    name: str = Field(..., description="The name of the dbt staging model that selects from this source.")
    description: Optional[str] = None
    identifier: str = Field(..., description="The exact raw table name in the source schema.")
    columns : List[ColumnDefintion]

class SourceDefinition(BaseModel):
    name: Literal['dbt_agent'] = 'dbt_agent'
    database: Literal['prj_job_advertisements'] = 'prj_job_advertisements'
    schema: Literal['staging'] = 'staging'
    # Requires at least one table definition
    tables: List[TableDefinition]

class DbtSourceYml(BaseModel):
    sources: List[SourceDefinition]

class SqlFileContent(BaseModel):
    """A Pydantic model with its sole purpose to move the SQL content for the tool."""
    sql_data: str = Field(..., description="The prompt in which to convert into sql")