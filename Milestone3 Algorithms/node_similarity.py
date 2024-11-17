from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class NodeSimilarityCalculator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def calculate_similarity(self, uri1, uri2):
        with self.driver.session() as session:
            # Retrieve features for the first node
            result1 = session.run(
                """
                MATCH (n:Resource {uri: $uri})-[:RELATION]-(m)
                RETURN collect(m.uri) AS neighbors
                """,
                uri=uri1
            )
            record1 = result1.single()
            neighbors1 = record1['neighbors'] if record1 else []

            # Retrieve features for the second node
            result2 = session.run(
                """
                MATCH (n:Resource {uri: $uri})-[:RELATION]-(m)
                RETURN collect(m.uri) AS neighbors
                """,
                uri=uri2
            )
            record2 = result2.single()
            neighbors2 = record2['neighbors'] if record2 else []

            # Create feature vectors and normalize
            all_neighbors = list(set(neighbors1 + neighbors2))
            vector1 = np.array([1 if neighbor in neighbors1 else 0 for neighbor in all_neighbors]).reshape(1, -1)
            vector2 = np.array([1 if neighbor in neighbors2 else 0 for neighbor in all_neighbors]).reshape(1, -1)

            # Calculate cosine similarity
            similarity_metric = cosine_similarity(vector1, vector2)[0][0]
            return similarity_metric

# Usage example
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    similarity_calculator = NodeSimilarityCalculator(uri, user, password)
    try:
        uri1 = 'http://yago-knowledge.org/resource/Belgium'
        uri2 = 'http://yago-knowledge.org/resource/Universal_Postal_Union'
        similarity = similarity_calculator.calculate_similarity(uri1, uri2)
        print(f"Similarity between URIs {uri1} and {uri2}: {similarity}")

    finally:
        similarity_calculator.close()
