from neo4j import GraphDatabase

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        # Initialize connection to Neo4j database
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close connection to Neo4j database
        if self.driver:
            self.driver.close()

    def initialize_graph(self):
        # Initialize Neo4j graph configuration for RDF handling
        with self.driver.session() as session:
            try:
                session.run("CALL n10s.graphconfig.init()")
                print("Graph configuration initialized successfully.")
            except Exception as e:
                print(f"Error initializing graph configuration: {e}")

    def create_constraint(self):
        # Create a unique constraint on the 'uri' property for Resource nodes
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE")
                print("Constraint on Resource(uri) created successfully.")
            except Exception as e:
                print(f"Error creating constraint: {e}")

    def ingest_triples(self, file_path, batch_size=200000):
        # Ingest triples from the TTL file in batches to the Neo4j database
        with self.driver.session() as session:
            count = 0  # Track the total number of triples processed
            skipped_lines = 0  # Track lines that couldn't be parsed
            triples = []  # Store triples for batch insertion

            print(f"Starting data ingestion from {file_path}...")
            
            # Open and read the TTL file line by line
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split()
                    
                    # Skip lines that do not conform to the expected triple format
                    if len(parts) < 3:
                        print(f"Skipped line (could not parse): {line.strip()}")
                        skipped_lines += 1
                        continue
                    
                    # Parse and extract subject, predicate, and object from the line
                    subject = parts[0]
                    predicate = parts[1]
                    obj = " ".join(parts[2:])

                    # Append the parsed triple to the list for batch processing
                    triples.append((subject, predicate, obj))
                    count += 1

                    # Insert a batch into Neo4j once batch_size is reached
                    if count % batch_size == 0:
                        self._insert_batch(session, triples)
                        print(f"Ingested {count} triples so far...")
                        triples = []  # Clear batch after insertion

            # Insert any remaining triples that didn't complete a full batch
            if triples:
                self._insert_batch(session, triples)
                print(f"Final batch ingested with {len(triples)} triples.")

            print("Ingestion complete.")
            print(f"Total triples ingested: {count}")
            print(f"Total skipped lines: {skipped_lines}")

    def _insert_batch(self, session, triples):
        # Insert a batch of triples into Neo4j
        query = """
        UNWIND $triples AS triple
        MERGE (subject:Resource {uri: triple[0]})
        MERGE (object:Resource {uri: triple[2]})
        MERGE (subject)-[:RELATION {type: triple[1]}]->(object)
        """
        result = session.run(query, triples=triples)
        summary = result.consume()
        # Print nodes and relationships created in this batch
        print(f"Inserted {summary.counters.nodes_created} nodes and {summary.counters.relationships_created} relationships in this batch.")

# Usage example
if __name__ == "__main__":
    # Define Neo4j connection details
    uri = "bolt://localhost:7687"  # Update if your Neo4j instance uses a different address
    user = "neo4j"
    password = "12345678"
    file_path = "C:\\Users\\coota\\Documents\\WSU Grad School\\WSU Fall 2024\\CPT_s 415\\Milestone 3\\yago-facts.ttl"
    
    # Initialize the ingestor instance and perform ingestion
    ingestor = Neo4jIngestor(uri, user, password)
    
    try:
        ingestor.initialize_graph()  # Initialize graph configuration
        ingestor.create_constraint()  # Set up unique constraint on URIs
        ingestor.ingest_triples(file_path)  # Start the triple ingestion process
    finally:
        ingestor.close()  # Close the Neo4j connection when done
