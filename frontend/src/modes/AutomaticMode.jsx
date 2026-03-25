import { useEffect, useRef, useState } from "react";

function AutomaticMode() {
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [zdata, setZdata] = useState(null);

  useEffect(() => {

    fetch("http://localhost:8000/Z_D")
      .then(res => res.json())
      .then(json => setZdata(json.message));

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

  return (
    <div
      style={{
        padding: "50px",
        paddingTop: "10px",
        color: "white",
      }}
    >
      <h2>Automatic Mode</h2>
      
      {/* Video Feeds */}
      <div style={{ display: "flex", flexDirection: "row", gap: "15px", marginTop: "20px" }}>
        <div>
          <h4>Camera 1</h4>
          <img
            src="http://localhost:8000/video-feed-1"
            alt="Camera 1"
            style={{
              width: "540px",
              height: "380px",
              border: "2px solid gray",
              borderRadius: "8px",
            }}
          />
        </div>

        <div>
          <h4>Camera 2</h4>
          <img
            src="http://localhost:8000/video-feed-2"
            alt="Camera 2"
            style={{
              width: "540px",
              height: "380px",
              border: "2px solid gray",
              borderRadius: "8px",
            }}
          />
        </div>
        <div style={{ marginBottom: "15px" }}>
              <div style={{ color: "#888", fontSize: "14px", marginBottom: "5px" }}>
                Z-Axis
              </div>
              <div
                style={{
                  color: "#fff",
                  fontSize: "32px",
                  fontWeight: "bold",
                  fontFamily: "monospace",
                }}
              >
                {zdata}
              </div>
            </div>
      </div>
    </div>
  );
}

export default AutomaticMode;