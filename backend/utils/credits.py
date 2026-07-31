"""
ARUA AI - Credit Refill System
Refills user credits every 24 hours (50 credits per day, max 100)
"""

import logging
from datetime import datetime, timezone, timedelta
from utils.supabase_client import supabase_query
import requests as req
import os

logger = logging.getLogger(__name__)

DAILY_REFILL = 50
MAX_CREDITS = 100


def _direct_patch(user_id, data):
    """Direct PATCH to Supabase to avoid any query-building issues."""
    url = os.getenv('SUPABASE_URL', '')
    key = os.getenv('SUPABASE_SERVICE_KEY', '')
    if not url or not key:
        return False
    try:
        r = req.patch(
            f"{url}/rest/v1/profiles?user_id=eq.{user_id}",
            json=data,
            headers={
                'apikey': key,
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            timeout=10
        )
        return r.status_code in [200, 204]
    except Exception as e:
        logger.error(f"Direct patch failed: {e}")
        return False


def check_and_refill_credits(user_id):
    """Check if 24 hours passed since last refill and add daily credits."""
    try:
        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}

        if not profile:
            return 0

        current_credits = profile.get('ai_credits', 0)

        if current_credits >= MAX_CREDITS:
            return current_credits

        last_refill_str = profile.get('last_credit_refill')
        now = datetime.now(timezone.utc)

        should_refill = False
        if not last_refill_str:
            should_refill = True
        else:
            try:
                last_refill = datetime.fromisoformat(last_refill_str.replace('Z', '+00:00'))
                if now - last_refill >= timedelta(hours=24):
                    should_refill = True
            except (ValueError, TypeError):
                should_refill = True

        if should_refill:
            new_credits = min(current_credits + DAILY_REFILL, MAX_CREDITS)
            ok = _direct_patch(user_id, {
                'ai_credits': new_credits,
                'last_credit_refill': now.isoformat()
            })
            if ok:
                logger.info(f"Refilled {new_credits - current_credits} credits for user {user_id}")
                return new_credits
            else:
                logger.warning(f"Credit refill PATCH failed for {user_id}, trying fallback...")
                try:
                    supabase_query(
                        'profiles',
                        method='PATCH',
                        data={
                            'ai_credits': new_credits,
                            'last_credit_refill': now.isoformat()
                        },
                        filters={'user_id': user_id},
                        use_service_key=True
                    )
                    logger.info(f"Refilled (fallback) {new_credits - current_credits} credits for user {user_id}")
                    return new_credits
                except Exception as e2:
                    logger.error(f"Fallback patch also failed: {e2}")

        return current_credits

    except Exception as e:
        logger.error(f"Credit refill check failed for {user_id}: {e}")
        return profile.get('ai_credits', 0) if 'profile' in dir() else 0
