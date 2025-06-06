import { useState } from "react";
import OperationsMenu from "./submenus/operations-menu/operations-menu";
import ColorMenu from "./submenus/color-menu/color-menu";
import AnimationMenu from "./submenus/animation-menu/animation-menu";

const SideMenu = () => {
  const [currentMenu, setCurrentMenu] = useState("operations");

  return (
    <div
      className={`flex flex-col gap-4 h-[100vh] w-[50vw] bg-white border border-gray-300 shadow-lg p-4 flex flex-col items-start`}
    >
      <div className="flex flex-row flex-wrap gap-2">
        <button className="pill" onClick={() => setCurrentMenu("operations")}>
          Operations
        </button>
        <button className="pill" onClick={() => setCurrentMenu("colors")}>
          Colors
        </button>
        <button className="pill" onClick={() => setCurrentMenu("animation")}>
          Animation
        </button>
      </div>
      {currentMenu == "operations" && <OperationsMenu></OperationsMenu>}
      {currentMenu == "colors" && <ColorMenu></ColorMenu>}
      {currentMenu == "animation" && <AnimationMenu></AnimationMenu>}
    </div>
  );
};

export default SideMenu;
