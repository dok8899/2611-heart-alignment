from app.core.config import get_settings
from app.db.store import build_document_store


def seed_synthetic_data(store=None) -> None:
    """Insert one non-personal, repeatable sample document."""
    if store is None:
        settings = get_settings()
        store = build_document_store(
            settings.data_store_backend,
            project=settings.google_cloud_project,
            database=settings.firestore_database,
            emulator_host=settings.firestore_emulator_host,
        )
    collection = "phase1_demo_records"
    document_id = "synthetic-sample"
    if store.get(collection, document_id) is None:
        store.set(
            collection,
            document_id,
            {
                "label": "Phase 1 synthetic sample",
                "note": "Synthetic development data only; contains no personal information.",
            },
        )


if __name__ == "__main__":
    seed_synthetic_data()
