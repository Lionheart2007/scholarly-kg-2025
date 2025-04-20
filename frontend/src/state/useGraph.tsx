import Graph from "graphology";
import { create } from "zustand";

export type StateGraph = {
  graph: Graph;
  lastChanged: Date;
  change: () => void;
  setGraph: (graph: Graph) => void;
};

const useGraph = create<StateGraph>((set) => ({
  lastChanged: new Date(),
  graph: new Graph(),

  change: () => set({ lastChanged: new Date() }),
  setGraph: (graph: Graph) => set({ graph: graph }),
}));

export default useGraph;
