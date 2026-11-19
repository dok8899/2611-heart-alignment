from functools import lru_cache

from app.core.config import get_settings

FIREBASE_APP_NAME = "heart-alignment-api"


@lru_cache(maxsize=4)
def get_firebase_app(project_id: str | None = None):
    """Initialize one Firebase Admin app using ADC and the configured project."""
    import firebase_admin

    try:
        return firebase_admin.get_app(FIREBASE_APP_NAME)
    except ValueError:
        project_id = project_id or get_settings().google_cloud_project
        return firebase_admin.initialize_app(
            options={"projectId": project_id},
            name=FIREBASE_APP_NAME,
        )


def verify_admin_id_token(id_token: str) -> dict:
    from firebase_admin import auth

    return auth.verify_id_token(id_token, app=get_firebase_app())
