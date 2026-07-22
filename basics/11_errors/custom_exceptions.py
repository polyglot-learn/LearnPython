"""Custom exception hierarchies — and the modern extras.

Give a package one base exception and derive the specific ones from it. Callers
can then catch narrowly (`except InsufficientFunds`) or broadly
(`except BankError`) without ever resorting to `except Exception`.

Carry structured data on the exception, not just a message string: the handler
usually wants the values, not a sentence to re-parse.

3.11 added two facilities used below: `exc.add_note()` for extra context, and
`ExceptionGroup` / `except*` for reporting several failures at once.
"""


class BankError(Exception):
    """Base class for everything this module raises."""


class AccountNotFound(BankError):
    def __init__(self, account_id: str) -> None:
        super().__init__(f"no account {account_id!r}")
        self.account_id = account_id


class InsufficientFunds(BankError):
    def __init__(self, balance: float, requested: float) -> None:
        super().__init__(f"balance {balance} is less than requested {requested}")
        self.balance = balance
        self.requested = requested

    @property
    def shortfall(self) -> float:
        return self.requested - self.balance


ACCOUNTS = {"alice": 100.0}


def withdraw(account_id: str, amount: float) -> float:
    if account_id not in ACCOUNTS:
        raise AccountNotFound(account_id)
    balance = ACCOUNTS[account_id]
    if amount > balance:
        error = InsufficientFunds(balance, amount)
        error.add_note(f"account {account_id!r} last seen with {balance}")
        raise error
    ACCOUNTS[account_id] = balance - amount
    return ACCOUNTS[account_id]


def validate(record: dict[str, str]) -> None:
    """Report *every* problem at once instead of stopping at the first."""
    problems: list[Exception] = []
    if "name" not in record:
        problems.append(ValueError("name is required"))
    if not record.get("email", "").count("@"):
        problems.append(ValueError("email is malformed"))
    if problems:
        raise ExceptionGroup("record is invalid", problems)


def main() -> None:
    print(f"withdraw 30 -> balance {withdraw('alice', 30)}")

    try:
        withdraw("bob", 10)
    except AccountNotFound as exc:
        print(f"AccountNotFound for {exc.account_id!r}: {exc}")

    try:
        withdraw("alice", 500)
    except InsufficientFunds as exc:
        print(f"InsufficientFunds: short by {exc.shortfall}")
        print(f"  notes: {exc.__notes__}")

    # The base class catches every error the module defines.
    for account, amount in (("bob", 1), ("alice", 999)):
        try:
            withdraw(account, amount)
        except BankError as exc:
            print(f"handled as BankError: {type(exc).__name__}")

    # except* unpacks an ExceptionGroup by type.
    try:
        validate({"email": "nope"})
    except* ValueError as group:
        for exc in group.exceptions:
            print(f"validation: {exc}")


if __name__ == "__main__":
    main()
