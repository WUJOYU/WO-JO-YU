import json
from pathlib import Path

from django.db import transaction
from herbarium.models import Taxon, CollectingEvent

data_path = Path.cwd() / "render_approved_records.json"
records = json.loads(data_path.read_text(encoding="utf-8-sig"))

expected_fields = {
    "taxon__family",
    "taxon__scientific_name",
    "collecting_number",
}

assert len(records) == 10, "Expected exactly 10 approved records."
assert all(
    isinstance(record, dict)
    and set(record) == expected_fields
    and all(isinstance(value, str) and value.strip() for value in record.values())
    for record in records
), "Invalid approved record."

with transaction.atomic():
    for index, record in enumerate(records, start=1):
        taxon, _ = Taxon.objects.get_or_create(
            family=record["taxon__family"],
            scientific_name=record["taxon__scientific_name"],
            defaults={"publication_status": "approved"},
        )
        if taxon.publication_status != "approved":
            taxon.publication_status = "approved"
            taxon.save(update_fields=["publication_status"])

        CollectingEvent.objects.update_or_create(
            source_identifier=f"TCF-RENDER-DEMO-{index:03d}",
            defaults={
                "taxon": taxon,
                "collecting_number": record["collecting_number"],
                "is_public": True,
            },
        )

assert Taxon.objects.count() == 9, "Unexpected taxon count."
assert CollectingEvent.objects.count() == 10, "Unexpected event count."

print("SUCCESS: 9 taxa and 10 approved records initialized.")
