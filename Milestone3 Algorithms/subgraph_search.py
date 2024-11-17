from neo4j import GraphDatabase

class KnowledgeGraphSearch:
    def __init__(self, uri, user, password):
        # Initialize connection to the Neo4j database
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the Neo4j database connection
        self.driver.close()

    def search_subgraph(self, keyword, limit=10):
        # Define a method to search for a subgraph based on a keyword
        with self.driver.session() as session:
            # Execute a Cypher query to match entities and relationships containing the keyword
            result = session.run(
                """
                MATCH (entity)-[relation]-(relatedEntity)
                WHERE entity.rdfs__label CONTAINS $keyword
                RETURN entity, relation, relatedEntity
                LIMIT $limit
                """,
                keyword=keyword, limit=limit
            )
            formatted_results = []  # Initialize a list to store formatted results
            for record in result:
                entity = record["entity"]  # Extract the entity node
                relation = record["relation"].type  # Extract the relationship type
                related_entity = record["relatedEntity"]  # Extract the related entity node

                # Append formatted data to the results list
                formatted_results.append({
                    "Entity Label": entity.get("rdfs__label", "N/A"),  # Retrieve entity label
                    "Entity URI": entity.get("uri", "N/A"),  # Retrieve entity URI
                    "Relation": relation,  # Get the relationship type
                    "Related Entity Label": related_entity.get("rdfs__label", "N/A"),  # Retrieve related entity label
                    "Related Entity URI": related_entity.get("uri", "N/A"),  # Retrieve related entity URI
                })
            return formatted_results  # Return the formatted results list

    def rank_results(self, subgraph):
        # Define a method to rank results based on relationship type
        ranked = sorted(subgraph, key=lambda x: x["Relation"])  # Sort results alphabetically by relationship type
        return ranked  # Return the ranked results

# Neo4j Credentials
NEO4J_URI = "neo4j://localhost:7687"  # Set the URI for connecting to the Neo4j database
NEO4J_USER = "neo4j"  # Set the username for authentication
NEO4J_PASSWORD = "12345678"  # Set the password for authentication

if __name__ == "__main__":
    # Create an instance of the KnowledgeGraphSearch class
    search_engine = KnowledgeGraphSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        keyword = "Albert Einstein"  # Define the keyword for the search
        subgraph = search_engine.search_subgraph(keyword)  # Search for subgraphs related to the keyword
        print(f"Subgraph for keyword '{keyword}':")  # Display the keyword
        for result in subgraph:
            print(f"- Entity Label: {result['Entity Label']}")  # Print the entity label
            print(f"  Entity URI: {result['Entity URI']}")  # Print the entity URI
            print(f"  Relation: {result['Relation']}")  # Print the relationship type
            print(f"  Related Entity Label: {result['Related Entity Label']}")  # Print the related entity label
            print(f"  Related Entity URI: {result['Related Entity URI']}")  # Print the related entity URI
            print("")  # Add a newline for better readability

        ranked_results = search_engine.rank_results(subgraph)  # Rank the results
        print("\nRanked Results:")  # Display ranked results
        for result in ranked_results:
            print(f"- Entity Label: {result['Entity Label']}")  # Print the ranked entity label
            print(f"  Entity URI: {result['Entity URI']}")  # Print the ranked entity URI
            print(f"  Relation: {result['Relation']}")  # Print the ranked relationship type
            print(f"  Related Entity Label: {result['Related Entity Label']}")  # Print the ranked related entity label
            print(f"  Related Entity URI: {result['Related Entity URI']}")  # Print the ranked related entity URI
            print("")  # Add a newline for better readability
    finally:
        search_engine.close()  # Close the database connection
