# cs415 Search Engine Project

Within Neo4j Desktop, install the **Neosemantics (n10s)** plugin which enables Neo4j to store and query RDF data. Restart Neo4j after installing the plugin.

Configure Neosemantics for RDF Import
```
// Install the Neosemantics procedures
CALL n10s.graphconfig.init();
```

Upload YAGO Data into Neo4j
```
// Load YAGO TTL data into Neo4j
CALL n10s.rdf.import.fetch("file:///path_to_yago_data/yago-4.5.0_ttl.ttl", "Turtle");
```

Explore YAGO Data in Neo4j
```
MATCH (n) RETURN n LIMIT 10;

MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 10;
```

Optimize Data for Queries
```
CREATE INDEX ON :Entity(name);
```