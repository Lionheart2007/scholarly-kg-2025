import { FC, useEffect, useState } from "react";
import Graph from "graphology";
import {
  SigmaContainer,
  useLoadGraph,
  useRegisterEvents,
  useSigma,
} from "@react-sigma/core";
import "@react-sigma/core/lib/style.css";
import useGraph, { StateGraph } from "../state/useGraph";
import {
  useWorkerLayoutForce,
} from "@react-sigma/layout-force";

const sigmaStyle = { height: "100vh", width: "100vw" };

const GraphEvents = () => {
  const registerEvents = useRegisterEvents();
  const sigma = useSigma();
  const [draggedNode, setDraggedNode] = useState<string | null>(null);

  useEffect(() => {
    // Register the events
    registerEvents({
      downNode: (e) => {
        setDraggedNode(e.node);
        sigma.getGraph().setNodeAttribute(e.node, "highlighted", true);
      },
      // On mouse move, if the drag mode is enabled, we change the position of the draggedNode
      mousemovebody: (e) => {
        if (!draggedNode) return;
        // Get new position of node
        const pos = sigma.viewportToGraph(e);
        sigma.getGraph().setNodeAttribute(draggedNode, "x", pos.x);
        sigma.getGraph().setNodeAttribute(draggedNode, "y", pos.y);

        // Prevent sigma to move camera:
        e.preventSigmaDefault();
        e.original.preventDefault();
        e.original.stopPropagation();
      },
      // On mouse up, we reset the autoscale and the dragging mode
      mouseup: () => {
        if (draggedNode) {
          setDraggedNode(null);
          sigma.getGraph().removeNodeAttribute(draggedNode, "highlighted");
        }
      },
      // Disable the autoscale at the first down interaction
      mousedown: () => {
        if (!sigma.getCustomBBox()) sigma.setCustomBBox(sigma.getBBox());
      },
    });
  }, [registerEvents, sigma, draggedNode]);

  return null;
};

const Force: FC = () => {
  const { start, kill } = useWorkerLayoutForce();

  useEffect(() => {
    start();

    return () => kill();
  }, [start, kill]);

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
        <GraphEvents></GraphEvents>
        <Force></Force>
      </SigmaContainer>
    </>
  );
};
