import { FC, useEffect, useState } from "react";
import Graph from "graphology";
import {
  SigmaContainer,
  useLoadGraph,
  useRegisterEvents,
  useSigma,
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import useGraph, { StateGraph } from "../../state/useGraph";
import { useWorkerLayoutForceAtlas2 } from "@react-sigma/layout-forceatlas2";

const sigmaStyle = { height: "100vh", width: "100vw" };

const Force: FC = () => {
  const { start, stop } = useWorkerLayoutForceAtlas2({
    settings: {
      gravity: 0.1,
      slowDown: 0.8,
      barnesHutOptimize: true,
    },
  });
  const lastChanged = useGraph((state: StateGraph) => state.lastChanged);
  useEffect(() => {
    start();

    return () => stop();
  }, [start, stop]);

  useEffect(() => {
    start();
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
