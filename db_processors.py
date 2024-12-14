import re
import json
import vertexai
import psycopg2
from enum import Enum
from typing import Dict, List, Any, Tuple, Optional
from psycopg2.extras import RealDictCursor
from vertexai.generative_models import GenerativeModel
from constants import (
    PROJECT_ID, MODEL_NAME, SYSTEM_PROMPT,
    GENERATION_CONFIG, NL2SQL_PROMPT
)

class OperationType(Enum):
    INSERT = "INSERT"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    UNKNOWN = "UNKNOWN"

class NLToPostgresProcessor:
    def __init__(self, connection_params: Dict[str, str], table_metadata: Dict[str, str]):
        """Initialize with enhanced functionality for CRUD operations."""
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
    
    def _extract_query_info(self, text: str) -> Tuple[OperationType, str]:
        """Extract operation type and query from the model response."""
        pattern = r'```json\s*({[^}]+})\s*```'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                data = json.loads(match.group(1))
                operation = OperationType[data.get('operation', 'UNKNOWN')]
                query = data.get('query', '')
                return operation, query
            except (json.JSONDecodeError, KeyError):
                return OperationType.UNKNOWN, ""
        return OperationType.UNKNOWN, ""
    
    def _format_response(self, operation: OperationType, status: str, 
                        sql_query: str, results: Optional[List[Dict]] = None, 
                        message: Optional[str] = None) -> Dict[str, Any]:
        """Format the response based on the operation type and results."""
        response = {
            "operation": operation.value,
            "status": status,
            "sql_query": sql_query
        }

        if status == "success":
            if operation == OperationType.INSERT:
                response["created_record"] = results[0] if results else None
            elif operation == OperationType.READ:
                response["results"] = results
            elif operation == OperationType.UPDATE:
                response["updated_records"] = results
            elif operation == OperationType.DELETE:
                response["deleted_records"] = results
        else:
            response["message"] = message

        return response

    def _execute_query(self, operation: OperationType, sql_query: str) -> Tuple[List[Dict], Optional[str]]:
        """Execute the SQL query and return results based on operation type."""
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query)
                    
                    if operation != OperationType.READ:
                        conn.commit()
                    
                    if operation in [OperationType.INSERT, OperationType.UPDATE, OperationType.DELETE]:
                        rows = cur.fetchall() if cur.description else []
                    else:  # READ operation
                        rows = cur.fetchall()
                    
                    return [dict(row) for row in rows], None
                    
        except Exception as e:
            return [], str(e)

    def query_db(self, nl_query: str) -> Dict[str, Any]:
        """Process natural language query and execute corresponding CRUD operation."""
        try:
            # Generate SQL query with operation type
            context = self._build_context_prompt()
            prompt = NL2SQL_PROMPT.format(
                context=context,
                nl_query=nl_query
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=GENERATION_CONFIG
            )
            
            operation, sql_query = self._extract_query_info(response.text.strip())
            
            if operation == OperationType.UNKNOWN or not sql_query:
                return self._format_response(
                    operation=OperationType.UNKNOWN,
                    status="error",
                    sql_query=sql_query,
                    message="Failed to determine operation type or generate valid query"
                )
            
            # Execute the query
            results, error = self._execute_query(operation, sql_query)
            
            if error:
                return self._format_response(
                    operation=operation,
                    status="error",
                    sql_query=sql_query,
                    message=error
                )
            
            return self._format_response(
                operation=operation,
                status="success",
                sql_query=sql_query,
                results=results
            )
            
        except Exception as e:
            return self._format_response(
                operation=OperationType.UNKNOWN,
                status="error",
                sql_query=sql_query if 'sql_query' in locals() else None,
                message=str(e)
            )