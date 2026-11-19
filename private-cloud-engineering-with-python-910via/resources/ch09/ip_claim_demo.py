"""IP allocation without double assignment: the database is the referee.

Two constraints on one table do the work:
  - address is the PRIMARY KEY, so one address can belong to only one VM;
  - vm_id is UNIQUE, so one VM can hold only one address.

claim_ip() is idempotent: calling it again for the same VM returns the same
address, so a retried provisioning job does not leak a second one.

Run: python ip_claim_demo.py
Standard library only. Uses an in-memory SQLite database.
"""
import ipaddress
import sqlite3

POOL = [str(ip) for ip in ipaddress.ip_network("10.20.0.0/29").hosts()]  # 6 addresses


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute(
        """
        CREATE TABLE allocations (
            address TEXT PRIMARY KEY,
            vm_id   TEXT NOT NULL UNIQUE
        )
        """
    )
    return db


def claim_ip(db: sqlite3.Connection, vm_id: str) -> str:
    """Return the address of vm_id, allocating one if it has none yet."""
    while True:
        row = db.execute(
            "SELECT address FROM allocations WHERE vm_id = ?", (vm_id,)
        ).fetchone()
        if row:
            return row[0]  # a retry of a step that already succeeded
        taken = {r[0] for r in db.execute("SELECT address FROM allocations")}
        free = next((a for a in POOL if a not in taken), None)
        if free is None:
            raise RuntimeError("address pool exhausted")
        try:
            with db:  # one transaction: commit, or roll back on an exception
                db.execute(
                    "INSERT INTO allocations (address, vm_id) VALUES (?, ?)",
                    (free, vm_id),
                )
            return free
        except sqlite3.IntegrityError:
            continue  # lost a race for that address (or for this VM): look again


def release_ip(db: sqlite3.Connection, vm_id: str) -> None:
    """Free the address of vm_id. Releasing twice is harmless."""
    with db:
        db.execute("DELETE FROM allocations WHERE vm_id = ?", (vm_id,))


def main() -> None:
    db = connect()
    print("pool:", POOL[0], "to", POOL[-1], f"({len(POOL)} addresses)")

    print("vm-1 first claim :", claim_ip(db, "vm-1"))
    print("vm-1 retry       :", claim_ip(db, "vm-1"))
    print("vm-2 first claim :", claim_ip(db, "vm-2"))

    # A worker that read the table a moment ago still believes 10.20.0.2 is free.
    try:
        with db:
            db.execute(
                "INSERT INTO allocations (address, vm_id) VALUES (?, ?)",
                ("10.20.0.2", "vm-3"),
            )
    except sqlite3.IntegrityError as exc:
        print("stale insert     :", type(exc).__name__, "-", exc)

    # The same VM asking for a second address is refused too.
    try:
        with db:
            db.execute(
                "INSERT INTO allocations (address, vm_id) VALUES (?, ?)",
                ("10.20.0.6", "vm-1"),
            )
    except sqlite3.IntegrityError as exc:
        print("second address   :", type(exc).__name__, "-", exc)

    release_ip(db, "vm-1")
    release_ip(db, "vm-1")  # idempotent: nothing left to delete
    print("vm-3 after release:", claim_ip(db, "vm-3"))

    for n in range(4, 8):
        print(f"vm-{n} claim       :", claim_ip(db, f"vm-{n}"))
    try:
        claim_ip(db, "vm-8")
    except RuntimeError as exc:
        print("vm-8 claim       :", type(exc).__name__, "-", exc)

    rows = db.execute("SELECT address, vm_id FROM allocations ORDER BY address").fetchall()
    print("final table      :", rows)


if __name__ == "__main__":
    main()
