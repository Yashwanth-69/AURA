import { useEffect, useRef, useState } from "react";

function ManualMode() {
  const areaRef = useRef(null);
  const socketRef = useRef(null);
  const [coordinates, setCoordinates] = useState({ x: 0, y: 0 });

  useEffect(() => {
    socketRef.current = new WebSocket("ws://localhost:8000/ws/manual");
    

    socketRef.current.onopen = () => {
      console.log("WebSocket Connected");
    };

    socketRef.current.onerror = (err) => {
      console.log("WebSocket Error:", err);
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket Closed");
    };

    return () => {
      socketRef.current.close();
    };
  }, []);

const handleMouseMove = (e) => {
  if (!areaRef.current || !socketRef.current) return;

  const rect = areaRef.current.getBoundingClientRect();

  const rawX = e.clientX - rect.left;
  const rawY = e.clientY - rect.top;

  // Normalize to 640x480
  const x = Math.floor((rawX / rect.width) * 640);
  const y = Math.floor((rawY / rect.height) * 480);

  setCoordinates({ x, y });
  socketRef.current.send(JSON.stringify({ x, y }));
};


  return (
    // <div style={{paddingLeft:"50px"}}> 
    //   <h2>Manual Mode</h2>
    //   <div
    //     ref={areaRef}
    //     onMouseMove={handleMouseMove}
    //    style={{
    //         width: "640px",
    //         height: "480px",
    //         backgroundColor: "#111",
    //         border: "3px solid red",
    //         borderRadius: "12px",
    //         cursor: "crosshair",
    //         boxShadow: "0 0 25px red",
    //       }}
    //   />
    // </div>
    <div style={{ paddingLeft: "50px", display: "flex", gap: "30px", alignItems: "flex-start" }}>
      <div>
        <h2>Manual Mode</h2>
        <div
          ref={areaRef}
          onMouseMove={handleMouseMove}
          style={{
            width: "640px",
            height: "480px",
            backgroundColor: "#111",
            border: "3px solid #111",
            borderRadius: "12px",
            cursor: "crosshair",
            boxShadow: "0 0 15px #adaaaa",
          }}
        />
      </div>

      {/* Coordinates Display */}
      <div style={{ marginTop: "75px" }}>
        <div style={{ 
          backgroundColor: "#1a1a1a", 
          padding: "20px", 
          borderRadius: "12px",
          border: "2px solid #333",
          minWidth: "200px"
        }}>
          <h3 style={{ color: "#fff", marginTop: 0, marginBottom: "20px" }}>Coordinates</h3>
          
          <div style={{ marginBottom: "15px" }}>
            <div style={{ color: "#888", fontSize: "14px", marginBottom: "5px" }}>X-Axis</div>
            <div style={{ color: "#fff", fontSize: "32px", fontWeight: "bold", fontFamily: "monospace" }}>
              {coordinates.x}
            </div>
          </div>

          <div>
            <div style={{ color: "#888", fontSize: "14px", marginBottom: "5px" }}>Y-Axis</div>
            <div style={{ color: "#fff", fontSize: "32px", fontWeight: "bold", fontFamily: "monospace" }}>
              {coordinates.y}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ManualMode;

