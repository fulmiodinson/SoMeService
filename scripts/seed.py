#!/usr/bin/env python3
"""Load fixtures/initial_data.json into the SoMeService database.

Must be run from the repo root so that the `app` package is importable,
or inside the running container:

    docker compose exec app python scripts/seed.py
    docker compose exec app python scripts/seed.py --fixture fixtures/initial_data.json

The script is idempotent: existing providers/accounts (matched by name /
account_id) are updated in-place rather than duplicated.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure repo root is on the path when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.some_account import SoMeAccount
from app.models.some_provider import SoMeProvider

FIXTURES_FILE = Path(__file__).parent.parent / "fixtures" / "initial_data.json"


async def upsert_provider(session: AsyncSession, data: dict) -> SoMeProvider:
    result = await session.execute(
        select(SoMeProvider).where(SoMeProvider.name == data["name"])
    )
    provider = result.scalar_one_or_none()
    if provider is None:
        provider = SoMeProvider(name=data["name"], account_url=data["account_url"])
        session.add(provider)
        await session.flush()
        print(f"  CREATED provider '{provider.name}'")
    else:
        provider.account_url = data["account_url"]
        print(f"  UPDATED provider '{provider.name}'")
    return provider


async def upsert_account(
    session: AsyncSession,
    data: dict,
    provider_map: dict[str, int],
) -> SoMeAccount | None:
    account_id = data.get("account_id", "").strip()
    if not account_id:
        print(
            f"  SKIP   account '{data['name']}' — account_id is empty. "
            "Run scripts/fetch_yt_channels.py first."
        )
        return None

    provider_id = provider_map.get(data.get("provider_name", ""))

    result = await session.execute(
        select(SoMeAccount).where(SoMeAccount.account_id == account_id)
    )
    account = result.scalar_one_or_none()
    if account is None:
        account = SoMeAccount(
            name=data["name"],
            account_id=account_id,
            description=data.get("description", ""),
            country_code=data.get("country_code", ""),
            uploads_playlist_id=data.get("uploads_playlist_id", ""),
            provider_id=provider_id,
        )
        session.add(account)
        print(f"  CREATED account '{account.name}' ({account_id})")
    else:
        account.name = data["name"]
        account.description = data.get("description", "")
        account.country_code = data.get("country_code", "")
        account.uploads_playlist_id = data.get("uploads_playlist_id", "")
        account.provider_id = provider_id
        print(f"  UPDATED account '{account.name}' ({account_id})")

    return account


async def seed(fixture_path: Path) -> None:
    with fixture_path.open() as f:
        fixture = json.load(f)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # --- Providers ---
            provider_map: dict[str, int] = {}
            for provider_data in fixture.get("providers", []):
                provider = await upsert_provider(session, provider_data)
                provider_map[provider.name] = provider.id

            # --- Accounts ---
            for account_data in fixture.get("accounts", []):
                await upsert_account(session, account_data, provider_map)

    print("\nSeeding complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database from a fixture file")
    parser.add_argument(
        "--fixture",
        default=str(FIXTURES_FILE),
        help="Path to the fixture JSON file (default: fixtures/initial_data.json)",
    )
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    if not fixture_path.exists():
        sys.exit(f"ERROR: Fixture file not found: {fixture_path}")

    asyncio.run(seed(fixture_path))


if __name__ == "__main__":
    main()
