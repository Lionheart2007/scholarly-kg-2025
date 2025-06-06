export const entry = {
  title: "Just a Test",
  onExecute: (graph, change) => {
    console.log(graph);

    graph.addNodeData([
      {
        id: "Test Node",
        style: {
          fill: "#e93758",
        },
      },
    ]);

    change();
  },
};
