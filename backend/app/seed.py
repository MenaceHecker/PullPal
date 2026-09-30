from sqlalchemy.orm import Session

from app.models import Service

# Names and descriptions match the simulated system exactly, since ingestion
# joins on service name.
SEED_SERVICES = [
    ("checkout-service", "Handles cart checkout and order creation."),
    ("payments-service", "Talks to the payment provider and records charges."),
    ("inventory-service", "Tracks stock levels and reserves inventory for orders."),
]


def seed_services(db: Session) -> None:
    """Idempotent, safe to call on every startup."""
    existing_names = {name for (name,) in db.query(Service.name).all()}
    for name, description in SEED_SERVICES:
        if name not in existing_names:
            db.add(Service(name=name, description=description))
    db.commit()
