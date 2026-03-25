import { useEffect, useRef, useState } from "react";

function AssistedMode() {
  const controlRef = useRef(null);
  const socketRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [coordinates, setCoordinates] = useState({ x: 0, y: 0 });
  
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
    setCoordinates({ x, y });
    socketRef.current.send(JSON.stringify({ x, y }));
  };

  return (
    // <div>
    //   <h2>Assisted Mode</h2>

    //   {/* Top Camera Section */}
    //   <div style={{ display: "flex", gap: "20px" }}>
    //     <img
    //       src="http://localhost:8000/video-feed-1"
    //       alt="Camera 1"
    //       style={{ width: "640px", height: "480px" }}
    //     />

    //     <img
    //       src="http://localhost:8000/video-feed-2"
    //       alt="Camera 2"
    //       style={{ width: "640px", height: "480px" }}
    //     />
    //   </div>

    //   {/* Control Box Below */}
    //   <div
    //     ref={controlRef}
    //     onMouseMove={handleMouseMove}
    //     style={{
    //       marginTop: "30px",
    //       width: "640px",
    //       height: "480px",
    //       border: "2px solid red",
    //       backgroundColor: "black",
    //     }}
    //   />
    // </div>
    <div
      style={{
        marginLeft:"-25px",
        padding: "0px",
        paddingTop: "10px",
        color: "white",
      }}
    >
      {/* Cameras on top */}
      <div style={{ display: "flex", flexDirection: "row", gap: "5px" }}>
        <div>
          <h4>Camera 1</h4>
          <img
            src="http://localhost:8000/video-feed-1"
            alt="Camera 1"
            style={{
              width: "300px",
              height: "220px",
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
              width: "300px",
              height: "220px",
              border: "2px solid gray",
              borderRadius: "8px",
            }}
          />
        </div>
      

      {/* Control Layer and Coordinates below */}
      
        <div>
          <h4 style={{ textAlign: "center" }}>Control Layer</h4>
          <div
            ref={controlRef}
            onMouseMove={handleMouseMove}
            style={{
              width: "640px",
              height: "480px",
              backgroundColor: "#111",
              border: "3px solid #111",
              borderRadius: "12px",
              cursor: "crosshair",
              boxShadow: "0 0 25px #adaaaa",
            }}
          />
        </div>
  </div>
        <div style={{ marginTop: "45px" }}>
          <div
            style={{
              backgroundColor: "#1a1a1a",
              padding: "20px",
              borderRadius: "12px",
              border: "2px solid #333",
              minWidth: "200px",
              width: "300px",
              height: "220px",
              marginTop:"-300px",
              marginLeft:"150px",
            }}
          >
            <h3 style={{ color: "#fff", marginTop: 0, marginBottom: "20px" }}>
              Coordinates
            </h3>

            <div style={{ marginBottom: "15px" }}>
              <div style={{ color: "#888", fontSize: "14px", marginBottom: "5px" }}>
                X-Axis
              </div>
              <div
                style={{
                  color: "#fff",
                  fontSize: "32px",
                  fontWeight: "bold",
                  fontFamily: "monospace",
                }}
              >
                {coordinates.x}
              </div>
            </div>

            <div>
              <div style={{ color: "#888", fontSize: "14px", marginBottom: "5px" }}>
                Y-Axis
              </div>
              <div
                style={{
                  color: "#fff",
                  fontSize: "32px",
                  fontWeight: "bold",
                  fontFamily: "monospace",
                }}
              >
                {coordinates.y}
              </div>
            </div>
            
          </div>
        </div>
      </div>
  );
}

export default AssistedMode;
