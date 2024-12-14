
from db_processors import NLToPostgresProcessor
from constants import CLOUD_SQL_CONNECTION, TABLE_METADATA

# Initialize the processor
processor = NLToPostgresProcessor(
    connection_params=CLOUD_SQL_CONNECTION,
    table_metadata=TABLE_METADATA
)

# Example natural language query
nl_query = "Top 10 most purchased products"

# Execute the query
results = processor.query_db(nl_query)

# Print results
if results["status"] == "success":
    print("Generated SQL Query:")
    print(results["sql_query"])
    print("\nResults:")
    for row in results["results"]:
        print(row)
else:
    print(results)
    print("Error:", results["message"])