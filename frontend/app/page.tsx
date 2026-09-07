"use client";

import React, { useState, useEffect } from "react";
import { 
  Activity, 
  Database, 
  Cpu, 
  Compass, 
  Bot, 
  Crosshair, 
  Users, 
  Map, 
  TrendingUp, 
  ShieldAlert 
} from "lucide-react";

import ShotMap, { Shot } from "@/components/ShotMap";
import PassingNetwork, { PassNode, PassLink } from "@/components/PassingNetwork";
import PlayerRadar, { MatchPlayer } from "@/components/PlayerRadar";
import XgSandbox from "@/components/XgSandbox";
import AssistantChat from "@/components/AssistantChat";
import { API_BASE_URL } from "@/lib/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"match" | "similarity" | "sandbox" | "assistant">("match");
  
  // Database datasets state
  const [competitions, setCompetitions] = useState<any[]>([]);
  const [selectedComp, setSelectedComp] = useState<string | null>(null);
  const [matches, setMatches] = useState<any[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState<number | null>(null);
  const [matchStats, setMatchStats] = useState<any | null>(null);
  const [shots, setShots] = useState<Shot[]>([]);
  const [passingNetwork, setPassingNetwork] = useState<{nodes: PassNode[], links: PassLink[]} | null>(null);
  const [passingTeamId, setPassingTeamId] = useState<number | null>(null);
  
  // Loading & data source indicators
  const [matchLoading, setMatchLoading] = useState<boolean>(false);
  const [passingLoading, setPassingLoading] = useState<boolean>(false);
  const [similarityLoading, setSimilarityLoading] = useState<boolean>(false);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  // Similarity states
  const [playersList, setPlayersList] = useState<any[]>([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState<number | null>(null);
  const [similarityData, setSimilarityData] = useState<any | null>(null);
  const [selectedMatchPlayer, setSelectedMatchPlayer] = useState<MatchPlayer | null>(null);

  // MLOps Status states
  const [systemOnline, setSystemOnline] = useState<boolean>(true);
  const [etlRunning, setEtlRunning] = useState<boolean>(false);
  const [trainingRunning, setTrainingRunning] = useState<boolean>(false);

  // Initial loads
  useEffect(() => {
    fetchCompetitions();
    fetchPlayers();
  }, []);

  // Fetch matches when competition changes
  useEffect(() => {
    if (selectedComp !== null) {
      const [compId, seasonId] = selectedComp.split("-").map(Number);
      fetchMatches(compId, seasonId);
    }
  }, [selectedComp]);

  // Fetch match details when match changes
  useEffect(() => {
    if (selectedMatchId !== null) {
      fetchMatchDetails(selectedMatchId);
    }
  }, [selectedMatchId]);

  // Fetch similarity details when player changes
  useEffect(() => {
    if (selectedPlayerId !== null) {
      fetchPlayerSimilarity(selectedPlayerId);
    }
  }, [selectedPlayerId]);

  const fetchCompetitions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/competitions`);
      if (!res.ok) throw new Error("Competitions request failed");
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setCompetitions(data);
        setSelectedComp(`${data[0].competition_id}-${data[0].season_id}`);
      } else {
        throw new Error("No competitions found");
      }
    } catch (e) {
      loggerFallback("Competitions server offline. Loading mock sets.");
      // Standard local fallback
      const mockComps = [
        {competition_id: 2, season_id: 27, competition_name: "Premier League", season_name: "2015/2016"},
        {competition_id: 43, season_id: 3, competition_name: "FIFA World Cup", season_name: "2018"},
        {competition_id: 43, season_id: 106, competition_name: "FIFA World Cup", season_name: "2022"},
        {competition_id: 11, season_id: 90, competition_name: "La Liga", season_name: "2020/2021"},
        {competition_id: 37, season_id: 4, competition_name: "FA Women's Super League", season_name: "2018/2019"}
      ];
      setCompetitions(mockComps);
      setSelectedComp("2-27");
    }
  };

  const fetchMatches = async (compId: number, seasonId: number) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/matches?competition_id=${compId}&season_id=${seasonId}`);
      if (!res.ok) throw new Error("Matches request failed");
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setMatches(data);
        setSelectedMatchId(data[0].id);
      } else {
        throw new Error("No matches found");
      }
    } catch (e) {
      let mockMatches: any[] = [];
      if (compId === 2) { // Premier League 2015/2016
        mockMatches = [
          {id: 3753983, home_team: {name: "Swansea City"}, away_team: {name: "Arsenal"}, match_date: "2015-10-31"},
          {id: 3754047, home_team: {name: "Liverpool"}, away_team: {name: "Swansea City"}, match_date: "2015-11-29"},
          {id: 3754058, home_team: {name: "Leicester City"}, away_team: {name: "AFC Bournemouth"}, match_date: "2016-01-02"},
          {id: 3754117, home_team: {name: "Aston Villa"}, away_team: {name: "Arsenal"}, match_date: "2015-12-13"},
          {id: 3754129, home_team: {name: "Arsenal"}, away_team: {name: "Liverpool"}, match_date: "2015-08-24"},
          {id: 3754160, home_team: {name: "Arsenal"}, away_team: {name: "Sunderland"}, match_date: "2015-12-05"},
          {id: 3754217, home_team: {name: "Chelsea"}, away_team: {name: "Arsenal"}, match_date: "2015-09-19"},
          {id: 3754245, home_team: {name: "West Bromwich Albion"}, away_team: {name: "Sunderland"}, match_date: "2015-10-17"},
          {id: 3754296, home_team: {name: "Arsenal"}, away_team: {name: "Manchester City"}, match_date: "2015-12-21"},
          {id: 3754309, home_team: {name: "Southampton"}, away_team: {name: "Arsenal"}, match_date: "2015-12-26"}
        ];
      } else if (compId === 43 && seasonId === 3) { // World Cup 2018
        mockMatches = [
          {id: 7534, home_team: {name: "Germany"}, away_team: {name: "Mexico"}, match_date: "2018-06-17"},
          {id: 7538, home_team: {name: "Sweden"}, away_team: {name: "South Korea"}, match_date: "2018-06-18"},
          {id: 7539, home_team: {name: "Poland"}, away_team: {name: "Senegal"}, match_date: "2018-06-19"},
          {id: 7543, home_team: {name: "Iran"}, away_team: {name: "Spain"}, match_date: "2018-06-20"},
          {id: 7544, home_team: {name: "Uruguay"}, away_team: {name: "Saudi Arabia"}, match_date: "2018-06-20"},
          {id: 7546, home_team: {name: "France"}, away_team: {name: "Peru"}, match_date: "2018-06-21"},
          {id: 7550, home_team: {name: "Serbia"}, away_team: {name: "Switzerland"}, match_date: "2018-06-22"},
          {id: 7554, home_team: {name: "England"}, away_team: {name: "Panama"}, match_date: "2018-06-24"},
          {id: 7584, home_team: {name: "Belgium"}, away_team: {name: "Japan"}, match_date: "2018-07-02"},
          {id: 8650, home_team: {name: "Brazil"}, away_team: {name: "Belgium"}, match_date: "2018-07-06"}
        ];
      } else if (compId === 43 && seasonId === 106) { // World Cup 2022
        mockMatches = [
          {id: 3857255, home_team: {name: "Japan"}, away_team: {name: "Spain"}, match_date: "2022-12-01"},
          {id: 3857271, home_team: {name: "England"}, away_team: {name: "Iran"}, match_date: "2022-11-21"},
          {id: 3857272, home_team: {name: "England"}, away_team: {name: "United States"}, match_date: "2022-11-25"},
          {id: 3857273, home_team: {name: "Wales"}, away_team: {name: "Iran"}, match_date: "2022-11-25"},
          {id: 3857274, home_team: {name: "Netherlands"}, away_team: {name: "Ecuador"}, match_date: "2022-11-25"},
          {id: 3857275, home_team: {name: "Tunisia"}, away_team: {name: "France"}, match_date: "2022-11-30"},
          {id: 3857276, home_team: {name: "Canada"}, away_team: {name: "Morocco"}, match_date: "2022-12-01"},
          {id: 3857277, home_team: {name: "Morocco"}, away_team: {name: "Croatia"}, match_date: "2022-11-23"},
          {id: 3857278, home_team: {name: "Iran"}, away_team: {name: "United States"}, match_date: "2022-11-29"},
          {id: 3857296, home_team: {name: "Croatia"}, away_team: {name: "Belgium"}, match_date: "2022-12-01"}
        ];
      } else if (compId === 11) { // La Liga 2020/2021
        mockMatches = [
          {id: 3773386, home_team: {name: "Deportivo Alavés"}, away_team: {name: "Barcelona"}, match_date: "2020-10-31"},
          {id: 3773457, home_team: {name: "Barcelona"}, away_team: {name: "Celta Vigo"}, match_date: "2021-05-16"},
          {id: 3773466, home_team: {name: "Celta Vigo"}, away_team: {name: "Barcelona"}, match_date: "2020-10-01"},
          {id: 3773497, home_team: {name: "Real Madrid"}, away_team: {name: "Barcelona"}, match_date: "2021-04-10"},
          {id: 3773565, home_team: {name: "Granada"}, away_team: {name: "Barcelona"}, match_date: "2021-01-09"},
          {id: 3773585, home_team: {name: "Barcelona"}, away_team: {name: "Real Madrid"}, match_date: "2020-10-24"},
          {id: 3773593, home_team: {name: "Barcelona"}, away_team: {name: "Villarreal"}, match_date: "2020-09-27"},
          {id: 3773631, home_team: {name: "Real Betis"}, away_team: {name: "Barcelona"}, match_date: "2021-02-07"},
          {id: 3773660, home_team: {name: "Barcelona"}, away_team: {name: "Levante UD"}, match_date: "2020-12-13"},
          {id: 3773665, home_team: {name: "Osasuna"}, away_team: {name: "Barcelona"}, match_date: "2021-03-06"}
        ];
      } else if (compId === 37) { // FA Women's Super League 2018/2019
        mockMatches = [
          {id: 19730, home_team: {name: "Chelsea FCW"}, away_team: {name: "Brighton & Hove Albion WFC"}, match_date: "2018-09-30"},
          {id: 19736, home_team: {name: "Chelsea FCW"}, away_team: {name: "Arsenal WFC"}, match_date: "2018-10-14"},
          {id: 19745, home_team: {name: "Brighton & Hove Albion WFC"}, away_team: {name: "Yeovil Town LFC"}, match_date: "2018-10-28"},
          {id: 19746, home_team: {name: "Everton LFC"}, away_team: {name: "West Ham United LFC"}, match_date: "2018-10-28"},
          {id: 19769, home_team: {name: "Brighton & Hove Albion WFC"}, away_team: {name: "West Ham United LFC"}, match_date: "2018-12-02"},
          {id: 19770, home_team: {name: "Manchester City WFC"}, away_team: {name: "Arsenal WFC"}, match_date: "2018-12-02"},
          {id: 19771, home_team: {name: "Birmingham City WFC"}, away_team: {name: "Yeovil Town LFC"}, match_date: "2018-12-02"},
          {id: 19772, home_team: {name: "Chelsea FCW"}, away_team: {name: "Reading WFC"}, match_date: "2018-12-02"},
          {id: 19778, home_team: {name: "Manchester City WFC"}, away_team: {name: "Birmingham City WFC"}, match_date: "2018-12-09"},
          {id: 19820, home_team: {name: "Reading WFC"}, away_team: {name: "Chelsea FCW"}, match_date: "2019-05-11"}
        ];
      }
      setMatches(mockMatches);
      if (mockMatches.length > 0) {
        setSelectedMatchId(mockMatches[0].id);
      }
    }
  };

  const fetchMatchDetails = async (matchId: number, preferredTeamId?: number) => {
    setMatchLoading(true);
    // Clear stale state to prevent displaying Match A data under Match B context
    setMatchStats(null);
    setShots([]);
    setPassingNetwork(null);

    try {
      // 1. Match Stats
      const resStats = await fetch(`${API_BASE_URL}/api/v1/matches/${matchId}/stats`);
      if (!resStats.ok) throw new Error("Stats request failed");
      const statsData = await resStats.json();
      setMatchStats(statsData);

      // 2. Shot Map
      const resShots = await fetch(`${API_BASE_URL}/api/v1/matches/${matchId}/shot-map`);
      if (!resShots.ok) throw new Error("Shots request failed");
      const shotsData = await resShots.json();
      setShots(shotsData);

      // 3. Passing Network for specific team (defaults to Home Team)
      const targetTeamId = preferredTeamId || statsData?.home_team?.id || 1;
      setPassingTeamId(targetTeamId);
      await fetchPassingNetwork(matchId, targetTeamId);
      setIsDemoMode(false);
    } catch (e) {
      setIsDemoMode(true);
      // Set dynamic mock match values matched to the selected fixture
      const currentMatch = matches.find(m => m.id === matchId);
      const homeName = currentMatch?.home_team?.name || "Arsenal";
      const awayName = currentMatch?.away_team?.name || "Chelsea";
      const homeId = currentMatch?.home_team?.id || 1;
      const awayId = currentMatch?.away_team?.id || 2;
      const targetTeamId = preferredTeamId || homeId;
      setPassingTeamId(targetTeamId);

      // Note: Shots xG sums (0.45 + 0.25 + 0.48 + 0.60 = 1.78; 0.65 + 0.29 = 0.94)
      // match home_team.xg (1.78) and away_team.xg (0.94)
      setMatchStats({
        match_id: matchId,
        home_team: { id: homeId, name: homeName, score: 2, possession: 56.4, shots: 14, shots_on_target: 6, xg: 1.78, passes: 512, pass_completion: 84.5 },
        away_team: { id: awayId, name: awayName, score: 1, possession: 43.6, shots: 9, shots_on_target: 3, xg: 0.94, passes: 384, pass_completion: 78.1 }
      });
      setShots([
        {"id": "s1", "player_name": `${homeName} Forward`, "team_id": homeId, "team_name": homeName, "minute": 14, "second": 22, "x": 108.5, "y": 32.4, "outcome": "Goal", "xg": 0.45, "body_part": "Right Foot", "under_pressure": true},
        {"id": "s2", "player_name": `${homeName} Midfielder`, "team_id": homeId, "team_name": homeName, "minute": 38, "second": 5, "x": 98.0, "y": 45.2, "outcome": "Saved", "xg": 0.25, "body_part": "Left Foot", "under_pressure": false},
        {"id": "s3", "player_name": `${awayName} Striker`, "team_id": awayId, "team_name": awayName, "minute": 44, "second": 50, "x": 114.2, "y": 38.0, "outcome": "Goal", "xg": 0.65, "body_part": "Right Foot", "under_pressure": true},
        {"id": "s4", "player_name": `${homeName} Striker`, "team_id": homeId, "team_name": homeName, "minute": 72, "second": 14, "x": 112.0, "y": 41.5, "outcome": "Goal", "xg": 0.48, "body_part": "Head", "under_pressure": false},
        {"id": "s5", "player_name": `${homeName} Winger`, "team_id": homeId, "team_name": homeName, "minute": 77, "second": 10, "x": 102.5, "y": 24.0, "outcome": "Saved", "xg": 0.60, "body_part": "Right Foot", "under_pressure": false},
        {"id": "s6", "player_name": `${awayName} Attacker`, "team_id": awayId, "team_name": awayName, "minute": 85, "second": 33, "x": 92.5, "y": 28.0, "outcome": "Off Target", "xg": 0.29, "body_part": "Left Foot", "under_pressure": true}
      ]);
      fetchMockPassingNetwork(targetTeamId, homeName, awayName, homeId, awayId);
    } finally {
      setMatchLoading(false);
    }
  };

  const handleTeamChangeForPassing = async (teamId: number) => {
    if (!selectedMatchId || teamId === passingTeamId) return;
    setPassingTeamId(teamId);
    if (!isDemoMode) {
      await fetchPassingNetwork(selectedMatchId, teamId);
    } else {
      const homeName = matchStats?.home_team?.name || "Arsenal";
      const awayName = matchStats?.away_team?.name || "Chelsea";
      const homeId = matchStats?.home_team?.id || 1;
      const awayId = matchStats?.away_team?.id || 2;
      fetchMockPassingNetwork(teamId, homeName, awayName, homeId, awayId);
    }
  };

  const fetchPassingNetwork = async (matchId: number, teamId: number) => {
    setPassingLoading(true);
    try {
      const resPass = await fetch(`${API_BASE_URL}/api/v1/matches/${matchId}/passing-network?team_id=${teamId}`);
      if (!resPass.ok) throw new Error("Pass request failed");
      const passData = await resPass.json();
      setPassingNetwork(passData);
    } catch (e) {
      const homeName = matchStats?.home_team?.name || "Arsenal";
      const awayName = matchStats?.away_team?.name || "Chelsea";
      const homeId = matchStats?.home_team?.id || 1;
      const awayId = matchStats?.away_team?.id || 2;
      fetchMockPassingNetwork(teamId, homeName, awayName, homeId, awayId);
    } finally {
      setPassingLoading(false);
    }
  };

  const fetchMockPassingNetwork = (teamId: number, homeName: string, awayName: string, homeId: number, awayId: number) => {
    const isAway = (teamId === awayId);
    const teamPrefix = isAway ? awayName : homeName;

    if (isAway) {
      setPassingNetwork({
        nodes: [
          {id: 201, name: `${teamPrefix} GK`, x: 14.0, y: 40.0, volume: 30},
          {id: 202, name: `${teamPrefix} RB`, x: 36.0, y: 70.0, volume: 44},
          {id: 203, name: `${teamPrefix} CB`, x: 32.0, y: 52.0, volume: 52},
          {id: 204, name: `${teamPrefix} CB`, x: 32.0, y: 28.0, volume: 48},
          {id: 205, name: `${teamPrefix} LB`, x: 36.0, y: 10.0, volume: 40},
          {id: 206, name: `${teamPrefix} DM`, x: 52.0, y: 46.0, volume: 56},
          {id: 207, name: `${teamPrefix} DM`, x: 54.0, y: 26.0, volume: 58},
          {id: 208, name: `${teamPrefix} RW`, x: 74.0, y: 68.0, volume: 42},
          {id: 209, name: `${teamPrefix} AM`, x: 72.0, y: 40.0, volume: 50},
          {id: 210, name: `${teamPrefix} LW`, x: 74.0, y: 12.0, volume: 38},
          {id: 211, name: `${teamPrefix} CF`, x: 92.0, y: 40.0, volume: 28}
        ],
        links: [
          {source: 201, target: 203, count: 12},
          {source: 201, target: 204, count: 10},
          {source: 203, target: 202, count: 16},
          {source: 203, target: 206, count: 18},
          {source: 204, target: 207, count: 15},
          {source: 204, target: 205, count: 14},
          {source: 202, target: 208, count: 20},
          {source: 205, target: 210, count: 17},
          {source: 206, target: 207, count: 22},
          {source: 206, target: 209, count: 19},
          {source: 207, target: 209, count: 21},
          {source: 209, target: 211, count: 16}
        ]
      });
    } else {
      setPassingNetwork({
        nodes: [
          {id: 1, name: `${teamPrefix} GK`, x: 12.0, y: 40.0, volume: 34},
          {id: 2, name: `${teamPrefix} RB`, x: 38.0, y: 68.0, volume: 48},
          {id: 3, name: `${teamPrefix} CB`, x: 34.0, y: 52.0, volume: 55},
          {id: 4, name: `${teamPrefix} CB`, x: 34.0, y: 28.0, volume: 51},
          {id: 5, name: `${teamPrefix} LB`, x: 38.0, y: 12.0, volume: 44},
          {id: 6, name: `${teamPrefix} DM`, x: 55.0, y: 48.0, volume: 58},
          {id: 7, name: `${teamPrefix} DM`, x: 58.0, y: 24.0, volume: 62},
          {id: 8, name: `${teamPrefix} AM`, x: 76.0, y: 50.0, volume: 54},
          {id: 9, name: `${teamPrefix} RW`, x: 88.0, y: 66.0, volume: 46},
          {id: 10, name: `${teamPrefix} LW`, x: 86.0, y: 14.0, volume: 42},
          {id: 11, name: `${teamPrefix} CF`, x: 95.0, y: 40.0, volume: 35}
        ],
        links: [
          {source: 1, target: 3, count: 14},
          {source: 1, target: 4, count: 12},
          {source: 3, target: 2, count: 18},
          {source: 3, target: 6, count: 22},
          {source: 4, target: 7, count: 19},
          {source: 4, target: 5, count: 15},
          {source: 2, target: 6, count: 11},
          {source: 2, target: 9, count: 25},
          {source: 5, target: 7, count: 14},
          {source: 5, target: 10, count: 18},
          {source: 6, target: 8, count: 20},
          {source: 7, target: 8, count: 15},
          {source: 8, target: 9, count: 24},
          {source: 8, target: 11, count: 17}
        ]
      });
    }
  };

  const fetchPlayers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/players`);
      if (!res.ok) throw new Error("Players request failed");
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        setPlayersList(data);
        setSelectedPlayerId(data[0].player_id);
      } else {
        throw new Error("No players found");
      }
    } catch (e) {
      const mockPlayers = [
        {player_id: 1, player_name: "Bukayo Saka"},
        {player_id: 11, player_name: "Martin Odegaard"},
        {player_id: 26, player_name: "Virgil van Dijk"}
      ];
      setPlayersList(mockPlayers);
      setSelectedPlayerId(1);
    }
  };

  const fetchPlayerSimilarity = async (playerId: number, count: number = 10) => {
    setSimilarityLoading(true);
    setSimilarityData(null);
    setSelectedMatchPlayer(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/players/${playerId}/similar?top_n=${count}`);
      if (!res.ok) throw new Error("Similarity request failed");
      const data = await res.json();
      if (data && data.similar_players && data.similar_players.length > 0) {
        setSimilarityData(data);
        setSelectedMatchPlayer(data.similar_players[0]);
      } else {
        throw new Error("No similarity data found");
      }
    } catch (e) {
      // Mock player similarity values with multiple realistic nearest neighbors
      const pName = playersList.find(p => p.player_id === playerId)?.player_name || "Bukayo Saka";
      const isSaka = pName.toLowerCase().includes("saka");
      const isVanDijk = pName.toLowerCase().includes("dijk");

      let mockMatches: MatchPlayer[] = [];
      if (isSaka) {
        mockMatches = [
          {
            player_id: 2, player_name: "Lionel Messi", similarity_score: 0.925,
            explanation: "Highly overlapping statistics in right-wing inside progression. Both generate massive progressive carries and key passes into the final third.",
            umap_x: 1.5, umap_y: 3.2,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.65, match_percentile: 94},
              {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 2.8, match_percentile: 96},
              {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 58.4, match_percentile: 91},
              {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 0.25, match_percentile: 32},
              {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 41.2, match_percentile: 92}
            ]
          },
          {
            player_id: 3, player_name: "Mohamed Salah", similarity_score: 0.895,
            explanation: "Elite wide forward profile with high box entries, direct shot volume, and transition goal threat from the right flank.",
            umap_x: 1.8, umap_y: 3.6,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.72, match_percentile: 98},
              {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 2.1, match_percentile: 88},
              {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 36.2, match_percentile: 74},
              {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 0.55, match_percentile: 45},
              {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 35.8, match_percentile: 84}
            ]
          },
          {
            player_id: 4, player_name: "Raphinha", similarity_score: 0.872,
            explanation: "Inverted winger profile creating dangerous deliveries into the half-spaces with high work rate in defensive transition.",
            umap_x: 1.3, umap_y: 2.9,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.44, match_percentile: 82},
              {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 2.5, match_percentile: 93},
              {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 40.5, match_percentile: 80},
              {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 1.25, match_percentile: 75},
              {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 32.1, match_percentile: 78}
            ]
          },
          {
            player_id: 5, player_name: "Rodrygo", similarity_score: 0.861,
            explanation: "Versatile technician excelling in 1v1 dribbles, quick combination play in tight spaces, and penalty box entries.",
            umap_x: 1.1, umap_y: 2.7,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.48, match_percentile: 85},
              {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 1.9, match_percentile: 82},
              {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 38.0, match_percentile: 76},
              {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 0.80, match_percentile: 55},
              {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 36.4, match_percentile: 86}
            ]
          },
          {
            player_id: 6, player_name: "Michael Olise", similarity_score: 0.849,
            explanation: "Creative outlet from wide areas featuring high expected assists (xA) and pinpoint crosses from deep build-up.",
            umap_x: 1.4, umap_y: 2.5,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.52, player_percentile: 88, match_value: 0.38, match_percentile: 78},
              {metric: "Key Passes Per 90", player_value: 2.2, player_percentile: 90, match_value: 2.7, match_percentile: 95},
              {metric: "Passes Per 90", player_value: 42.1, player_percentile: 82, match_value: 45.2, match_percentile: 86},
              {metric: "Tackles Per 90", player_value: 0.95, player_percentile: 62, match_value: 1.10, match_percentile: 68},
              {metric: "Carries Per 90", player_value: 38.5, player_percentile: 89, match_value: 30.2, match_percentile: 74}
            ]
          }
        ];
      } else if (isVanDijk) {
        mockMatches = [
          {
            player_id: 27, player_name: "William Saliba", similarity_score: 0.918,
            explanation: "Elite modern center-back profile. Dominant in defensive duels, press-resistant passing from the back, and sweeping recovery pace.",
            umap_x: -3.2, umap_y: -4.0,
            radar_comparison: [
              {metric: "Passes Per 90", player_value: 75.4, player_percentile: 96, match_value: 71.8, match_percentile: 94},
              {metric: "Tackles Per 90", player_value: 1.4, player_percentile: 68, match_value: 1.6, match_percentile: 74},
              {metric: "Aerial Won %", player_value: 74.2, player_percentile: 95, match_value: 68.5, match_percentile: 88},
              {metric: "Interceptions Per 90", player_value: 1.8, player_percentile: 84, match_value: 1.5, match_percentile: 78},
              {metric: "Carries Per 90", player_value: 52.0, player_percentile: 92, match_value: 48.5, match_percentile: 89}
            ]
          },
          {
            player_id: 28, player_name: "Ruben Dias", similarity_score: 0.884,
            explanation: "Commanding central defender with high volume distribution, block efficiency, and leadership in defensive organization.",
            umap_x: -3.0, umap_y: -4.3,
            radar_comparison: [
              {metric: "Passes Per 90", player_value: 75.4, player_percentile: 96, match_value: 79.2, match_percentile: 98},
              {metric: "Tackles Per 90", player_value: 1.4, player_percentile: 68, match_value: 1.3, match_percentile: 64},
              {metric: "Aerial Won %", player_value: 74.2, player_percentile: 95, match_value: 65.0, match_percentile: 82},
              {metric: "Interceptions Per 90", player_value: 1.8, player_percentile: 84, match_value: 1.4, match_percentile: 74},
              {metric: "Carries Per 90", player_value: 52.0, player_percentile: 92, match_value: 54.1, match_percentile: 94}
            ]
          },
          {
            player_id: 29, player_name: "Gabriel Magalhaes", similarity_score: 0.865,
            explanation: "Aggressive front-foot defender, physical aerial box presence, and left-sided progressive passing outlet.",
            umap_x: -3.1, umap_y: -3.8,
            radar_comparison: [
              {metric: "Passes Per 90", player_value: 75.4, player_percentile: 96, match_value: 68.4, match_percentile: 90},
              {metric: "Tackles Per 90", player_value: 1.4, player_percentile: 68, match_value: 1.7, match_percentile: 78},
              {metric: "Aerial Won %", player_value: 74.2, player_percentile: 95, match_value: 69.2, match_percentile: 90},
              {metric: "Interceptions Per 90", player_value: 1.8, player_percentile: 84, match_value: 1.2, match_percentile: 68},
              {metric: "Carries Per 90", player_value: 52.0, player_percentile: 92, match_value: 45.0, match_percentile: 85}
            ]
          }
        ];
      } else {
        // Default / Martin Odegaard Playmaker
        mockMatches = [
          {
            player_id: 12, player_name: "Kevin De Bruyne", similarity_score: 0.894,
            explanation: "Similar playmaker signatures. High density of progressive passes in the right half-spaces and key chances created.",
            umap_x: -0.5, umap_y: 2.5,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.31, player_percentile: 78, match_value: 0.38, match_percentile: 82},
              {metric: "Key Passes Per 90", player_value: 3.1, player_percentile: 94, match_value: 3.8, match_percentile: 98},
              {metric: "Passes Per 90", player_value: 62.4, player_percentile: 89, match_value: 70.2, match_percentile: 93},
              {metric: "Tackles Per 90", player_value: 1.2, player_percentile: 71, match_value: 0.8, match_percentile: 55},
              {metric: "Carries Per 90", player_value: 28.5, player_percentile: 76, match_value: 31.0, match_percentile: 80}
            ]
          },
          {
            player_id: 13, player_name: "Florian Wirtz", similarity_score: 0.875,
            explanation: "Modern advanced playmaker with dynamic half-turn reception, sharp through-balls, and defensive counter-pressing.",
            umap_x: -0.6, umap_y: 2.2,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.31, player_percentile: 78, match_value: 0.42, match_percentile: 86},
              {metric: "Key Passes Per 90", player_value: 3.1, player_percentile: 94, match_value: 2.9, match_percentile: 91},
              {metric: "Passes Per 90", player_value: 62.4, player_percentile: 89, match_value: 58.1, match_percentile: 85},
              {metric: "Tackles Per 90", player_value: 1.2, player_percentile: 71, match_value: 1.4, match_percentile: 76},
              {metric: "Carries Per 90", player_value: 28.5, player_percentile: 76, match_value: 34.5, match_percentile: 86}
            ]
          },
          {
            player_id: 14, player_name: "James Maddison", similarity_score: 0.852,
            explanation: "Attacking midfielder profile centered around set-piece delivery, shot creation from zone 14, and high key pass volume.",
            umap_x: -0.4, umap_y: 2.0,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.31, player_percentile: 78, match_value: 0.28, match_percentile: 74},
              {metric: "Key Passes Per 90", player_value: 3.1, player_percentile: 94, match_value: 2.8, match_percentile: 90},
              {metric: "Passes Per 90", player_value: 62.4, player_percentile: 89, match_value: 54.0, match_percentile: 80},
              {metric: "Tackles Per 90", player_value: 1.2, player_percentile: 71, match_value: 1.1, match_percentile: 65},
              {metric: "Carries Per 90", player_value: 28.5, player_percentile: 76, match_value: 26.2, match_percentile: 70}
            ]
          },
          {
            player_id: 15, player_name: "Bernardo Silva", similarity_score: 0.841,
            explanation: "Elite ball retention in high-pressure midfield zones, tempo control, and progressive circulation.",
            umap_x: -0.7, umap_y: 2.1,
            radar_comparison: [
              {metric: "Goals Per 90", player_value: 0.31, player_percentile: 78, match_value: 0.25, match_percentile: 70},
              {metric: "Key Passes Per 90", player_value: 3.1, player_percentile: 94, match_value: 2.4, match_percentile: 86},
              {metric: "Passes Per 90", player_value: 62.4, player_percentile: 89, match_value: 66.8, match_percentile: 92},
              {metric: "Tackles Per 90", player_value: 1.2, player_percentile: 71, match_value: 1.8, match_percentile: 82},
              {metric: "Carries Per 90", player_value: 28.5, player_percentile: 76, match_value: 36.0, match_percentile: 88}
            ]
          }
        ];
      }

      setSimilarityData({
        player_id: playerId,
        player_name: pName,
        similar_players: mockMatches
      });
      setSelectedMatchPlayer(mockMatches[0]);
    } finally {
      setSimilarityLoading(false);
    }
  };

  const triggerEtlPipeline = async () => {
    setEtlRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/etl/run`, { method: "POST" });
      if (res.ok) alert("Data Ingestion ETL pipeline started in the background. Fresh StatsBomb data will load shortly!");
    } catch (e) {
      alert("Pipeline server offline. Simulation modes are running.");
    } finally {
      setTimeout(() => setEtlRunning(false), 2000);
    }
  };

  const triggerModelRetraining = async () => {
    setTrainingRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/ml/train`, { method: "POST" });
      if (res.ok) alert("ML Model training initiated in the background! Re-evaluating xG classifications and similarity vectors.");
    } catch (e) {
      alert("Model pipeline server offline. Simulation models loaded.");
    } finally {
      setTimeout(() => setTrainingRunning(false), 2000);
    }
  };

  const loggerFallback = (msg: string) => {
    console.log(`[Tactivision Fallback]: ${msg}`);
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans">
      
      {/* Top Header Bar */}
      <header className="bg-card border-b border-border py-4 px-6 flex items-center justify-between sticky top-0 z-40 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-500 flex items-center justify-center font-black text-slate-950 text-xl shadow-lg">
            TV
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight">TactiVision AI</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold">
              Football Intelligence Platform
            </p>
          </div>
        </div>

        {/* MLOps controls */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-green-950/30 border border-green-800/40 rounded-full text-xs">
            <span className={`w-2 h-2 rounded-full ${isDemoMode ? "bg-amber-400" : "bg-green-500"} animate-pulse`}></span>
            <span className={`${isDemoMode ? "text-amber-300" : "text-green-400"} font-semibold text-[10px] uppercase`}>
              {isDemoMode ? "Demo / Simulation Mode" : "Live Service Online"}
            </span>
          </div>

          <button
            onClick={triggerEtlPipeline}
            disabled={etlRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 rounded-lg border border-border transition-colors disabled:opacity-50"
          >
            <Database className="w-3.5 h-3.5" />
            <span>{etlRunning ? "Ingesting..." : "Run ETL"}</span>
          </button>

          <button
            onClick={triggerModelRetraining}
            disabled={trainingRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-slate-950 text-xs font-bold rounded-lg transition-colors shadow disabled:opacity-50"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>{trainingRunning ? "Training..." : "Retrain ML"}</span>
          </button>
        </div>
      </header>

      {/* Main Container Layout */}
      <div className="flex-1 flex flex-col md:flex-row">
        
        {/* Navigation Sidebar */}
        <aside className="w-full md:w-60 bg-card/60 md:border-r border-border p-4 space-y-2 md:space-y-6">
          <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground px-3 hidden md:block">
            Analytics Modules
          </div>
          <nav className="flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-x-visible">
            <button
              onClick={() => setActiveTab("match")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "match" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Map className="w-4 h-4" />
              <span>Match Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab("similarity")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "similarity" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Player Similarity</span>
            </button>

            <button
              onClick={() => setActiveTab("sandbox")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "sandbox" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Crosshair className="w-4 h-4" />
              <span>xG Sandbox</span>
            </button>

            <button
              onClick={() => setActiveTab("assistant")}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-bold transition-all w-full shrink-0 ${
                activeTab === "assistant" 
                  ? "bg-green-500/10 text-green-400 border-l-2 border-green-500" 
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Bot className="w-4 h-4" />
              <span>Tactical Assistant</span>
            </button>
          </nav>
        </aside>

        {/* Content Panel */}
        <main className="flex-1 p-6 overflow-y-auto space-y-6 max-w-6xl mx-auto w-full">
          
          {/* TAB 1: MATCH DASHBOARD */}
          {activeTab === "match" && (
            <div className="space-y-6 animate-fadeIn">
              {/* Filter controls */}
              <div className="bg-card border border-border p-4 rounded-xl flex flex-wrap gap-4 items-center">
                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">Competition</label>
                  <select
                    value={selectedComp || ""}
                    onChange={(e) => setSelectedComp(e.target.value)}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none"
                  >
                    {competitions.map(c => (
                      <option key={`${c.competition_id}-${c.season_id}`} value={`${c.competition_id}-${c.season_id}`}>
                        {c.competition_name} ({c.season_name})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">MatchFixture</label>
                  <select
                    value={selectedMatchId || ""}
                    onChange={(e) => setSelectedMatchId(Number(e.target.value))}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none min-w-[200px]"
                  >
                    {matches.map(m => (
                      <option key={m.id} value={m.id}>
                        {m.home_team.name} vs {m.away_team.name} ({m.match_date})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Match Loading State */}
              {matchLoading && (
                <div className="bg-card/50 border border-border/80 rounded-xl p-12 text-center flex flex-col items-center justify-center gap-3 min-h-[300px]">
                  <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-xs font-semibold text-slate-300">Loading match statistics & shot coordinates...</p>
                </div>
              )}

              {/* Match Stats Splits */}
              {!matchLoading && matchStats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Scoreboard and general stats */}
                  <div className="md:col-span-1 bg-card border border-border p-5 rounded-xl flex flex-col justify-between shadow-md">
                    <div className="text-center space-y-2 border-b border-border/50 pb-4">
                      <div className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Match Result</div>
                      <div className="flex justify-center items-center gap-6">
                        <div>
                          <div className="text-base font-bold text-slate-200">{matchStats.home_team.name}</div>
                          <div className="text-2xl font-black text-slate-100">{matchStats.home_team.score}</div>
                        </div>
                        <div className="text-muted-foreground font-black text-lg">FT</div>
                        <div>
                          <div className="text-base font-bold text-slate-200">{matchStats.away_team.name}</div>
                          <div className="text-2xl font-black text-slate-100">{matchStats.away_team.score}</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3 pt-4 text-xs">
                      {/* Possession split */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-muted-foreground font-semibold">
                          <span>Possession</span>
                          <span>{matchStats.home_team.possession}% vs {matchStats.away_team.possession}%</span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                          <div className="bg-blue-500 h-full" style={{ width: `${matchStats.home_team.possession}%` }}></div>
                          <div className="bg-green-500 h-full flex-1"></div>
                        </div>
                      </div>

                      {/* xG split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Expected Goals (xG)</span>
                        <span className="font-bold text-slate-200">{matchStats.home_team.xg} vs {matchStats.away_team.xg}</span>
                      </div>

                      {/* Shots split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Shots (On Target)</span>
                        <span className="font-semibold text-slate-200">
                          {matchStats.home_team.shots} ({matchStats.home_team.shots_on_target}) vs {matchStats.away_team.shots} ({matchStats.away_team.shots_on_target})
                        </span>
                      </div>

                      {/* Passes split */}
                      <div className="flex justify-between py-1 border-b border-border/20">
                        <span className="text-muted-foreground">Pass Accuracy</span>
                        <span className="font-semibold text-slate-200">
                          {matchStats.home_team.pass_completion}% vs {matchStats.away_team.pass_completion}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Shot Map Visualization */}
                  <div className="md:col-span-2">
                    <ShotMap shots={shots} />
                  </div>
                </div>
              )}

              {/* Passing Network */}
              {!matchLoading && passingNetwork && (
                <div className="border border-border bg-card/25 p-5 rounded-xl">
                  <PassingNetwork 
                    nodes={passingNetwork.nodes} 
                    links={passingNetwork.links} 
                    homeTeam={matchStats?.home_team}
                    awayTeam={matchStats?.away_team}
                    selectedTeamId={passingTeamId || matchStats?.home_team?.id}
                    onSelectTeam={handleTeamChangeForPassing}
                    isLoading={passingLoading}
                  />
                </div>
              )}
            </div>
          )}

          {/* TAB 2: PLAYER SIMILARITY */}
          {activeTab === "similarity" && (
            <div className="space-y-6 animate-fadeIn">
              {/* Player search filter */}
              <div className="bg-card border border-border p-4 rounded-xl flex items-center gap-4">
                <div className="space-y-1">
                  <label className="block text-[10px] font-semibold text-muted-foreground uppercase">Target Player</label>
                  <select
                    value={selectedPlayerId || ""}
                    onChange={(e) => setSelectedPlayerId(Number(e.target.value))}
                    className="bg-background border border-border text-slate-200 text-xs p-2 rounded focus:outline-none min-w-[200px]"
                  >
                    {playersList.map(p => (
                      <option key={p.player_id} value={p.player_id}>
                        {p.player_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Similarity Loading State */}
              {similarityLoading && (
                <div className="bg-card/50 border border-border/80 rounded-xl p-12 text-center flex flex-col items-center justify-center gap-3 min-h-[350px]">
                  <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-xs font-semibold text-slate-300">Searching high-dimensional feature embeddings & finding nearest neighbors...</p>
                </div>
              )}

              {!similarityLoading && similarityData && (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  {/* Similarity List Sidebar */}
                  <div className="lg:col-span-1 bg-card border border-border rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        Nearest Neighbors
                      </h4>
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-green-500/10 text-green-400 rounded-full border border-green-500/20">
                        {similarityData.similar_players ? similarityData.similar_players.length : 0} Matches
                      </span>
                    </div>
                    <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                      {similarityData.similar_players && similarityData.similar_players.map((match: MatchPlayer) => (
                        <button
                          key={match.player_id}
                          onClick={() => setSelectedMatchPlayer(match)}
                          className={`w-full text-left p-3 rounded-lg border text-xs transition-all flex flex-col gap-1.5 ${
                            selectedMatchPlayer?.player_id === match.player_id
                              ? "bg-green-500/10 border-green-500/30 text-green-400"
                              : "bg-background/40 border-border/80 text-slate-300 hover:bg-slate-800/20"
                          }`}
                        >
                          <div className="font-bold flex justify-between items-center">
                            <span>{match.player_name}</span>
                            <span className="text-green-500 font-black">
                              {(match.similarity_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="text-[10px] text-muted-foreground line-clamp-2">
                            {match.explanation}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Radar Chart Panel */}
                  <div className="lg:col-span-3">
                    {selectedMatchPlayer ? (
                      <PlayerRadar
                        playerName={similarityData.player_name}
                        matchPlayer={selectedMatchPlayer}
                      />
                    ) : (
                      <div className="bg-card border border-border rounded-xl p-8 text-center text-xs text-muted-foreground flex items-center justify-center min-h-[350px]">
                        Select a player from the nearest neighbors list to view radar metrics comparison.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {!similarityLoading && !similarityData && (
                <div className="bg-card border border-border rounded-xl p-8 text-center text-xs text-muted-foreground flex items-center justify-center min-h-[350px]">
                  Select a player above to calculate multi-metric cosine distance and generate statistical radar charts.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: xG SIMULATOR SANDBOX */}
          {activeTab === "sandbox" && (
            <div className="animate-fadeIn">
              <XgSandbox />
            </div>
          )}

          {/* TAB 4: TACTICAL assistant */}
          {activeTab === "assistant" && (
            <div className="animate-fadeIn">
              <AssistantChat />
            </div>
          )}

        </main>
      </div>

      {/* Footer bar */}
      <footer className="bg-card border-t border-border/60 py-3.5 px-6 text-center text-[10px] text-muted-foreground flex flex-col sm:flex-row justify-between items-center gap-2 mt-auto">
        <div>
          © {new Date().getFullYear()} TactiVision AI. Serving StatsBomb Open Data schemas.
        </div>
        <div className="flex gap-4">
          <span>Explainable ML Model (XGBoost/LR)</span>
          <span>•</span>
          <span>Conversational FAISS RAG Retriever</span>
        </div>
      </footer>

    </div>
  );
}
