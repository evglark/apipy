from apipy.auth.security import hash_password

fake_credentials_db = [{"user_id": 1, "password_hash": hash_password("password123")}]
refresh_tokens_db: list[dict] = []
token_blacklist: set[str] = set()
login_attempts_db: dict[str, dict] = {}
ip_rate_limit_db: dict[str, list[int]] = {}
security_events_db: list[dict] = []
