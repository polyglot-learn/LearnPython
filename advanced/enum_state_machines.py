"""State machines with Enum: making illegal transitions unrepresentable.

A status field typed `str` accepts "shiped" without complaint. An Enum member
does not exist unless you defined it, and the set of legal transitions can be
declared as data rather than scattered across if-statements.

The pattern below has three parts: an Enum of states, a table of allowed
transitions, and a machine that consults the table. Adding a state means adding
a member and a table row — no control flow changes — and an illegal transition
raises at the point it is attempted, with both states named in the message.

`match` over the enum handles the per-state behaviour, and a total match (no
`case _`) makes a forgotten state visible.
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class State(Enum):
    DRAFT = auto()
    SUBMITTED = auto()
    APPROVED = auto()
    REJECTED = auto()
    PUBLISHED = auto()


class Event(Enum):
    SUBMIT = auto()
    APPROVE = auto()
    REJECT = auto()
    PUBLISH = auto()
    WITHDRAW = auto()


TRANSITIONS: dict[tuple[State, Event], State] = {
    (State.DRAFT, Event.SUBMIT): State.SUBMITTED,
    (State.SUBMITTED, Event.APPROVE): State.APPROVED,
    (State.SUBMITTED, Event.REJECT): State.REJECTED,
    (State.SUBMITTED, Event.WITHDRAW): State.DRAFT,
    (State.REJECTED, Event.SUBMIT): State.SUBMITTED,
    (State.APPROVED, Event.PUBLISH): State.PUBLISHED,
}


class IllegalTransition(Exception):
    pass


@dataclass
class Document:
    title: str
    state: State = State.DRAFT
    history: list[str] = field(default_factory=list)

    def apply(self, event: Event) -> State:
        try:
            new_state = TRANSITIONS[(self.state, event)]
        except KeyError:
            raise IllegalTransition(
                f"cannot {event.name} from {self.state.name}"
            ) from None
        self.history.append(f"{self.state.name} --{event.name}--> {new_state.name}")
        self.state = new_state
        return new_state

    def allowed_events(self) -> list[Event]:
        return [event for (state, event) in TRANSITIONS if state == self.state]

    def describe(self) -> str:
        match self.state:  # no `case _`: a new state would show up as a gap
            case State.DRAFT:
                return "still being written"
            case State.SUBMITTED:
                return "waiting on a reviewer"
            case State.APPROVED:
                return "cleared, not yet live"
            case State.REJECTED:
                return "sent back for changes"
            case State.PUBLISHED:
                return "live"


def main() -> None:
    doc = Document("Quarterly report")
    print(f"start: {doc.state.name} — {doc.describe()}")
    print(f"allowed now: {[e.name for e in doc.allowed_events()]}")

    for event in (Event.SUBMIT, Event.REJECT, Event.SUBMIT, Event.APPROVE, Event.PUBLISH):
        state = doc.apply(event)
        print(f"  {event.name:<9} -> {state.name:<10} ({doc.describe()})")

    print("history:")
    for line in doc.history:
        print(f"  {line}")

    print("illegal transitions raise, naming both states:")
    for event in (Event.SUBMIT, Event.WITHDRAW):
        try:
            doc.apply(event)
        except IllegalTransition as exc:
            print(f"  {exc}")

    print("the table is the specification:")
    reachable = {state for state, _ in TRANSITIONS} | set(TRANSITIONS.values())
    print(f"  states in the table: {sorted(s.name for s in reachable)}")
    print(f"  terminal states: "
          f"{sorted(s.name for s in State if s not in {st for st, _ in TRANSITIONS})}")
    print(f"  transitions defined: {len(TRANSITIONS)} of "
          f"{len(State) * len(Event)} possible pairs")


if __name__ == "__main__":
    main()
