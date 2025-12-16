from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any


class ColumnSchema(BaseModel):
    """Represents a single column in the source data."""
    column_name: str = Field(description="The name of the column, copied exactly from the source data.")
    data_type: str = Field(description="The inferred data type for the column (e.g., 'string', 'integer', 'date').")


class YAMLPromptDetails(BaseModel):
    """Structured data to be used to generate the final YAML creation prompt."""
    table_name: str = Field(description="Exactly the same as recieved from the prompt. E.g. if you recieved staging.scb_stats, set name to staging.scb_stats.")
    description: str = Field(description="A brief, one-sentence description of what the table's data includes.")
    columns: List[ColumnSchema] = Field(description="A list of all columns found in the source data.")

class SRCfile(BaseModel):
    """Structured data to be used to generate the final source SQL prompt."""
    table_name: str = Field(description="Exactly the same as recieved from the prompt. E.g. if you recieved scb_stats, set name to scb_stats.")
    columns: List[ColumnSchema] = Field(description="A list of all columns found in the source data.")

class ColumnDefintion(BaseModel):
    name: str = Field(..., description="The name of the column.")
    description: Optional[str] = None
    data_type: str
    data_tests: Optional[List[str]] = Field(None, description="Optional list of basic dbt tests (e.g., ['not_null', 'unique']).")

class TableDefinition(BaseModel):
    name: str = Field(..., description="The name of the dbt model that selects from this source.")
    description: Optional[str] = None
    identifier: str = Field(..., description="The exact table name in the source schema.")
    columns : List[ColumnDefintion]

class SourceDefinition(BaseModel):
    name: Literal['dbt_agent'] = 'dbt_agent'
    database: Literal['grad-work-john'] = 'grad-work-john'
    schema: Literal['raw'] = 'raw'
    tables: List[TableDefinition]

class DbtSourceYml(BaseModel):
    version: Literal[2] = 2
    sources: List[SourceDefinition]
    file_name : str

class SqlFileContent(BaseModel):
    """Creating a sql model in from source."""
    sql_data: str = Field(..., description="sql syntax to select from source and create model")
    file_name : str = Field(description="file name should be same as table name and include .sql prefix")