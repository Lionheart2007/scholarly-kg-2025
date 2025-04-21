import useGraph, { StateGraph } from "../state/useGraph";

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
          query: "MATCH (u: University)<-[b:BELONGS_TO]-(f: Faculty)",

          node_mappings: {
            university: "u",
            faculty: "f",
          },

          edge_mappings: {
            belongs_to: "b",
          },
        }),
      })
    ).json();

    const university = data.nodes.university[0];
    graph.mergeNode(university.id, {
      x: Math.random() * 10,
      y: Math.random() * 10,
      size: 15,
      label: university.properties.name,
    });

    const faculties = data.nodes.faculty;
    for (const faculty of faculties) {
      graph.mergeNode(faculty.id, {
        x: Math.random() * 10,
        y: Math.random() * 10,
        size: 15,
        label: faculty.properties.name,
      });
    }

    for (const belongsTo of data.edges.belongs_to) {
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
