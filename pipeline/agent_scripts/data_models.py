from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any


class ColumnSchema(BaseModel):
    """Represents a single column in the source data."""
    column_name: str = Field(description="The name of the column, improve the name from the source data.")
    data_type: str = Field(description="The inferred data type for the column (e.g., 'string', 'integer', 'date').")


class YAMLPromptDetails(BaseModel):
    """Structured data to be used to generate the final YAML creation prompt."""
    table_name: str = Field(description="Exactly the same as recieved from the prompt. E.g. if you recieved staging.scb_stats, set name to staging.scb_stats.")
    description: str = Field(description="A brief, one-sentence description of what the table's data includes.")
    columns: List[ColumnSchema] = Field(description="A list of all columns found in the source data.")

class SRCfile(BaseModel):
    """Structured data to be used to generate the final source SQL prompt."""
    table_name: str = Field(description="Exactly the same as recieved from the prompt. E.g. if you recieved staging.scb_stats, set name to staging.scb_stats.")
    columns: List[ColumnSchema] = Field(description="A list of all columns found in the source data.")

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
    file_name : str

class SqlFileContent(BaseModel):
    """A Pydantic model with its sole purpose to move the SQL content for the tool."""
    sql_data: str = Field(..., description="The prompt in which to convert into sql")
    file_name : str = Field(description="file name should be the same as table name  and include .sql prefix")