import os
import pytest
from app.services.xg_service import xg_service
from app.services.similarity_service import similarity_service
from ml.xg_model.features import extract_shot_features, calculate_distance, calculate_angle

def test_xg_inference_bounds():
    """Verify that the xG model outputs are properly bounded probabilities."""
    # Test open play foot shot from close range
    xg_close = xg_service.predict_xg(x=115.0, y=40.0, body_part="Foot", shot_type="Open Play")
    assert 0.0 <= xg_close <= 1.0
    
    # Test penalty is fixed standard xG of 0.76
    xg_penalty = xg_service.predict_xg(x=108.0, y=40.0, shot_type="Penalty")
    assert xg_penalty == 0.76
    
    # Test long range header is low probability
    xg_far_head = xg_service.predict_xg(x=75.0, y=10.0, body_part="Head", shot_type="Open Play", under_pressure=True)
    assert 0.0 <= xg_far_head < 0.15
    assert xg_far_head < xg_close

def test_feature_engineering_math():
    """Check distance and angle math calculations."""
    dist_center = calculate_distance(120.0, 40.0)
    assert dist_center == 0.0
    
    dist_far = calculate_distance(60.0, 40.0)
    assert dist_far == 60.0
    
    angle_center = calculate_angle(110.0, 40.0)
    # Right in front of goal should be wide angle
    assert angle_center > 0.6
    
    # Wide corner angle should be very small
    angle_corner = calculate_angle(115.0, 75.0)
    assert angle_corner < angle_center

def test_feature_extraction_payload():
    """Verify raw DB dict parsing mapping works."""
    shot_event = {
        "x": 105.0,
        "y": 42.0,
        "under_pressure": True,
        "detail_json": {
            "body_part": "Head",
            "technique": "Volley",
            "type": "Open Play"
        }
    }
    feats = extract_shot_features(shot_event)
    
    assert feats["is_header"] == 1
    assert feats["is_volley"] == 1
    assert feats["under_pressure"] == 1
    assert feats["is_penalty"] == 0
    assert feats["distance"] > 0

def test_similarity_neighbors():
    """Ensure similarity engine returns correct response shape and metrics."""
    # Since model is auto-initialized with mock if empty, it should have players
    players = similarity_service.get_all_players()
    assert len(players) > 0
    
    first_player = players[0]
    pid = first_player["player_id"]
    
    sim_result = similarity_service.find_similar_players(pid, top_n=2)
    assert "player_name" in sim_result
    assert "similar_players" in sim_result
    
    neighbors = sim_result["similar_players"]
    assert len(neighbors) <= 2
    for n in neighbors:
        assert "player_name" in n
        assert 0.0 <= n["similarity_score"] <= 1.0
        assert len(n["radar_comparison"]) > 0
        assert "explanation" in n


def test_mock_match_stats_xg_consistency():
    """Verify that mock shot map xG totals match the mock match stats xG summary."""
    from app.services.analytics_service import analytics_service
    
    stats = analytics_service._get_mock_match_stats(match_id=1, home_id=1, away_id=2)
    shots = analytics_service._get_mock_shot_map(match_id=1, home_id=1, away_id=2)
    
    home_shots_xg = round(sum(s["xg"] for s in shots if s["team_id"] == 1), 2)
    away_shots_xg = round(sum(s["xg"] for s in shots if s["team_id"] == 2), 2)
    
    assert home_shots_xg == stats["home_team"]["xg"], f"Expected {stats['home_team']['xg']}, got {home_shots_xg}"
    assert away_shots_xg == stats["away_team"]["xg"], f"Expected {stats['away_team']['xg']}, got {away_shots_xg}"


def test_mock_passing_network_teams_and_determinism():
    """Verify that home and away passing networks are distinct and deterministic."""
    from app.services.analytics_service import analytics_service
    
    home_net = analytics_service._get_mock_passing_network(team_id=1)
    away_net = analytics_service._get_mock_passing_network(team_id=2)
    
    # 1. Determinism: calling it twice produces identical results
    home_net_again = analytics_service._get_mock_passing_network(team_id=1)
    assert [n["volume"] for n in home_net["nodes"]] == [n["volume"] for n in home_net_again["nodes"]]
    
    # 2. Team distinction: home vs away nodes are different
    assert home_net["team_id"] == 1
    assert away_net["team_id"] == 2
    assert home_net["nodes"][0]["id"] != away_net["nodes"][0]["id"]
    assert home_net["nodes"][0]["name"] != away_net["nodes"][0]["name"]


def test_mock_touches_within_pitch_bounds():
    """Verify that touch coordinates are clipped within pitch boundaries [0-120, 0-80]."""
    from app.services.analytics_service import analytics_service
    
    touches = analytics_service._get_mock_touches()
    assert len(touches) > 0
    for t in touches:
        assert 0.0 <= t["x"] <= 120.0
        assert 0.0 <= t["y"] <= 80.0

