export const entry = {
  title: "Load Suggestions",
  parameters: [
    { name: "First Name", type: "text", constraints: [] },
    {
      name: "Last Name",
      type: "text",
      constraints: [],
    },
  ],
  onExecute: async (graph, change, parameters) => {
    const firstName = parameters.get("Load Suggestions-First Name") ?? "";
    const lastName = parameters.get("Load Suggestions-Last Name") ?? "";

    graph.clear();

    const idTracker = new Set();

    const data = await (
      await fetch("http://localhost:3000/data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: `MATCH (n: Researcher)-[r:SUGGESTED_COAUTHORSHIP]->(m: Researcher) WHERE tolower(n.last_name) CONTAINS tolower("${lastName}") AND tolower(n.first_name) CONTAINS tolower("${firstName}")`,

          node_mappings: {
            n: "n",
            m: "m",
          },

          edge_mappings: {
            r: "r",
          },
        }),
      })
    ).json();

    console.log(data);

    graph.addNodeData(
      data.nodes.n.map((n) => {
        if (idTracker.has(n.id)) return null;
        idTracker.add(n.id);

        const toAdd = {
          id: n.id,
          size: 1,
          style: {
            fill: "#8D6A9F",
            labelText: `${n.properties.first_name} ${n.properties.last_name}`,
            labelBackground: true,
          },
        };

        return toAdd;
      })
    );

    graph.addNodeData(
      data.nodes.m
        .map((n) => {
          if (idTracker.has(n.id)) return null;
          idTracker.add(n.id);

          const toAdd = {
            id: n.id,
            style: {
              fill: "#EFC3E6",
              labelText: `${n.properties.first_name} ${n.properties.last_name}`,
              labelBackground: true,
            },
          };

          return toAdd;
        })
        .filter((n) => n != null)
    );

    const edgeTracker = new Set();

    const generateEdgeName = (start, end) =>
      start <= end ? `${start}-${end}` : `${end}-${start}`;

    graph.addEdgeData(
      data.edges.r
        .map((r) => {
          if (edgeTracker.has(generateEdgeName(r.start, r.end))) return null;
          edgeTracker.add(generateEdgeName(r.start, r.end));
          return {
            source: `${r.start}`,
            target: `${r.end}`,
          };
        })
        .filter((r) => r != null)
    );

    change();
  },
};
