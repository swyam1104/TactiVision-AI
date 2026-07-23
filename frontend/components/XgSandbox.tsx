import React, { useState, useEffect } from "react";
import Pitch from "./Pitch";

export default function XgSandbox() {
  const [shotX, setShotX] = useState<number>(105.0);
  const [shotY, setShotY] = useState<number>(40.0);
  const [bodyPart, setBodyPart] = useState<string>("Foot");
  const [technique, setTechnique] = useState<string>("Normal");
  const [shotType, setShotType] = useState<string>("Open Play");
  const [underPressure, setUnderPressure] = useState<boolean>(false);
  
  const [xg, setXg] = useState<number | null>(null);
  const [distance, setDistance] = useState<number>(0);
  const [angleDeg, setAngleDeg] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  // Helper calculations for UI display
  useEffect(() => {
    // Distance
    const dx = 120.0 - shotX;
    const dy = 40.0 - shotY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    setDistance(dist);
    
    // Angle (relative to goal mouth y=36 to y=44)
    const goalWidth = 8.0;
    const vAY = 36.0 - shotY;
    const vBY = 44.0 - shotY;
    const dot = dx * dx + vAY * vBY;
    const normA = Math.sqrt(dx * dx + vAY * vAY);
    const normB = Math.sqrt(dx * dx + vBY * vBY);
    const cosTheta = Math.max(-1.0, Math.min(1.0, dot / (normA * normB)));
    const angleRad = Math.acos(cosTheta);
    setAngleDeg((angleRad * 180) / Math.PI);
    
    // Auto predict on parameters change
    triggerPrediction();
  }, [shotX, shotY, bodyPart, technique, shotType, underPressure]);

  const triggerPrediction = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/predict/xg", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          x: shotX,
          y: shotY,
          body_part: bodyPart,
          technique: technique,
          shot_type: shotType,
          under_pressure: underPressure
        })
      });
      if (res.ok) {
        const data = await res.json();
        setXg(data.xg);
      }
    } catch (e) {
      // Fallback local mock formula if backend server is not reachable
      const d = distance;
      const a = (angleDeg * Math.PI) / 180;
      const isHeader = bodyPart === "Head" ? 1 : 0;
      const isVolley = technique === "Volley" || technique === "Half Volley" ? 1 : 0;
      const isFk = shotType === "Free Kick" ? 1 : 0;
      const press = underPressure ? 1 : 0;
      
      const logit = 0.5 - 0.11 * d + 1.6 * a - 0.7 * isHeader - 0.4 * press - 0.3 * isVolley;
      const prob = 1.0 / (1.0 + Math.exp(-logit));
      setXg(Math.round(prob * 100) / 100);
    } finally {
      setLoading(false);
    }
  };

  const handlePitchClick = (x: number, y: number) => {
    // Restrict shots to attacking half for realism
    if (x >= 60.0) {
      setShotX(x);
      setShotY(y);
    }
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 space-y-6 shadow-md">
      <div>
        <h3 className="text-lg font-bold text-slate-100">Explainable xG Simulator Sandbox</h3>
        <p className="text-xs text-muted-foreground mt-0.5">
          Click anywhere in the attacking half to position the shot. Adjust features to recalculate expected goals.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Pitch Click Target */}
        <div className="lg:col-span-3">
          <Pitch onClick={handlePitchClick}>
            {/* Draw crosshair goal target coordinates line */}
            <line x1="120" y1="40" x2={shotX} y2={shotY} stroke="#38bdf8" strokeDasharray="2" strokeWidth="0.5" strokeOpacity="0.6" />
            
            {/* Draw the shot node */}
            <g>
              <circle cx={shotX} cy={shotY} r="3" fill="#38bdf8" stroke="#ffffff" strokeWidth="1" className="animate-pulse" />
              <circle cx={shotX} cy={shotY} r="1" fill="#ffffff" />
            </g>
          </Pitch>
        </div>

        {/* Control Board & Output Gauges */}
        <div className="lg:col-span-2 flex flex-col justify-between space-y-4">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="col-span-2">
              <label className="block text-muted-foreground font-semibold mb-1">Shot Type</label>
              <select
                value={shotType}
                onChange={(e) => setShotType(e.target.value)}
                className="w-full bg-background border border-border p-2 rounded text-slate-200 focus:outline-none focus:border-green-500"
              >
                <option value="Open Play">Open Play</option>
                <option value="Free Kick">Direct Free Kick</option>
                <option value="Penalty">Penalty Kick</option>
              </select>
            </div>

            <div>
              <label className="block text-muted-foreground font-semibold mb-1">Body Part</label>
              <select
                value={bodyPart}
                onChange={(e) => setBodyPart(e.target.value)}
                className="w-full bg-background border border-border p-2 rounded text-slate-200 focus:outline-none"
              >
                <option value="Foot">Foot</option>
                <option value="Head">Header</option>
                <option value="Other">Other (Knee/Chest)</option>
              </select>
            </div>

            <div>
              <label className="block text-muted-foreground font-semibold mb-1">Technique</label>
              <select
                value={technique}
                onChange={(e) => setTechnique(e.target.value)}
                className="w-full bg-background border border-border p-2 rounded text-slate-200 focus:outline-none"
              >
                <option value="Normal">Normal Strike</option>
                <option value="Volley">Volley</option>
                <option value="Half Volley">Half Volley</option>
                <option value="Lob">Lob/Chip</option>
              </select>
            </div>

            <div className="col-span-2 flex items-center gap-2 p-2 bg-background/50 border border-border rounded">
              <input
                type="checkbox"
                id="pressureCheck"
                checked={underPressure}
                onChange={(e) => setUnderPressure(e.target.checked)}
                className="w-4 h-4 rounded accent-green-500 cursor-pointer"
              />
              <label htmlFor="pressureCheck" className="text-slate-300 select-none cursor-pointer">
                Under Defensive Pressure
              </label>
            </div>
          </div>

          {/* Model Prediction Metrics Output */}
          <div className="bg-background/80 border border-border p-4 rounded-xl space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-xs text-muted-foreground uppercase tracking-wider block">Predicted Probability</span>
                <span className="text-2xl font-black text-green-400">
                  {xg !== null ? (xg * 100).toFixed(1) : "--"}%
                </span>
              </div>
              <div className="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded text-lg font-black">
                {xg !== null ? xg.toFixed(2) : "--"} <span className="text-xs font-semibold">xG</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground border-t border-border/50 pt-3">
              <div>
                Distance to Goal: <span className="font-semibold text-slate-300">{distance.toFixed(1)}m</span>
              </div>
              <div>
                Goal Mouth Angle: <span className="font-semibold text-slate-300">{angleDeg.toFixed(1)}°</span>
              </div>
              <div>
                Shot Coordinates: <span className="font-semibold text-slate-300">({shotX.toFixed(0)}, {shotY.toFixed(0)})</span>
              </div>
              <div>
                Status: <span className="font-semibold text-green-500">Live Inference</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
