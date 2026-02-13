import { useEffect, useRef } from "react";

function ManualMode() {
  const areaRef = useRef(null);
  const socketRef = useRef(null);

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

  socketRef.current.send(JSON.stringify({ x, y }));
};


  return (
    <div>
      <h2>Manual Mode</h2>
      <div
        ref={areaRef}
        onMouseMove={handleMouseMove}
        style={{
          width: "800px",
          height: "500px",
          border: "2px solid white",
          backgroundColor: "black",
        }}
      />
    </div>
  );
}

export default ManualMode;

