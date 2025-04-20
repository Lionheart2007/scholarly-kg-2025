import "./App.css";
import useGraph, { StateGraph } from "./state/useGraph";
import { GraphView } from "./components/graph-view";

function App() {
  const change = useGraph((state: StateGraph) => state.change);
  const graph = useGraph((state: StateGraph) => state.graph);

  const onclick = () => {
    graph.addNode(graph.nodes().length ?? 0, {
      x: 10 * Math.random(),
      y: 10 * Math.random(),
      size: 15,
      label: graph.nodes().length,
      color: "#FA4F40",
    });
    change();
  };

  return (
    <>
      <button onClick={onclick}>Click me</button>
      <div
        style={{
          height: "100vh",
          width: "100vw",
          borderWidth: "1px",
          borderColor: "black",
        }}
      >
        <GraphView></GraphView>;
      </div>
    </>
  );
}

export default App;
