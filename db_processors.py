import re
import json
import vertexai
import psycopg2
from typing import Dict, List, Any
from psycopg2.extras import RealDictCursor
from vertexai.generative_models import GenerativeModel
from constants import (
    PROJECT_ID, NL2SQL_PROMPT, 
    MODEL_NAME, SYSTEM_PROMPT,
    GENERATION_CONFIG
    )

class NLToPostgresProcessor:
    def __init__(self, connection_params: Dict[str, str], table_metadata: Dict[str, str]):
        """
        Initialize the processor with database connection and table information.
        
        Args:
            connection_params: Database connection parameters
            table_metadata: Dictionary mapping table names to their descriptions
        """
        vertexai.init(project=PROJECT_ID)
        self.table_metadata = table_metadata
        self.connection_params = connection_params
        self.model = GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT
        )
        
        self.schema_cache: Dict[str, List[Dict[str, str]]] = {}

    def _get_db_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(
            **self.connection_params,
            cursor_factory=RealDictCursor
        )

    def _get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Fetch and format schema information for a given table from PostgreSQL."""
        if table_name in self.schema_cache:
            return self.schema_cache[table_name]

        schema_query = """
        SELECT 
            column_name,
            data_type,
            col_description((table_schema || '.' || table_name)::regclass::oid, ordinal_position) as description,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """

        schema_info = []
        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_query, (table_name,))
                columns = cur.fetchall()
                
                for col in columns:
                    schema_info.append({
                        "name": col['column_name'],
                        "type": col['data_type'],
                        "description": col['description'] or "No description available",
                        "nullable": col['is_nullable'],
                        "default": col['column_default']
                    })
        
        # Get foreign key information
        fk_query = """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = %s;
        """
        
        with self._get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(fk_query, (table_name,))
                foreign_keys = cur.fetchall()
                
                # Add foreign key information to schema
                for fk in foreign_keys:
                    for col in schema_info:
                        if col['name'] == fk['column_name']:
                            col['foreign_key'] = {
                                'references_table': fk['foreign_table_name'],
                                'references_column': fk['foreign_column_name']
                            }
        
        self.schema_cache[table_name] = schema_info
        return schema_info

    def _build_context_prompt(self) -> str:
        """Build a context prompt containing schema information and descriptions for all tables."""
        context = "Database Schema Information:\n\n"
        
        for table_name, description in self.table_metadata.items():
            context += f"Table: {table_name}\n"
            context += f"Description: {description}\n"
            context += "Columns:\n"
            
            schema_info = self._get_table_schema(table_name)
            for field in schema_info:
                context += f"- {field['name']} ({field['type']})"
                if 'foreign_key' in field:
                    context += f" [FK -> {field['foreign_key']['references_table']}.{field['foreign_key']['references_column']}]"
                context += f": {field['description']}\n"
            context += "\n"
            
        context += "\nRelationships:\n"
        # Add a section highlighting table relationships through foreign keys
        for table_name in self.table_metadata.keys():
            schema_info = self._get_table_schema(table_name)
            for field in schema_info:
                if 'foreign_key' in field:
                    context += f"- {table_name}.{field['name']} relates to {field['foreign_key']['references_table']}.{field['foreign_key']['references_column']}\n"
        
        return context
    
    def _extract_query(self, text):
        # Pattern to match JSON content between ```json and ```
        pattern = r'```json\s*({[^}]+})\s*```'
        
        # Find the match
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                # Parse the JSON string
                data = json.loads(json_str)
                # Extract the query value
                return data.get('query')
            except json.JSONDecodeError:
                return "Error: Invalid JSON format"
        return "Error: No JSON found"

    def _generate_query(self, nl_query: str) -> str:
        """Generate SQL query from natural language using Gemini."""
        context = self._build_context_prompt()
        prompt = NL2SQL_PROMPT.format(
            context=context,
            nl_query=nl_query
        )

        response = self.model.generate_content(
            prompt,
            generation_config=GENERATION_CONFIG
        )
        
        return self._extract_query(response.text.strip())

    def query_db(self, nl_query: str) -> Dict[str, Any]:
        """Execute a natural language query and return the results."""
        try:
            # Generate SQL query
            sql_query = self._generate_query(nl_query)
            
            # Execute query
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query)
                    rows = cur.fetchall()
            
            return {
                "status": "success",
                "sql_query": sql_query,
                "results": [dict(row) for row in rows]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "sql_query": sql_query if 'sql_query' in locals() else None
            }