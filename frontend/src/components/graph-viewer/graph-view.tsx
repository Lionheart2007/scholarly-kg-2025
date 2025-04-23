import { FC, useEffect } from "react";
import Graph from "graphology";
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import useGraph, { StateGraph } from "../../state/use-graph";
import { useWorkerLayoutForceAtlas2 } from "@react-sigma/layout-forceatlas2";

const sigmaStyle = { height: "100vh", width: "100vw" };

const Force: FC = () => {
  const { start, stop } = useWorkerLayoutForceAtlas2({
    settings: {
      linLogMode: true,
      outboundAttractionDistribution: false,
      scalingRatio: 5,
      gravity: 10,
      slowDown: 100,
      barnesHutOptimize: true,
      barnesHutTheta: 0.6,
    },
  });
  const lastChanged = useGraph((state: StateGraph) => state.lastChanged);
  useEffect(() => {
    start();

    return () => stop();
  }, [start, stop]);

  useEffect(() => {
    start();
    setTimeout(() => stop(), 10_000);
  }, [lastChanged]);

  return null;
};
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
        <Force></Force>
      </SigmaContainer>
    </>
  );
};
