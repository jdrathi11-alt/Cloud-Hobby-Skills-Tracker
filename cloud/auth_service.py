"""Authentication strategy.
Local: application-issued expiring JWTs.
Cloud: prefer managed authentication such as Supabase Auth/Cognito/Identity Platform.
The browser must never receive a provider service-role/admin credential.
"""
AUTH_MODE=os.getenv('AUTH_MODE','local')
