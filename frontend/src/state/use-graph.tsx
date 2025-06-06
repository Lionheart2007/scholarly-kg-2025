import { Graph } from "@antv/g6";
import { create } from "zustand";

export type StateGraph = {
  graph: Graph | undefined;
  lastChanged: Date;
  change: () => void;
  setGraph: (graph: Graph) => void;
};

const useGraph = create<StateGraph>((set) => ({
  lastChanged: new Date(),
  graph: undefined,

  change: () => set({ lastChanged: new Date() }),
  setGraph: (graph: Graph) => set({ graph: graph }),
}));

export default useGraph;
