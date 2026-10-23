"""Object models for the library inventory system."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


class LibraryItem(ABC):
    """Abstract base for inventory items that can be loaned."""

    def __init__(self, item_id, title, price, loan_period_days, daily_late_fee):
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("item_id must be a non-empty string.")
        self.__item_id = item_id.strip()
        self.title = title
        self.price = price
        self.__loan_period_days = self._validate_integer(
            loan_period_days, "loan_period_days", allow_zero=True
        )
        self.__daily_late_fee = self._validate_money(
            daily_late_fee, "daily_late_fee"
        )
        self.__borrow_date = None

    @staticmethod
    def _validate_integer(value, field_name, allow_zero=False):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{field_name} must be an integer.")
        minimum = 0 if allow_zero else 1
        if value < minimum:
            qualifier = "zero or greater" if allow_zero else "greater than zero"
            raise ValueError(f"{field_name} must be {qualifier}.")
        return value

    @staticmethod
    def _validate_money(value, field_name):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"{field_name} must be a valid decimal amount.") from error
        if not amount.is_finite() or amount < 0:
            raise ValueError(f"{field_name} must be finite and non-negative.")
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_date(value, field_name):
        if value is None:
            return date.today()
        if not isinstance(value, date) or isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a datetime.date value.")
        return value

    @property
    def item_id(self):
        return self.__item_id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("title must be a non-empty string.")
        self.__title = value.strip()

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        self.__price = self._validate_money(value, "price")

    @property
    def loan_period_days(self):
        return self.__loan_period_days

    @property
    def daily_late_fee(self):
        return self.__daily_late_fee

    @property
    def borrow_date(self):
        return self.__borrow_date

    @borrow_date.setter
    def borrow_date(self, value):
        if value is not None:
            value = self._validate_date(value, "borrow_date")
        self.__borrow_date = value

    @property
    def is_available(self):
        return self.__borrow_date is None

    def checkout(self, checkout_date=None):
        """Mark this item as checked out on a calendar date."""
        if not self.is_available:
            raise ValueError(f"Item {self.item_id} is already checked out.")
        self.borrow_date = self._validate_date(checkout_date, "checkout_date")

    def _validated_return_date(self, return_date):
        return_date = self._validate_date(return_date, "return_date")
        if self.borrow_date is not None and return_date < self.borrow_date:
            raise ValueError("return_date cannot be earlier than borrow_date.")
        return return_date

    def _calculate_overdue_fee(self, return_date=None):
        if self.borrow_date is None:
            return Decimal("0.00")
        checked_in_date = self._validated_return_date(return_date)
        elapsed_days = (checked_in_date - self.borrow_date).days
        overdue_days = max(0, elapsed_days - self.loan_period_days)
        return (self.daily_late_fee * overdue_days).quantize(Decimal("0.01"))

    @abstractmethod
    def calculate_fee(self, return_date=None):
        """Calculate the late fee for the item at the given return date."""

    @abstractmethod
    def display_metadata(self):
        """Return item details in a report-friendly mapping."""

    @abstractmethod
    def __len__(self):
        """Return the item's natural size (pages or duration in seconds)."""

    def _base_metadata(self):
        return {
            "item_id": self.item_id,
            "type": type(self).__name__,
            "title": self.title,
            "price": self.price,
            "available": self.is_available,
            "borrow_date": self.borrow_date,
            "loan_period_days": self.loan_period_days,
            "daily_late_fee": self.daily_late_fee,
        }

    def __str__(self):
        availability = "available" if self.is_available else "checked out"
        return f"{type(self).__name__} [{self.item_id}] {self.title} ({availability})"

    def __repr__(self):
        return (
            f"{type(self).__name__}(item_id={self.item_id!r}, "
            f"title={self.title!r}, price={self.price!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return type(self) is type(other) and self.item_id == other.item_id


class Book(LibraryItem):
    """A printed book, measured by page count."""

    def __init__(
        self,
        item_id,
        title,
        author,
        page_count,
        price,
        loan_period_days=21,
        daily_late_fee="0.25",
    ):
        super().__init__(item_id, title, price, loan_period_days, daily_late_fee)
        if not isinstance(author, str) or not author.strip():
            raise ValueError("author must be a non-empty string.")
        self.__author = author.strip()
        self.__page_count = self._validate_integer(page_count, "page_count")

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("author must be a non-empty string.")
        self.__author = value.strip()

    @property
    def page_count(self):
        return self.__page_count

    @page_count.setter
    def page_count(self, value):
        self.__page_count = self._validate_integer(value, "page_count")

    def calculate_fee(self, return_date=None):
        return self._calculate_overdue_fee(return_date)

    def display_metadata(self):
        return {**self._base_metadata(), "author": self.author, "page_count": self.page_count}

    def __len__(self):
        return self.page_count


class Magazine(LibraryItem):
    """A magazine issue, measured by page count."""

    def __init__(
        self,
        item_id,
        title,
        issue_number,
        page_count,
        price,
        loan_period_days=7,
        daily_late_fee="0.50",
    ):
        super().__init__(item_id, title, price, loan_period_days, daily_late_fee)
        if not isinstance(issue_number, str) or not issue_number.strip():
            raise ValueError("issue_number must be a non-empty string.")
        self.__issue_number = issue_number.strip()
        self.__page_count = self._validate_integer(page_count, "page_count")

    @property
    def issue_number(self):
        return self.__issue_number

    @issue_number.setter
    def issue_number(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("issue_number must be a non-empty string.")
        self.__issue_number = value.strip()

    @property
    def page_count(self):
        return self.__page_count

    @page_count.setter
    def page_count(self, value):
        self.__page_count = self._validate_integer(value, "page_count")

    def calculate_fee(self, return_date=None):
        return self._calculate_overdue_fee(return_date)

    def display_metadata(self):
        return {
            **self._base_metadata(),
            "issue_number": self.issue_number,
            "page_count": self.page_count,
        }

    def __len__(self):
        return self.page_count


class DigitalMedia(LibraryItem):
    """A digital asset, measured by duration in seconds and never fined."""

    def __init__(
        self,
        item_id,
        title,
        media_format,
        duration_seconds,
        price,
        loan_period_days=7,
    ):
        super().__init__(item_id, title, price, loan_period_days, "0.00")
        if not isinstance(media_format, str) or not media_format.strip():
            raise ValueError("media_format must be a non-empty string.")
        self.__media_format = media_format.strip().lower()
        self.__duration_seconds = self._validate_integer(
            duration_seconds, "duration_seconds"
        )

    @property
    def media_format(self):
        return self.__media_format

    @media_format.setter
    def media_format(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("media_format must be a non-empty string.")
        self.__media_format = value.strip().lower()

    @property
    def duration_seconds(self):
        return self.__duration_seconds

    @duration_seconds.setter
    def duration_seconds(self, value):
        self.__duration_seconds = self._validate_integer(
            value, "duration_seconds"
        )

    def calculate_fee(self, return_date=None):
        self._validated_return_date(return_date)
        return Decimal("0.00")

    def display_metadata(self):
        return {
            **self._base_metadata(),
            "media_format": self.media_format,
            "duration_seconds": self.duration_seconds,
        }

    def __len__(self):
        return self.duration_seconds