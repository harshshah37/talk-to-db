from db_processors import NLToPostgresProcessor
from constants import CLOUD_SQL_CONNECTION, TABLE_METADATA

def print_results(results: dict):
    """Pretty print the results based on operation type."""
    print("\nOperation:", results["operation"])
    print("Status:", results["status"])
    print("\nGenerated SQL Query:")
    print(results["sql_query"])
    
    if results["status"] == "success":
        if results["operation"] == "INSERT":
            print("\nInserted Record:")
            print(results["created_record"])
        elif results["operation"] == "READ":
            print("\nResults:")
            for row in results["results"]:
                print(row)
        elif results["operation"] == "UPDATE":
            print("\nUpdated Records:")
            for record in results["updated_records"]:
                print(record)
        elif results["operation"] == "DELETE":
            print("\nDeleted Records:")
            for record in results["deleted_records"]:
                print(record)
    else:
        print("\nError:", results["message"])

def main():
    # Initialize the processor
    processor = NLToPostgresProcessor(
        connection_params=CLOUD_SQL_CONNECTION,
        table_metadata=TABLE_METADATA
    )

    # Example queries for different CRUD operations
    queries = [
        # INSERT example
        "Insert the data of the stockcode 52353A with description of ADT T-SHIRT and unitprice of 4.44",
        
        # READ example
        "Fetch the details of the stockcode of 52353A",
        
        # UPDATE example
        "Update the unitprice as 3.22 for the stockcode of 52353A",
        
        # # DELETE example
        "Delete the record of stockcode 52353A"
    ]

    # Process each query
    for query in queries:
        print("\n" + "="*50)
        print("Processing query:", query)
        results = processor.query_db(query)
        print_results(results)

if __name__ == "__main__":
    main()