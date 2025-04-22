import { useEffect, useState } from "react";
import useGraph, { StateGraph } from "../../state/useGraph";
import Graph from "graphology";

const SideMenu = () => {
  const change = useGraph((state: StateGraph) => state.change);
  const graph = useGraph((state: StateGraph) => state.graph);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [entries, setEntries] = useState<any[]>([]);
  const [loadedEntry, setLoadedEntry] = useState<
    { onExecute: (graph: Graph, change: () => void) => void } | undefined
  >(undefined);

  const setList = async () => {
    const data = await (await fetch("http://localhost:3002")).json();
    setEntries(data);
    setLoadedEntry(undefined);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const onClickEntry = async (entry: any) => {
    const module = await import(
      "http://localhost:3002/" +
        entry.fileName +
        "?v=" +
        Date.now() /* @vite-ignore */
    );
    setLoadedEntry(module.entry);
  };

  const onExecuteEntry = async () => {
    loadedEntry?.onExecute(graph, change);
  };

  useEffect(() => {
    setList();
  }, []);

  return (
    <div
      className={` h-[100vh] w-[50vw] bg-white border border-gray-300 shadow-lg p-4 flex flex-col items-start`}
    >
      <div className="flex justify-between w-full flex-row">
        <h2 className="font-bold">Operations ({entries.length})</h2>
        <span
          onClick={setList}
          className="material-symbols-rounded text-gray-300 hover:text-black w-fit hover:rotate-45 transition-all cursor-pointer"
        >
          refresh
        </span>
      </div>
      <div className="w-full py-8">
        {entries.map((e) => (
          <div
            onClick={() => onClickEntry(e)}
            key={e.fileName}
            className="border-b-1 last:border-b-0 border-gray-300 w-full border-x-0 hover:bg-gray-100 cursor-pointer"
          >
            {e.title}
          </div>
        ))}
      </div>

      {loadedEntry != undefined && (
        <button
          onClick={onExecuteEntry}
          className="py-1 rounded-md px-2 bg-gray border-1 border-gray-300 hover:bg-gray-100 "
        >
          Execute
        </button>
      )}
    </div>
  );
};

export default SideMenu;
