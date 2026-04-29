# SQLAlchemy — Safety

Red lines — conditions that must NEVER occur.

## NEVER share a Session across threads or async tasks

SQLAlchemy Sessions are NOT thread-safe. Each thread / async task must create its own session.

```python
# NEVER
session = Session(engine)

def worker():
    session.add(Item(name="x"))  # ❌ data race with other workers
    session.commit()

Thread(target=worker).start()
Thread(target=worker).start()

# ALWAYS: one session per thread
def worker():
    with Session(engine) as session:
        session.add(Item(name="x"))
        session.commit()
```

## NEVER catch exceptions without rolling back

After an exception in a session operation, the session is in an unusable state. All subsequent operations fail.

```python
# NEVER
try:
    session.add(user)
    session.commit()
except IntegrityError:
    session.add(log_entry)  # ❌ This also fails — session is dirty

# ALWAYS: rollback on exception
try:
    session.add(user)
    session.commit()
except IntegrityError:
    session.rollback()  # ✅ reset session state
    session.add(log_entry)
    session.commit()

# EVEN BETTER: use context manager (auto rollback on exception)
with Session(engine) as session:
    try:
        session.add(user)
        session.commit()
    except IntegrityError:
        pass  # session.__exit__ handles rollback
```

## NEVER use autocommit=True in production (2.0 style)

`autocommit=True` with `begin()` makes every individual statement auto-commit, losing transactional guarantees.

```python
# NEVER
engine = create_engine("postgresql://...", isolation_level="AUTOCOMMIT")
# ❌ No transaction boundaries — partial writes on error

# ALWAYS: explicit transaction management
engine = create_engine("postgresql://...")
with Session(engine) as session:
    session.add(user)
    session.add(profile)
    session.commit()  # atomic: both succeed or neither
```

## NEVER interpolate user input into raw SQL strings

String interpolation opens SQL injection vectors, even when you "trust" the input.

```python
# NEVER
session.execute(text(f"SELECT * FROM users WHERE name = '{user_input}'"))  # ❌ SQL injection!

# ALWAYS: bind parameters
session.execute(text("SELECT * FROM users WHERE name = :name"), {"name": user_input})

# BEST: use ORM
stmt = select(User).where(User.name == user_input)
```

## NEVER modify `mapped_column()` defaults at the instance level expecting them to apply globally

Setting defaults on the column definition sets them per-query. Mutating them at the class level affects all future instances.

```python
# NEVER
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # ❌ function evaluated at class definition time!

# ALWAYS: use callables for defaults
from datetime import datetime, timezone

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)  # ✅ evaluated per-row
    )

# OR: use server_default for DB-side default
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
```
