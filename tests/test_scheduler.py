import pytest
from datetime import datetime
from main import get_scheduled_timeframes

def test_get_scheduled_timeframes_multiple():
    # 2026-06-01 is Monday (Weekly) and 1st of month (Monthly)
    # 2026-06-01 is also the start of June (Yearly if set to June)
    test_date = datetime(2026, 6, 1)
    
    schedule = {
        "reports": {
            "daily": {"enabled": True},
            "weekly": {"enabled": True, "target_day": "Monday"},
            "monthly": {"enabled": True, "target_day": 1},
            "yearly": {"enabled": True, "month": 6}
        }
    }
    
    result = get_scheduled_timeframes(schedule, today=test_date)
    assert "daily" in result
    assert "weekly" in result
    assert "monthly" in result
    assert "yearly" in result
    assert len(result) == 4

def test_get_scheduled_timeframes_daily_only():
    test_date = datetime(2026, 6, 2) # Tuesday
    schedule = {
        "reports": {
            "daily": {"enabled": True},
            "weekly": {"enabled": True, "target_day": "Monday"},
            "monthly": {"enabled": True, "target_day": 1}
        }
    }
    
    result = get_scheduled_timeframes(schedule, today=test_date)
    assert result == ["daily"]

def test_get_scheduled_timeframes_weekly():
    test_date = datetime(2026, 6, 8) # Monday
    schedule = {
        "reports": {
            "daily": {"enabled": True},
            "weekly": {"enabled": True, "target_day": "Monday"},
            "monthly": {"enabled": True, "target_day": 1}
        }
    }
    
    result = get_scheduled_timeframes(schedule, today=test_date)
    assert "daily" in result
    assert "weekly" in result
    assert "monthly" not in result
    assert len(result) == 2

def test_get_scheduled_timeframes_quarterly():
    # April 1st is usually a quarterly start
    test_date = datetime(2026, 4, 1)
    schedule = {
        "reports": {
            "daily": {"enabled": True},
            "monthly": {"enabled": True, "target_day": 1},
            "quarterly": {"enabled": True, "months": [1, 4, 7, 10]}
        }
    }
    
    result = get_scheduled_timeframes(schedule, today=test_date)
    assert "daily" in result
    assert "monthly" in result
    assert "quarterly" in result
    assert len(result) == 3
