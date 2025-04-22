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

    def add_relationship(self, start_node, end_node, relationship_type, properties=None):
        """
        Adds a relationship between two nodes in the database with optional properties.

        :param start_node: The start node or its ID
        :param end_node: The end node or its ID
        :param relationship_type: Type of the relationship
        :param properties: Dictionary of properties for the relationship (optional)
        """
        if properties:
            props = ', '.join([f'{k}: ${k}' for k in properties.keys()])
            query = f"""
            MATCH (a), (b)
            WHERE a.id = $start_id AND b.id = $end_id
            CREATE (a)-[r:{relationship_type} {{ {props} }}]->(b)
            """
        else:
            query = f"""
            MATCH (a), (b)
            WHERE a.id = $start_id AND b.id = $end_id
            CREATE (a)-[:{relationship_type}]->(b)
            """
        
        # If nodes are passed directly, get their IDs
        start_id = start_node.get('id') if isinstance(start_node, dict) else start_node
        end_id = end_node.get('id') if isinstance(end_node, dict) else end_node
        
        params = {
            'start_id': start_id,
            'end_id': end_id,
            **(properties or {})
        }
        
        with self.driver.session() as session:
            session.run(query, **params)

    def clear_database(self):
        """
        Clears the entire database by deleting all nodes and relationships.
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def node_exists(self, id):
        """
        Checks if a node with the specified label exists in the database.

        :param label: Label of the node
        :return: True if the node exists, False otherwise
        """
        query = f"MATCH (n) WHERE n.id = $id RETURN COUNT(n) > 0 AS exists"
        with self.driver.session() as session:
            result = session.run(query, id=id)
            return result.single()["exists"]
 

        
    def relationship_exists(self, start_id, end_id, relationship_type=None):
        """
        Check if a relationship exists between nodes with given IDs.

        :param start_id: ID of the start node
        :param end_id: ID of the end node
        :param relationship_type: Type of relationship to check (optional)
        :return: True if relationship exists, False otherwise
        """
        if relationship_type:
            query = """
            MATCH (a)-[r:%s]->(b)
            WHERE a.id = $start_id AND b.id = $end_id
            RETURN COUNT(r) > 0 AS exists
            """ % relationship_type
        else:
            query = """
            MATCH (a)-[r]->(b)
            WHERE a.id = $start_id AND b.id = $end_id
            RETURN COUNT(r) > 0 AS exists
            """
        
        with self.driver.session() as session:
            result = session.run(query, start_id=start_id, end_id=end_id)
            return result.single()[0]
            
    def add_relationship_if_not_exists(self, start_node, end_node, relationship_type, properties=None):
        """
        Adds a relationship between two nodes if it does not already exist. 
        :param start_node: The start node or its ID
        :param end_node: The end node or its ID
        :param relationship_type: Type of relationship to create
        :param properties: Properties for the relationship (optional)
        """
        # Get IDs from nodes if nodes are passed
        start_id = start_node.get('id') if isinstance(start_node, dict) else start_node
        end_id = end_node.get('id') if isinstance(end_node, dict) else end_node 
        if properties:
            props = ', '.join([f'{k}: ${k}' for k in properties.keys()])
            query = f"""
            MATCH (a), (b)
            WHERE a.id = $start_id AND b.id = $end_id
            MERGE (a)-[r:{relationship_type} {{ {props} }}]->(b)
            """
        else:
            query = f"""
            MATCH (a), (b)
            WHERE a.id = $start_id AND b.id = $end_id
            MERGE (a)-[:{relationship_type}]->(b)
            """ 
        params = {
            'start_id': start_id,
            'end_id': end_id,
            **(properties or {})
        }   
        with self.driver.session() as session:
            session.run(query, **params)