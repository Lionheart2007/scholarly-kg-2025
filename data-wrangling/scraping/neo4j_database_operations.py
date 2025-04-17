from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"  
AUTH = ("neo4j", "afadfpafgkaeopdfafawefaefggergtaefaaw179y4710gdf0172dh9")

def add_node(label, properties):
    """
    Adds a node to the database with the given label and properties.

    :param label: Label for the node
    :param properties: Dictionary of properties for the node
    """
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            query = f"CREATE (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }})"
            session.run(query, **properties)
            # print(f"Node with label '{label}' and properties {properties} added to the database.")

def add_relationship(start_node_label, end_node_label, relationship_type):
    """
    Adds a relationship between two nodes in the database.

    :param start_node_label: Label of the starting node
    :param end_node_label: Label of the ending node
    :param relationship_type: Type of the relationship
    """
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            query = f"""
            MATCH (a:{start_node_label}), (b:{end_node_label})
            CREATE (a)-[:{relationship_type}]->(b)
            """
            session.run(query)
            # print(f"Relationship '{relationship_type}' created between '{start_node_label}' and '{end_node_label}'.")

def clear_database():
    """
    Clears the entire database by deleting all nodes and relationships.
    """
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared. All nodes and relationships deleted.")