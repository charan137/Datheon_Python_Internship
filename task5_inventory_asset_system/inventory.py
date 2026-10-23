"""Inventory operations, checkout workflows, and audit reporting."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from threading import RLock

from models import Book, DigitalMedia, LibraryItem, Magazine


@dataclass(frozen=True)
class AuditRecord:
    """An immutable record of one inventory operation."""

    occurred_at: datetime
    action: str
    item_id: str
    title: str
    fee: Decimal
    details: str


class InventoryManager:
    """Manage library items and retain an in-memory audit trail."""

    def __init__(self, items=()):
        self.__items = {}
        self.__audit_log = []
        self.__lock = RLock()
        for item in items:
            self.add_item(item)

    @property
    def items(self):
        """Return an immutable snapshot sorted by item ID."""
        with self.__lock:
            return tuple(self.__items[item_id] for item_id in sorted(self.__items))

    @property
    def audit_log(self):
        """Return an immutable snapshot of the audit events."""
        with self.__lock:
            return tuple(self.__audit_log)

    def _get_item(self, item_id):
        try:
            return self.__items[item_id]
        except KeyError as error:
            raise KeyError(f"Unknown inventory item: {item_id}") from error

    def _record(self, action, item, fee=Decimal("0.00"), details=""):
        self.__audit_log.append(
            AuditRecord(
                occurred_at=datetime.now(timezone.utc),
                action=action,
                item_id=item.item_id,
                title=item.title,
                fee=fee,
                details=details,
            )
        )

    def add_item(self, item):
        """Add a library item, rejecting duplicate IDs and other object types."""
        if not isinstance(item, LibraryItem):
            raise TypeError("item must be an instance of LibraryItem.")
        with self.__lock:
            if item.item_id in self.__items:
                raise ValueError(f"An item with ID {item.item_id!r} already exists.")
            self.__items[item.item_id] = item
            self._record("ADD", item, details="Added to inventory")
        return item

    def get_item(self, item_id):
        """Return an item by ID."""
        with self.__lock:
            return self._get_item(item_id)

    def remove_item(self, item_id):
        """Remove an available item and return it."""
        with self.__lock:
            item = self._get_item(item_id)
            if not item.is_available:
                raise ValueError(f"Cannot remove checked-out item {item_id!r}.")
            del self.__items[item_id]
            self._record("REMOVE", item, details="Removed from inventory")
            return item

    def checkout(self, item_id, checkout_date=None):
        """Check out an available item and return the item."""
        with self.__lock:
            item = self._get_item(item_id)
            item.checkout(checkout_date)
            self._record(
                "CHECKOUT",
                item,
                details=f"Borrowed on {item.borrow_date.isoformat()}",
            )
            return item

    def return_item(self, item_id, return_date=None):
        """Return an item, record its fee, and return that Decimal fee."""
        with self.__lock:
            item = self._get_item(item_id)
            if item.is_available:
                raise ValueError(f"Item {item_id!r} is not checked out.")

            effective_date = item._validated_return_date(return_date)
            fee = item.calculate_fee(effective_date)
            borrowed_date = item.borrow_date
            item.borrow_date = None
            self._record(
                "RETURN",
                item,
                fee=fee,
                details=(
                    f"Borrowed {borrowed_date.isoformat()}, "
                    f"returned {effective_date.isoformat()}"
                ),
            )
            return fee

    def available_items(self):
        """Return the available items as an immutable tuple."""
        with self.__lock:
            return tuple(
                item for item in self.items if item.is_available
            )

    def generate_inventory_report(self):
        """Build a text table containing polymorphic metadata for all items."""
        with self.__lock:
            rows = []
            for item in self.items:
                metadata = item.display_metadata()
                rows.append(
                    (
                        metadata["item_id"],
                        metadata["type"],
                        metadata["title"],
                        "Available" if metadata["available"] else "Checked out",
                        f"${metadata['price']:,.2f}",
                        str(len(item)),
                    )
                )
        if not rows:
            return "Inventory is empty."
        return self._format_table(
            ("ID", "Type", "Title", "Status", "Price", "Size"), rows
        )

    def generate_audit_report(self):
        """Build a text table of add, remove, checkout, and return events."""
        with self.__lock:
            records = tuple(self.__audit_log)
        if not records:
            return "No audit events recorded."

        rows = [
            (
                record.occurred_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                record.action,
                record.item_id,
                record.title,
                f"${record.fee:,.2f}",
                record.details,
            )
            for record in records
        ]
        return self._format_table(
            ("Timestamp", "Action", "ID", "Title", "Fee", "Details"), rows
        )

    @staticmethod
    def _format_table(headers, rows):
        widths = [
            max(len(header), *(len(str(row[index])) for row in rows))
            for index, header in enumerate(headers)
        ]
        header_line = " | ".join(
            header.ljust(widths[index]) for index, header in enumerate(headers)
        )
        divider = "-+-".join("-" * width for width in widths)
        data_lines = [
            " | ".join(
                str(value).ljust(widths[index]) for index, value in enumerate(row)
            )
            for row in rows
        ]
        return "\n".join((header_line, divider, *data_lines))

    def __len__(self):
        with self.__lock:
            return len(self.__items)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item_or_id):
        with self.__lock:
            if isinstance(item_or_id, LibraryItem):
                stored = self.__items.get(item_or_id.item_id)
                return stored == item_or_id
            return item_or_id in self.__items

    def __getitem__(self, item_id):
        return self.get_item(item_id)

    def __str__(self):
        return f"InventoryManager({len(self)} items)"

    def __repr__(self):
        return f"InventoryManager(item_count={len(self)})"


def main():
    """Run a small example showing polymorphic reports and loan fees."""
    today = date.today()
    inventory = InventoryManager(
        (
            Book("BK-100", "Python Patterns", "A. Developer", 320, "34.95"),
            Magazine("MG-210", "Science Weekly", "Vol. 12, Issue 4", 64, "8.50"),
            DigitalMedia("DM-050", "Data Structures Course", "mp4", 5400, "0.00"),
        )
    )
    inventory.checkout("BK-100", today - timedelta(days=24))
    inventory.return_item("BK-100", today)
    inventory.checkout("DM-050", today)

    print("INVENTORY")
    print(inventory.generate_inventory_report())
    print("\nAUDIT LOG")
    print(inventory.generate_audit_report())


if __name__ == "__main__":
    main()