import Graph from "graphology";
import { ParameterSetter } from "../../../parameter-setter/parameter-setter";
import { useEffect, useState } from "react";
import useGraph, { StateGraph } from "../../../../state/use-graph";
import useParameters, {
  StateParameters,
} from "../../../../state/use-parameters";

const OperationsMenu = () => {
  const change = useGraph((state: StateGraph) => state.change);
  const graph = useGraph((state: StateGraph) => state.graph);
  const parameters = useParameters(
    (state: StateParameters) => state.parameters
  );
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [entries, setEntries] = useState<any[]>([]);
  const [loadedEntry, setLoadedEntry] = useState<
    | {
        title: string;
        parameters: any[];
        onExecute: (
          graph: Graph,
          change: () => void,
          parameters: Map<string, any>
        ) => void;
      }
    | undefined
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
    loadedEntry?.onExecute(graph, change, parameters);
  };

  useEffect(() => {
    setList();
  }, []);

  return (
    <div className="w-full">
      <div className="flex justify-between w-full flex-row">
        <h2 className="font-bold">Operations ({entries.length})</h2>

        <span
          onClick={setList}
          className="material-symbols-rounded text-gray-300 hover:text-black w-fit hover:rotate-45 transition-all cursor-pointer"
        >
          refresh
        </span>
      </div>
      {loadedEntry == undefined && (
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
      )}

      {loadedEntry != undefined && (
        <div className="flex flex-col gap-2 w-full">
          <div className="flex flex-row justify-between w-full">
            <h2>{loadedEntry.title}</h2>
            <span
              onClick={() => setLoadedEntry(undefined)}
              className="material-symbols-rounded text-gray-300 hover:text-black w-fit transition-all cursor-pointer"
            >
              close
            </span>
          </div>

          <ParameterSetter
            parameters={loadedEntry.parameters}
            entry={loadedEntry.title}
          ></ParameterSetter>

          <button onClick={onExecuteEntry} className="">
            Execute
          </button>
        </div>
      )}
    </div>
  );
};

export default OperationsMenu;
