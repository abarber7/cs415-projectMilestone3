from neo4j import GraphDatabase

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def custom_shortest_path(self, start_uri, end_uri):
        with self.driver.session() as session:
            queue = [[start_uri]]
            visited = set()

            while queue:
                path = queue.pop(0)
                node = path[-1]

                # Return path if end node is found
                if node == end_uri:
                    return path, len(path)

                # Skip nodes already visited
                if node in visited:
                    continue
                visited.add(node)

                # Query neighbors of the current node
                result = session.run(
                    """
                    MATCH (n:Resource {uri: $node})-[]-(neighbor:Resource)
                    RETURN neighbor.uri AS neighbor
                    """,
                    node=node
                )

                # Add each neighbor to the queue
                for record in result:
                    neighbor = record["neighbor"]
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

            return None, 0  # No path found

# Usage
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    ingestor = Neo4jIngestor(uri, user, password)

    try:
        start_uri = "http://yago-knowledge.org/resource/State_of_Bahrain"
        end_uri = "http://yago-knowledge.org/resource/Order_of_King_Abdulaziz"
        path, length = ingestor.custom_shortest_path(start_uri, end_uri)

        if path:
            print(f"Shortest path: {path}")
            print(f"Path length: {length}")
        else:
            print("No path found.")
    finally:
        ingestor.close()
