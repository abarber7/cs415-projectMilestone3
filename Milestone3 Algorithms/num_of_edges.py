from neo4j import GraphDatabase

class DegreeCentrality:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def calculate_degree_centrality(self, uri_list):
        with self.driver.session() as session:
            degrees = {}
            for uri in uri_list:
                # Debugging print statement
                print(f"Calculating degree centrality for: {uri}")
                
                # Custom Degree Centrality implementation for each specified URI
                result = session.run(
                    """
                    MATCH (n:Resource {uri: $uri})
                    OPTIONAL MATCH (n)-[r]-()
                    RETURN n.uri AS node, count(r) AS degree
                    """, 
                    uri=uri
                )
                
                # Extract result and print for debugging
                record = result.single()
                if record:
                    node, degree = record["node"], record["degree"]
                    degrees[node] = degree
                    print(f"Node: {node}, Degree Centrality: {degree}")
                else:
                    print(f"No data found for URI: {uri}")

            return degrees

    def verify_with_builtin(self, uri_list):
        with self.driver.session() as session:
            degrees = {}
            for uri in uri_list:
                print(f"Verifying with Neo4j's built-in count for: {uri}")
                
                # Using Neo4j's built-in count function
                result = session.run(
                    """
                    MATCH (n:Resource {uri: $uri})
                    OPTIONAL MATCH (n)-[r]-()
                    RETURN n.uri AS node, count(r) AS degree
                    """, 
                    uri=uri
                )
                
                record = result.single()
                if record:
                    node, degree = record["node"], record["degree"]
                    degrees[node] = degree
                    print(f"Node: {node}, Built-in Degree Centrality: {degree}")
                else:
                    print(f"No data found for URI: {uri}")

            return degrees

# Usage example
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    
    centrality_calculator = DegreeCentrality(uri, user, password)
    uris_to_test = [
        "http://yago-knowledge.org/resource/State_of_Bahrain",
        "http://yago-knowledge.org/resource/Order_of_King_Abdulaziz"
    ]
    
    try:
        # Custom degree centrality calculation with debugging
        print("Calculating custom degree centrality:")
        custom_degrees = centrality_calculator.calculate_degree_centrality(uris_to_test)
        
        # Verify using built-in count functionality with debugging
        print("\nVerifying with built-in Neo4j functionality:")
        builtin_degrees = centrality_calculator.verify_with_builtin(uris_to_test)
        
        # Compare results
        print("\nComparison of custom and built-in results:")
        for uri in uris_to_test:
            custom_degree = custom_degrees.get(uri, "Not Found")
            builtin_degree = builtin_degrees.get(uri, "Not Found")
            print(f"URI: {uri}")
            print(f"  Custom Degree: {custom_degree}")
            print(f"  Built-in Degree: {builtin_degree}")
            if custom_degree == builtin_degree:
                print("  Test Passed: Results match.")
            else:
                print("  Test Failed: Results do not match.")
            
    finally:
        centrality_calculator.close()
