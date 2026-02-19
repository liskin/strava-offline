from contextlib import contextmanager
from dataclasses import dataclass
from itertools import chain
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Tuple
from typing import Union

from typing_extensions import Protocol


class FromDict(Protocol):
    def __call__(self, data: Mapping[str, Any]) -> Mapping[str, Any]:
        pass


@dataclass(frozen=True)
class Table:
    name: str
    columns: Mapping[str, str]
    from_dict: FromDict

    def _columns(self) -> Iterable[Tuple[str, str]]:
        return chain(self.columns.items(), (('json', "TEXT"),))

    def _from_dict(self, data: Mapping[str, Any]) -> Mapping[str, Any]:
        return {'json': json.dumps(data), **self.from_dict(data)}

    def create(self, db: sqlite3.Connection) -> None:
        columns = ', '.join(f"{name} {type}" for name, type in self._columns())
        db.execute(f"CREATE TABLE IF NOT EXISTS {self.name} ({columns})")

    def migrate(self, db: sqlite3.Connection) -> None:
        for row in db.execute(f"SELECT json FROM {self.name}_old"):
            self.upsert_row(db, self._from_dict(json.loads(row['json'])))
        db.execute(f"DROP TABLE {self.name}_old")

    def prepare_migration(self, db: sqlite3.Connection) -> List[Callable]:
        # migrate table by re-syncing entries from stored raw json replies
        try:
            db.execute(f"DROP TABLE IF EXISTS {self.name}_old")
            db.execute(f"ALTER TABLE {self.name} RENAME TO {self.name}_old")
            return [self.migrate]
        except sqlite3.DatabaseError:
            return []

    def upsert_row(self, db: sqlite3.Connection, row: Mapping[str, Any]) -> None:
        keys = ', '.join(row.keys())
        placeholders = ', '.join('?' for k in row.keys())
        db.execute(
            f"INSERT OR REPLACE INTO {self.name} ({keys}) VALUES ({placeholders})",
            tuple(row.values())
        )

    def upsert(
        self,
        db: sqlite3.Connection,
        data: Iterable[Mapping[str, Any]],
        incremental: bool = False
    ):
        rows = (self._from_dict(datum) for datum in data)
        with db:  # transaction
            db.execute("BEGIN")

            old_ids = set(r['id'] for r in db.execute(f"SELECT id FROM {self.name}"))
            seen = 0
            new = 0
            deleted = 0

            for row in rows:
                logging.debug(f"{self.name}: {row['id']} {'seen' if row['id'] in old_ids else 'new'}")

                if row['id'] in old_ids:
                    old_ids.discard(row['id'])

                    seen += 1
                    if incremental and seen > 10:
                        break
                else:
                    new += 1

                self.upsert_row(db, row)

            if not incremental:
                delete = ((i,) for i in old_ids)
                db.executemany(f"DELETE FROM {self.name} WHERE id = ?", delete)
                deleted += len(old_ids)

            logging.info(f"{self.name} upsert stats: {new} new, {seen} seen, {deleted} deleted")


@dataclass(frozen=True)
class Schema:
    version: int
    tables: List[Table]

    def initialize(self, db: sqlite3.Connection) -> None:
        with db:  # transaction
            db.execute("BEGIN")

            migrations = self.prepare_migrations(db)
            for table in self.tables:
                table.create(db)
            for migration in migrations:
                migration(db)

    def prepare_migrations(self, db: sqlite3.Connection) -> List[Callable]:
        db_version = db.execute("PRAGMA user_version").fetchone()[0]
        if db_version >= self.version:
            return []

        migrations: List[Callable] = []
        for table in self.tables:
            migrations += table.prepare_migration(db)
        migrations.append(lambda db: db.execute(f"PRAGMA user_version = {self.version}"))

        return migrations


@contextmanager
def database(path: Union[str, Path], schema: Schema) -> Iterator[sqlite3.Connection]:
    if isinstance(path, Path):
        path.parent.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(path, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        schema.initialize(db)
        yield db
    finally:
        db.close()
