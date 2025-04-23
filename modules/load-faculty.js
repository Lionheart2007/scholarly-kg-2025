export const entry = {
  title: "Load Faculty",
  parameters: [
    {
      name: "Faculty Name",
      type: "text",
      constraints: { maxLength: 255, required: true, min: 0 },
    },
    {
      name: "Depth",
      type: "number",
      constraints: { min: 1, max: 5 },
    },
  ],
  onExecute: async (graph, change, parameters) => {
    graph.clear();

    const depth = parameters.get("Load Faculty-Depth") ?? 1;
    const query = parameters.get("Load Faculty-Faculty Name") ?? "";

    const data = await (
      await fetch("http://localhost:3000/data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: `MATCH (n)-[r*1..${depth}]->(f: Faculty) WHERE toLower(f.name) CONTAINS toLower("${query}")`,

          node_mappings: {
            n: "n",
            f: "f",
          },

          edge_mappings: {
            r: "r",
          },
        }),
      })
    ).json();

    const n = data.nodes.n;
    for (const nEntity of n) {
      graph.mergeNode(nEntity.id, {
        x: Math.random(),
        y: Math.random(),
        size: 5,
        label:
          nEntity.properties.name ??
          nEntity.properties.firstName + " " + nEntity.properties.lastName,
      });
    }

    const f = data.nodes.f[0];
    graph.mergeNode(f.id, {
      x: Math.random(),
      y: Math.random(),
      size: 10,
      label: f.properties.name,
    });

    for (const belongsTo of data.edges.r) {
      if (!graph.hasNode(belongsTo.start)) continue;
      if (!graph.hasNode(belongsTo.end)) continue;
      graph.mergeEdge(belongsTo.start, belongsTo.end, {
        size: 1,
      });
    }

    change();
  },
};
