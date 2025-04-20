import { useEffect } from "react";
import Graph from "graphology";
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import useGraph, { StateGraph } from "../state/useGraph";

const sigmaStyle = { height: "100vh", width: "100vw" };

// Component that load the graph
export const LoadGraph = () => {
  const loadGraph = useLoadGraph();
  const graph: Graph = useGraph((state: StateGraph) => state.graph);
  const lastChanged = useGraph((state: StateGraph) => state.lastChanged);

  useEffect(() => {
    loadGraph(graph);
  }, [loadGraph, graph, lastChanged]);

  return null;
};

// Component that display the graph
export const GraphView = () => {
  return (
    <>
      <SigmaContainer style={sigmaStyle}>
        <LoadGraph />
      </SigmaContainer>
    </>
  );
};
