import React, { useState } from "react";
import Pitch from "./Pitch";

export interface PassNode {
  id: number;
  name: string;
  x: number;
  y: number;
  volume: number;
}

export interface PassLink {
  source: number;
  target: number;
  count: number;
}

interface PassingNetworkProps {
  nodes: PassNode[];
  links: PassLink[];
}

export default function PassingNetwork({ nodes, links }: PassingNetworkProps) {
  const [hoveredNode, setHoveredNode] = useState<PassNode | null>(null);

  // Find node coordinates by ID for lines
  const getNodeById = (id: number) => nodes.find((n) => n.id === id);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100">Passing Network & Build-up Structure</h3>
        <div className="text-xs text-muted-foreground">
          Showing average positions and pass links (min. 3 passes)
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Network Overlay */}
        <div className="lg:col-span-3">
          <Pitch>
            {/* Draw Links (passing pathways) first so they sit underneath nodes */}
            {links.map((link, idx) => {
              const sourceNode = getNodeById(link.source);
              const targetNode = getNodeById(link.target);
              if (!sourceNode || !targetNode) return null;

              // Line thickness based on pass volume
              // Min count is 3. Scale count to stroke width [0.5, 4.0]
              const strokeWidth = 0.5 + Math.min(link.count / 8, 3.5);

              return (
                <line
                  key={`link-${idx}`}
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke="#22c55e"
                  strokeWidth={strokeWidth}
                  strokeOpacity="0.4"
                  className="transition-all hover:stroke-opacity-90"
                />
              );
            })}

            {/* Draw Nodes (players) */}
            {nodes.map((node) => {
              // Volume represents passes. Scale volume to radius [2.5, 6.0]
              const r = 2.5 + Math.min((node.volume || 10) / 25, 3.5);

              return (
                <g key={`node-${node.id}`}>
                  {/* Outer pulsing ring on hover */}
                  {hoveredNode?.id === node.id && (
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={r + 1.5}
                      fill="none"
                      stroke="#22c55e"
                      strokeWidth="1"
                      className="animate-ping"
                    />
                  )}
                  {/* Solid node circle */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={r}
                    fill="#1e293b"
                    stroke="#22c55e"
                    strokeWidth="1.2"
                    className="cursor-pointer hover:fill-slate-800 transition-colors"
                    onMouseEnter={() => setHoveredNode(node)}
                    onMouseLeave={() => setHoveredNode(null)}
                  />
                  {/* Player initials/number text label */}
                  <text
                    x={node.x}
                    y={node.y + r + 3}
                    textAnchor="middle"
                    fill="#cbd5e1"
                    fontSize="2.2"
                    fontWeight="600"
                    className="pointer-events-none select-none bg-black"
                  >
                    {node.name.split(" ").pop() || node.name}
                  </text>
                </g>
              );
            })}
          </Pitch>
        </div>

        {/* Details card */}
        <div className="lg:col-span-1 flex flex-col justify-between p-5 bg-card border border-border rounded-xl min-h-[220px]">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Network Inspector
            </h4>
            {hoveredNode ? (
              <div className="space-y-3">
                <div>
                  <div className="text-sm font-bold text-slate-100">{hoveredNode.name}</div>
                  <div className="text-xs text-muted-foreground">Average Position</div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Pitch Coord X</div>
                    <div className="font-semibold text-slate-200">{hoveredNode.x.toFixed(1)}m</div>
                  </div>
                  <div className="bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Pitch Coord Y</div>
                    <div className="font-semibold text-slate-200">{hoveredNode.y.toFixed(1)}m</div>
                  </div>
                  <div className="col-span-2 bg-background/40 p-2 rounded border border-border/50">
                    <div className="text-muted-foreground">Passes Completed</div>
                    <div className="font-bold text-green-400 text-lg">{hoveredNode.volume}</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-32 flex items-center justify-center text-center text-xs text-muted-foreground">
                Hover over player nodes to inspect average coordinates and total completed passes.
              </div>
            )}
          </div>
          
          <div className="text-[10px] text-muted-foreground border-t border-border/50 pt-2 mt-4">
            Passing network coordinates are derived from the center of gravity (mean position) of all passes made.
          </div>
        </div>
      </div>
    </div>
  );
}
