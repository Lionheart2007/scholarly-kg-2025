import useAnimation, { StateAnimation } from "../../../../state/use-animation";

const AnimationMenu = () => {
  const setStopped = useAnimation((state: StateAnimation) => state.setStopped);
  return (
    <div className="flex flex-col gap-2">
      <p>Start and stop the layout animation as you please.</p>
      <div className="flex flex-row gap-2">
        <button onClick={() => setStopped(false)}>Start</button>
        <button onClick={() => setStopped(true)}>Stop</button>
      </div>
    </div>
  );
};

export default AnimationMenu;
