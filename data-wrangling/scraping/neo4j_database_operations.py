from neo4j import GraphDatabase

class Neo4jDatabase:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def add_node(self, label, properties):
        """
        Adds a node to the database with the given label and properties.

        :param label: Label for the node
        :param properties: Dictionary of properties for the node
        """
        query = f"CREATE (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }})"
        with self.driver.session() as session:
            session.run(query, **properties)

    def add_relationship(self, start_node_label, end_node_label, relationship_type, properties=None):
        """
        Adds a relationship between two nodes in the database with optional properties.

        :param start_node_label: Label of the starting node
        :param end_node_label: Label of the ending node
        :param relationship_type: Type of the relationship
        :param properties: Dictionary of properties for the relationship (optional)
        """
        if properties:
            props = ', '.join([f'{k}: ${k}' for k in properties.keys()])
            query = f"""
            MATCH (a:{start_node_label}), (b:{end_node_label})
            CREATE (a)-[r:{relationship_type} {{ {props} }}]->(b)
            """
        else:
            query = f"""
            MATCH (a:{start_node_label}), (b:{end_node_label})
            CREATE (a)-[:{relationship_type}]->(b)
            """
        with self.driver.session() as session:
            session.run(query, **(properties or {}))

    def clear_database(self):
        """
        Clears the entire database by deleting all nodes and relationships.
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def node_exists(self, label):
        """
        Checks if a node with the specified label exists in the database.

        :param label: Label of the node
        :return: True if the node exists, False otherwise
        """
        query = f"MATCH (n:{label}) RETURN COUNT(n) > 0 AS exists"
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()["exists"]
 

        
    def relationship_exists(self, start_node_label, end_node_label, relationship_type=None):
        """
        Checks if a relationship of the specified type exists between two nodes.

        :param start_node_label: Label of the starting node
        :param end_node_label: Label of the ending node
        :param relationship_type: Type of the relationship (optional)
        :return: True if the relationship exists, False otherwise
        """
        query = f"""
        MATCH (a:{start_node_label})-[r{':' + relationship_type if relationship_type else ''}]->(b:{end_node_label})
        RETURN COUNT(r) > 0 AS exists
        """
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()["exists"]
            
        
    def add_relationship_if_not_exists(self, start_node_label, end_node_label, relationship_type, properties=None):
        """
        Adds a relationship between two nodes if it does not already exist.

        :param start_node_label: Label of the starting node
        :param end_node_label: Label of the ending node
        :param relationship_type: Type of the relationship
        :param properties: Dictionary of properties for the relationship (optional)
        """
        # do this with one query 
        if properties:
            props = ', '.join([f'{k}: ${k}' for k in properties.keys()])
            query = f"""
            MATCH (a:{start_node_label}), (b:{end_node_label})
            MERGE (a)-[r:{relationship_type} {{ {props} }}]->(b)
            """
        else:
            query = f"""
            MATCH (a:{start_node_label}), (b:{end_node_label})
            MERGE (a)-[:{relationship_type}]->(b)
            """
        with self.driver.session() as session:

            session.run(query, **(properties or {}))