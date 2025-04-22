export const entry = {
  entryTitle: "Just a test",
  onExecute: (graph, change) => {
    graph.clear();
    graph.addNode(Math.random() * 1000, {
      x: Math.random(),
      y: Math.random(),
      size: 10,
      label: "Test Node",
    });

    change();
  },
};
