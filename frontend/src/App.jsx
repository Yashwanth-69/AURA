import { useState } from "react";
import ManualMode from './modes/manualmode'
import AssistedMode from "./modes/AssistedMode";

function App() {
  const [mode, setMode] = useState("manual");

  return (
    <div>
      <button onClick={() => setMode("manual")}>Manual</button>
      <button onClick={() => setMode("automatic")}>Automatic</button>
      <button onClick={() => setMode("assisted")}>Assisted</button>

      {mode === "manual" && <ManualMode />}
      {mode === "assisted" && <AssistedMode />}
    </div>
  );
}

export default App;
