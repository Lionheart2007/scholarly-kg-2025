import { create } from "zustand";

export type StateAnimation = {
  stopped: boolean;
  setStopped: (newStopped: boolean) => void;
};

const useAnimation = create<StateAnimation>((set) => ({
  stopped: false,
  setStopped: (newStopped: boolean) =>
    set({
      stopped: newStopped,
    }),
}));

export default useAnimation;
