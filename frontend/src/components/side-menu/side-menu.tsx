import LoadFaculties from "../../modules/loadFaculty";
import useGraph, { StateGraph } from "../../state/useGraph";

const SideMenu = () => {
  const change = useGraph((state: StateGraph) => state.change);
  const graph = useGraph((state: StateGraph) => state.graph);
  const onclick = () => {
    graph.addNode(graph.nodes().length ?? 0, {
      x: 10 * Math.random(),
      y: 10 * Math.random(),
      size: 15,
      label: graph.nodes().length,
      color: "#FA4F40",
    });
    change();
  };

  return (
    <div
      className={` h-[100vh] w-[50vw]  bg-white border border-gray-300 shadow-lg p-4 flex flex-col items-start`}
    >
      <button onClick={onclick}>Click me</button>
      <LoadFaculties></LoadFaculties>
    </div>
  );
};

export default SideMenu;
