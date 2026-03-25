import { useState } from "react";
import ManualMode from './modes/manualmode'
import AssistedMode from "./modes/AssistedMode";
import AutomaticMode from "./modes/AutomaticMode";

function App() {
  const [mode, setMode] = useState("manual");


  const handleModeChange = (newMode) => {
  setMode(newMode);

  if (newMode === "automatic") {
    fetch("http://localhost:8000/start-automatic", {
      method: "POST"
    });
  } else {
    fetch("http://localhost:8000/stop-automatic", {
      method: "POST"
    });
  }
};


  return (
    <div style={{padding: "30px", marginTop:"-55px"}}>
      <h1 style={{marginLeft: "10px", marginBottom:"20px"}}>AURA</h1>
      <button style={{
          backgroundColor: mode === "manual" ? "white" : "transparent",
          color: mode === "manual" ? "black" : "white",
          border: "2px solid white",
          padding: "10px 20px",
          marginLeft: "10px",
          cursor: "pointer",
          gap:"10px",
          marginRight:"10px",
          fontWeight: "bold",
        }} onClick={() => setMode("manual")}>Manual</button>
      <button style={{
          backgroundColor: mode === "automatic" ? "white" : "transparent",
          color: mode === "automatic" ? "black" : "white",
          border: "2px solid white",
          padding: "10px 20px",
          cursor: "pointer",
          gap:"10px",
          marginRight:"10px",
          fontWeight: "bold",
        }} onClick={() => handleModeChange("automatic")}>Automatic</button>
      <button style={{
          backgroundColor: mode === "assisted" ? "white" : "transparent",
          color: mode === "assisted" ? "black" : "white",
          border: "2px solid white",
          padding: "10px 20px",
          cursor: "pointer",
          gap:"10px",
          marginRight:"10px",
          fontWeight: "bold",
        }} onClick={() => setMode("assisted")}>Assisted</button>

      {mode === "manual" && <ManualMode />}
      {mode === "assisted" && <AssistedMode />}
      {mode === "automatic" && <AutomaticMode />}
    </div>
  );
}

export default App;
