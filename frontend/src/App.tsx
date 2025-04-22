import "./App.css";
import { GraphView } from "./components/graph-viewer/graph-view";
import { useState } from "react";
import SideMenu from "./components/side-menu/side-menu";

function App() {
  const [menuIsVisible, setMenuIsVisible] = useState(false);

  return (
    <div className="relative">
      <div
        className={`absolute top-0 left-0  transition-transform z-100 ${
          !menuIsVisible ? "-translate-x-full" : ""
        }`}
      >
        <button
          onClick={() => setMenuIsVisible((prev) => !prev)}
          className="absolute right-0 bg-white p-2 translate-x-[99%] border border-l-0 rounded-r-lg border-gray-300 translate-y-2 flex items-center"
        >
          <span className="material-symbols-rounded text-gray-400">menu</span>
        </button>
        <SideMenu></SideMenu>
      </div>
      <GraphView></GraphView>;
    </div>
  );
}

export default App;
