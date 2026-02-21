import sys
import time
import logging
from urllib.parse import urlparse, parse_qs
from typing import Literal, Optional, Set, Union
from pixivpy3 import AppPixivAPI

# --- Configuration ---
REFRESH_TOKEN = ""  # Enter your token here, or leave empty to prompt user input

DEFAULT_TAGS: Set[str] = {
    "R-18",
    "nsfw",
    "ecchi",
    "ero",
    "hentai",
    "sex",
    "nude",
    "uncensored",
    "oppai",
    "yuri",
    "yaoi",
    "BBC",
    "巨乳化",
    "爆乳",
    "尻",
    "ぱんつ",
    "おしри",
    "欧派",
    "マイクロビキニ",
}

# logging settings
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bookmarks' types
RestrictType = Literal["public", "private", ""]

UserIdType = Optional[Union[int, str]]


class PixivBookmarkManager:
    def __init__(self, refresh_token: Optional[str] = None):
        self.api = AppPixivAPI()
        self.refresh_token = refresh_token
        self.user_id: UserIdType = None
        self._authenticated = False

    def authenticate(self) -> bool:
        """Performs authentication and maintains state."""
        try:
            auth_result = self.api.auth(refresh_token=self.refresh_token)

            if auth_result and "access_token" in auth_result:
                self.user_id = self.api.user_id
                self._authenticated = True
                logger.info(f"Authorization successful. User ID: {self.user_id}")
                return True
            else:
                logger.error("Authentication did not return an access_token.")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def fetch_bookmark_ids(
        self, restrict: RestrictType = "public", target_tags: Optional[Set[str]] = None
    ) -> list[int]:
        """Gets illustration IDs from paginated bookmarks."""
        if self.user_id is None:
            logger.error("User ID is not set. Authenticate first.")
            return []

        illust_ids: list[int] = []
        max_bookmark_id: Optional[int] = None
        total_processed = 0

        target_tags_lower = {t.lower() for t in target_tags} if target_tags else None

        logger.info(f"Fetching {restrict} bookmarks...")

        while True:
            try:
                # type: ignore[arg-type]
                json_result = self.api.user_bookmarks_illust(
                    user_id=self.user_id,
                    restrict=restrict,
                    max_bookmark_id=max_bookmark_id,
                )

                if not json_result or "illusts" not in json_result:
                    logger.warning("Unexpected API response structure. Stopping.")
                    break

                illusts_batch = json_result["illusts"]
                if not illusts_batch:
                    logger.info(f"No more {restrict} bookmarks.")
                    break

                if target_tags_lower:
                    filtered_batch = []
                    for illust in illusts_batch:
                        illust_tags = {
                            tag["name"].lower() for tag in illust.get("tags", [])
                        }
                        if illust_tags & target_tags_lower:
                            filtered_batch.append(illust)
                    illusts_batch = filtered_batch

                batch_ids = [illust["id"] for illust in illusts_batch]
                illust_ids.extend(batch_ids)
                total_processed += len(batch_ids)

                logger.info(
                    f"Retrieved {len(batch_ids)} items. Total: {total_processed}"
                )

                next_url = json_result.get("next_url")
                if next_url:
                    parsed = urlparse(next_url)
                    params = parse_qs(parsed.query)
                    max_bookmark_id_str = params.get("max_bookmark_id", [None])[0]
                    max_bookmark_id = (
                        int(max_bookmark_id_str) if max_bookmark_id_str else None
                    )
                else:
                    break

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error fetching bookmarks: {e}")
                break

        return illust_ids

    def update_bookmark_visibility(
        self, illust_ids: list[int], restrict: RestrictType
    ) -> None:
        """Changes the visibility of bookmarks."""
        if not self._authenticated:
            logger.error("Not authenticated.")
            return

        success_count = 0
        fail_list: list[int] = []
        total_illusts = len(illust_ids)

        logger.info(
            f"Starting to change visibility to '{restrict}' for {total_illusts} illustrations..."
        )

        for i, illust_id in enumerate(illust_ids):
            try:
                # type: ignore[arg-type]
                self.api.illust_bookmark_add(illust_id=illust_id, restrict=restrict)
                success_count += 1
            except Exception as e:
                fail_list.append(illust_id)
                logger.warning(f"Error changing visibility for ID {illust_id}: {e}")

            if (i + 1) % 10 == 0 or (i + 1) == total_illusts:
                logger.info(
                    f"Progress: {i+1}/{total_illusts} (Success: {success_count}, Errors: {len(fail_list)})"
                )

            time.sleep(0.5)

        logger.info("--- Summary ---")
        logger.info(f"Total processed: {total_illusts}")
        logger.info(f"Successfully changed: {success_count}")
        logger.info(f"Failed: {len(fail_list)}")
        if fail_list:
            logger.warning(f"Failed IDs (first 10): {fail_list[:10]}")


def get_refresh_token_interactive(saved_token: Optional[str]) -> str:
    if saved_token:
        logger.info("Using refresh token from settings.")
        return saved_token
    else:
        token = input("Enter your refresh_token: ").strip()
        if not token:
            logger.error("Refresh token not provided. Exiting.")
            sys.exit(1)
        return token


def main() -> None:
    print("\n--- Pixiv Bookmark Manager ---")
    refresh_token = get_refresh_token_interactive(REFRESH_TOKEN)

    manager = PixivBookmarkManager(refresh_token=refresh_token)

    if not manager.authenticate():
        logger.error("Failed to authenticate. Exiting.")
        sys.exit(1)

    scope_choice = input(
        "\nWork with bookmarks:\n"
        "1. All public -> private\n"
        "2. Public with tags -> private\n"
        "3. All private -> public\n"
        "4. Private with tags -> public\n"
        "Enter choice (1, 2, 3, or 4): "
    ).strip()

    target_tags: Optional[Set[str]] = None
    restrict_fetch: RestrictType = "public"
    restrict_set: RestrictType = "private"
    direction = ""

    if scope_choice == "1":
        direction = "move"
    elif scope_choice == "2":
        target_tags = DEFAULT_TAGS
        direction = "move"
    elif scope_choice == "3":
        restrict_fetch = "private"
        restrict_set = "public"
        direction = "move"
    elif scope_choice == "4":
        restrict_fetch = "private"
        restrict_set = "public"
        target_tags = DEFAULT_TAGS
        direction = "move"
    else:
        logger.error("Invalid choice. Exiting.")
        sys.exit(1)

    logger.info(f"Fetching {restrict_fetch} bookmarks...")
    illust_ids = manager.fetch_bookmark_ids(
        restrict=restrict_fetch, target_tags=target_tags
    )

    if not illust_ids:
        logger.info("No illustrations found matching the criteria. Exiting.")
        return

    logger.info(f"Found {len(illust_ids)} illustrations to process.")
    manager.update_bookmark_visibility(illust_ids, restrict=restrict_set)


if __name__ == "__main__":
    main()
