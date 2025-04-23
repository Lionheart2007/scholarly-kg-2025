import { create } from "zustand";

export type StateParameters = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameters: Map<string, any>;
  set: (key: string, value: any) => void;
};

const useParameters = create<StateParameters>((set) => ({
  parameters: new Map(),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  set: (key: string, value: any) =>
    set((state: StateParameters) => {
      const newMap = new Map(state.parameters);
      newMap.set(key, value);
      return { parameters: newMap };
    }),
}));

export default useParameters;
