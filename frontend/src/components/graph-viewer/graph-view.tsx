import { useEffect, useRef, useState } from "react";
import "@react-sigma/core/lib/style.css";
import useGraph, { StateGraph } from "../../state/use-graph";
import { Graph } from "@antv/g6";

// Component that display the graph
export const GraphView = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  const lastChanged = useGraph((state: StateGraph) => state.lastChanged);
  const change = useGraph((state: StateGraph) => state.change);
  const setGraph = useGraph((state: StateGraph) => state.setGraph);
  const graph = useGraph((state: StateGraph) => state.graph);

  useEffect(() => {
    setGraph(
      new Graph({
        container: containerRef.current!,
        width: window.innerWidth,
        height: window.innerHeight,
        layout: {
          type: "d3-force",
          collide: {
            strength: 0.5,
          },
        },
        behaviors: [
          "drag-canvas",
          "zoom-canvas",
          "drag-element-force",
          {
            key: "auto-adapt-label",
            type: "auto-adapt-label",
            padding: 0,
            throttle: 200,
          },
        ],
        plugins: [{ type: "grid-line", size: 50 }],
      })
    );
    change();
  }, []);

  useEffect(() => {
    if (!graph) return;

    graph.render();
  }, [lastChanged]);

  return <div className="w-screen h-screen " ref={containerRef}></div>;
};
