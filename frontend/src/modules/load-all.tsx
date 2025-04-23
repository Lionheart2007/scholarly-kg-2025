import useGraph, { StateGraph } from "../state/use-graph";

const LoadFaculties = () => {
  const graph = useGraph((state: StateGraph) => state.graph);
  const change = useGraph((state: StateGraph) => state.change);

  const onClick = async () => {
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

    console.log(data);

    const n = data.nodes.n;
    for (const nEntity of n) {
      graph.mergeNode(nEntity.id, {
        x: Math.random(),
        y: Math.random(),
        size: 5,
        label: nEntity.properties.name,
      });
    }

    const m = data.nodes.m;
    for (const faculty of m) {
      if (faculty.id == undefined) continue;
      graph.mergeNode(faculty.id, {
        x: Math.random(),
        y: Math.random(),
        size: 5,
        label: faculty.properties.name,
      });
    }

    for (const belongsTo of data.edges.r) {
      if (!graph.hasNode(belongsTo.start)) continue;
      if (!graph.hasNode(belongsTo.end)) continue;
      graph.mergeEdge(belongsTo.start, belongsTo.end);
    }

    change();
  };

  return (
    <button
      onClick={onClick}
      className="bg-gray-100 p-1 px-2 border-gray-300 hover:bg-gray-200 border-1 rounded-md"
    >
      Load Faculties
    </button>
  );
};

export default LoadFaculties;
