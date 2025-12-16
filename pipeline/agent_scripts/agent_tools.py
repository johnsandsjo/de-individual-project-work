from pipeline.agent_scripts.data_models import DbtSourceYml
import yaml
from pathlib import Path

src_models_path = Path(__file__).parents[1]/"data_transformation/models/source"

def create_new_yml_file(yml_data : DbtSourceYml):
    """Accepts a validated Pydantic object, converts it to a dict, and dumps it into a new yml file."""
    data_dict = yml_data.model_dump(exclude_none=True)
    file_name = data_dict.pop('file_name')
    
    #make it idempotent
    Path.mkdir(src_models_path, parents=True, exist_ok=True)

    # Ensure file ends in .yml
    file_name = f"{file_name}.yml"
    full_path = src_models_path / file_name
    
    with open(full_path, 'w') as file:
        yaml.dump(data_dict, file, sort_keys=False, indent=2)

    return f"Successfully created dbt YAML file"

def create_new_sql_file(sql_data : str, file_name: str):
    """
    Create a new source as a sql file inside the models/source folder
    Args:
        sql_data: The SQL content for the file.
        file_name: The name of the file (e.g. 'scb_stats.sql').
    """
    #makes it idempotent
    src_models_path.mkdir(parents=True, exist_ok=True)

    # Ensure file ends in .sql
    if not file_name.endswith('.sql'):
        file_name = f"{file_name}.sql"
    
    file_path = src_models_path / file_name
    
    with open(file_path, "w") as f:
        f.write(sql_data)
    
    return f"Successfully created {file_path}"