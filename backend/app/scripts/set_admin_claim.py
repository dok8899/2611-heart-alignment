"""Grant the Firebase custom claim used to protect CRM routes."""

import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("uid", help="Firebase Auth UID of the operator")
    args = parser.parse_args()

    import firebase_admin.auth as firebase_auth

    from app.core.firebase import get_firebase_app

    app = get_firebase_app()
    user = firebase_auth.get_user(args.uid, app=app)
    claims = user.custom_claims or {}
    claims["admin"] = True
    firebase_auth.set_custom_user_claims(args.uid, claims, app=app)
    print(f"Granted admin claim to Firebase Auth UID: {args.uid}")


if __name__ == "__main__":
    main()
