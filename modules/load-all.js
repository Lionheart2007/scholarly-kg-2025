export const entry = {
  title: "Load All",
  parameters: [],
  onExecute: async (graph, change) => {
    const data = await (
      await fetch("http://localhost:3000/data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: "MATCH (n)-[r]->(m)",

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

    const n = data.nodes.n;
    for (const nEntity of n) {
      graph.mergeNode(nEntity.id, {
        x: Math.random(),
        y: Math.random(),
        size: 1,
        label: nEntity.properties.name,
      });
    }

    const m = data.nodes.m;
    for (const faculty of m) {
      if (faculty.id == undefined) continue;
      graph.mergeNode(faculty.id, {
        x: Math.random(),
        y: Math.random(),
        size: 1,
        label: faculty.properties.name,
      });
    }

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
