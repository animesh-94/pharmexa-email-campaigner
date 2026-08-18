import csv
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models import Subscriber

def process_subscriber_csv(db: Session, file_content: str) -> Tuple[int, int]:
    """
    Parses a CSV string, ignores duplicates in the DB, and adds new subscribers.
    Assumes columns: email, first_name (optional), tags (optional)
    Returns: (inserted_count, skipped_count)
    """
    reader = csv.DictReader(file_content.splitlines())
    
    # Normalize field names to lower case
    if not reader.fieldnames:
        return 0, 0
    
    fieldnames = [f.strip().lower() for f in reader.fieldnames]
    reader.fieldnames = fieldnames

    if 'email' not in fieldnames:
        raise ValueError("CSV must contain an 'email' column")

    inserted = 0
    skipped = 0
    batch_size = 500
    subscribers_to_add = []

    # Get existing emails to avoid constraint violations efficiently
    existing_emails = {row[0] for row in db.query(Subscriber.email).all()}

    for row in reader:
        email = row.get('email', '').strip().lower()
        if not email:
            continue
            
        if email in existing_emails:
            skipped += 1
            continue

        first_name = row.get('first_name', '').strip()
        tags = row.get('tags', '').strip()

        subscribers_to_add.append(
            Subscriber(
                email=email,
                first_name=first_name if first_name else None,
                tags=tags if tags else None,
                is_active=True
            )
        )
        existing_emails.add(email) # to handle duplicates within the CSV itself

        if len(subscribers_to_add) >= batch_size:
            db.bulk_save_objects(subscribers_to_add)
            db.commit()
            inserted += len(subscribers_to_add)
            subscribers_to_add = []

    if subscribers_to_add:
        db.bulk_save_objects(subscribers_to_add)
        db.commit()
        inserted += len(subscribers_to_add)

    return inserted, skipped
