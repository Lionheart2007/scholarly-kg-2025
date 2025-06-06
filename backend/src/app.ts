import express, { Request, Response } from "express";
import dotenv from "dotenv";
import neo4j from "neo4j-driver";
import cors from "cors";

dotenv.config();

const app = express();

app.use(cors());

const driver = neo4j.driver(
  `neo4j://${process.env.NEO4J_ADDRESS}:${process.env.NEO4J_PORT}`,
  neo4j.auth.basic(
    process.env.NEO4J_USERNAME || "",
    process.env.NEO4J_PASSWORD || ""
  )
);

const PORT = process.env.PORT || 3000;

// Middleware to parse JSON requests
app.use(express.json());

app.get("/", (req: Request, res: Response) => {
  res.send("These are not the droids you are looking for.");
});

app.post("/data", async (req: Request, res: Response) => {
  console.log(`/data called with query "${req.body.query}"`);
  if (!req.body || !req.body.query) {
    res.status(400).send("No valid query given");
    return;
  }

  const toReturn = new Map();
  const session = driver.session({ defaultAccessMode: neo4j.session.READ });

  if (req.body.node_mappings) {
    // Calculate a query that only fetches the variables specified under node mapping
    const nodes_query = `${req.body.query} RETURN ${Object.values(
      req.body.node_mappings
    ).join(",")}`;

    const result = await session.run(nodes_query);

    // Map results and remove duplicates
    const nodes: Map<string, any> = new Map();
    for (const [key, value] of Object.entries(req.body.node_mappings)) {
      const nodes_with_duplicates = result.records
        .flatMap((record) => {
          return record.get(value as string);
        })
        .map((node) => {
          const prepared = {
            id: node.identity.toString(),
            properties: node.properties,
            types: node.labels,
          };

          return prepared;
        });

      nodes.set(
        key,
        Array.from(
          nodes_with_duplicates
            .reduce((acc, item) => {
              acc.set(item.id, item);
              return acc;
            }, new Map())
            .values()
        )
      );
    }

    toReturn.set("nodes", Object.fromEntries(nodes));
  }

  if (req.body.edge_mappings) {
    // Calculate a query that only fetches the variables specified under edge mapping
    const edges_query = `${req.body.query} RETURN ${Object.values(
      req.body.edge_mappings
    ).join(",")}`;

    const result = await session.run(edges_query);

    const edges: Map<string, any[]> = new Map();
    for (const [key, value] of Object.entries(req.body.edge_mappings)) {
      const edges_for_value: any[] = [];
      result.records
        .filter((r) => r.has(value as string))
        .flatMap((r) => {
          return r.get(value as string);
        })
        .map((r) => ({
          start: r.start.toString(),
          end: r.end.toString(),
          type: r.type,
        }))
        .forEach((record) => {
          edges_for_value.push(record);
        });

      edges.set(key, edges_for_value);
    }

    toReturn.set("edges", Object.fromEntries(edges));
  }

  res.send(Object.fromEntries(toReturn));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
