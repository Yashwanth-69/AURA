import { useEffect, useRef, useState } from "react";

function AssistedMode() {
  const controlRef = useRef(null);
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/manual");

    socket.onopen = () => {
      console.log("WS Connected");
      setIsConnected(true);
    };

    socket.onclose = () => {
      console.log("WS Closed");
      setIsConnected(false);
    };

    socketRef.current = socket;

    return () => socket.close();
  }, []);

  const handleMouseMove = (e) => {
    if (!controlRef.current || !isConnected) return;

    const rect = controlRef.current.getBoundingClientRect();

    const rawX = e.clientX - rect.left;
    const rawY = e.clientY - rect.top;

    const x = Math.floor((rawX / rect.width) * 640);
    const y = Math.floor((rawY / rect.height) * 480);

    socketRef.current.send(JSON.stringify({ x, y }));
  };

  return (
    <div>
      <h2>Assisted Mode</h2>

      {/* Top Camera Section */}
      <div style={{ display: "flex", gap: "20px" }}>
        <img
          src="http://localhost:8000/video-feed-1"
          alt="Camera 1"
          style={{ width: "640px", height: "480px" }}
        />

        <img
          src="http://localhost:8000/video-feed-1"
          alt="Camera 2"
          style={{ width: "640px", height: "480px" }}
        />
      </div>

      {/* Control Box Below */}
      <div
        ref={controlRef}
        onMouseMove={handleMouseMove}
        style={{
          marginTop: "30px",
          width: "640px",
          height: "480px",
          border: "2px solid red",
          backgroundColor: "black",
        }}
      />
    </div>
  );
}

export default AssistedMode;
