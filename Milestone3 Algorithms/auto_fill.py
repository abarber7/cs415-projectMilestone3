from neo4j import GraphDatabase
from flask import Flask, request, jsonify

app = Flask(__name__)

# a class to manage the database connection and its queries
class Neo4jConnection:
    
    # to initialize the connection
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user,password))

    # to close the connection
    def close(self):
        self.driver.close()

    # main function
    def get_autofill(self, input_text):

        # cypher query to find nodes whos name property starts with the input_text
        with self.driver.session() as session:
            query = """
            MATCH (n:Topic)
            WHERE n.name STARTS WITH $input
            RETURN n.name AS suggestion
            LIMIT 10
            """

            # query is executes witht the input_text as the param
            result = session.run(query, input = input_text)
            
            # extracting the 'suggestion' field from the query result
            return [record["suggestion"] for record in result]

# neo4j credentials can be replaced if necessary, taken from shortest_path.py
neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "12345678")

@app.route('/autofill', methods = ['GET'])
def autofill():

    # getting the query
    query = request.args.get('query', '')
    if query: # if found, fetch suggestions

        suggestions = neo4j_conn.get_autofill(query)

        return jsonify(suggestions) # JSON response with the list of suggestions
        # for example ["Topic1", "Topic2", "Topic3"])
    
    else:
        return jsonify([]) # JSON response with empty list

if __name__ == "__main__":
    app.run(debug=True) # Needs frontend, but starts the flask server in debug mode
