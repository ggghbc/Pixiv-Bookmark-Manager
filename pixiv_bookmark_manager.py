from pixivpy3 import AppPixivAPI
import sys
import time
from urllib.parse import urlparse, parse_qs

# --- Configuration ---
DEFAULT_TAGS = [
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
    "おしり",
    "欧派",
    "マイクロビキニ",
]

REFRESH_TOKEN = ""  # Enter your token here, or leave empty to prompt user input

ACCESS_TOKEN = ""
HEADERS = {}
USER_ID = None


def authenticate_with_refresh_token(refresh_token):
    global ACCESS_TOKEN, HEADERS, USER_ID
    try:
        api = AppPixivAPI()
        auth_result = api.auth(refresh_token=refresh_token)

        if auth_result and "access_token" in auth_result:
            ACCESS_TOKEN = auth_result["access_token"]
            HEADERS = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "User-Agent": "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)",
            }
            USER_ID = api.user_id
            if USER_ID:
                print(f"Authorization successful. User ID: {USER_ID}")
                return True
            else:
                print("Failed to get user_id")
                return False
        else:
            print("Authentication did not return an access_token.")
            return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False


def get_all_illust_ids_public(target_tags=None):
    """Fetches all public illustration IDs, optionally filtered by tags."""
    global USER_ID
    if USER_ID is None:
        print("Error: USER_ID is not set. Check authentication.")
        return []

    illust_ids = []
    restrict = "public"
    max_bookmark_id = None
    total_processed = 0

    while True:
        try:
            # Fetching bookmarks
            api = AppPixivAPI()
            api.access_token = ACCESS_TOKEN

            json_result = api.user_bookmarks_illust(
                user_id=USER_ID, restrict=restrict, max_bookmark_id=max_bookmark_id
            )

            if not json_result or "illusts" not in json_result:
                print(
                    f"Warning: unexpected API response structure at max_bookmark_id {max_bookmark_id}. Stopping."
                )
                break

            illusts_batch = json_result["illusts"]

            if not illusts_batch:
                print("No more public bookmarks.")
                break

            # Filter illustrations based on tags if a list is provided
            if target_tags:
                filtered_batch = []
                for illust in illusts_batch:
                    illust_tags = [tag["name"] for tag in illust.get("tags", [])]
                    if any(
                        tag_name.lower() in [t.lower() for t in illust_tags]
                        for tag_name in target_tags
                    ):
                        filtered_batch.append(illust)
                illusts_batch = filtered_batch

            batch_ids = [illust["id"] for illust in illusts_batch]
            illust_ids.extend(batch_ids)
            total_processed += len(illusts_batch)

            # Get the next max_bookmark_id for pagination
            next_url = json_result.get("next_url")
            if next_url:
                # Parse the max_bookmark_id from the URL
                parsed = urlparse(next_url)
                params = parse_qs(parsed.query)
                max_bookmark_id_str = params.get("max_bookmark_id", [None])[0]
                max_bookmark_id = (
                    int(max_bookmark_id_str) if max_bookmark_id_str else None
                )
            else:
                max_bookmark_id = None  # No more pages

            print(
                f"Retrieved {len(batch_ids)} public bookmarks matching criteria. Total processed: {total_processed}"
            )

            if not max_bookmark_id:  # No more pages for current restrict type
                break

            # Add delay to avoid rate limits
            time.sleep(1)

        except Exception as e:
            print(
                f"Error fetching public bookmarks at max_bookmark_id {max_bookmark_id}: {e}"
            )
            break

    return illust_ids


def get_all_illust_ids_private(target_tags=None):
    """Fetches all private illustration IDs, optionally filtered by tags."""
    global USER_ID
    if USER_ID is None:
        print("Error: USER_ID is not set. Check authentication.")
        return []

    illust_ids = []
    restrict = "private"
    max_bookmark_id = None
    total_processed = 0

    while True:
        try:
            # Fetching bookmarks
            api = AppPixivAPI()
            api.access_token = ACCESS_TOKEN

            json_result = api.user_bookmarks_illust(
                user_id=USER_ID, restrict=restrict, max_bookmark_id=max_bookmark_id
            )

            if not json_result or "illusts" not in json_result:
                print(
                    f"Warning: unexpected API response structure at max_bookmark_id {max_bookmark_id}. Stopping."
                )
                break

            illusts_batch = json_result["illusts"]

            if not illusts_batch:
                print("No more private bookmarks.")
                break

            # Filter illustrations based on tags if a list is provided
            if target_tags:
                filtered_batch = []
                for illust in illusts_batch:
                    illust_tags = [tag["name"] for tag in illust.get("tags", [])]
                    if any(
                        tag_name.lower() in [t.lower() for t in illust_tags]
                        for tag_name in target_tags
                    ):
                        filtered_batch.append(illust)
                illusts_batch = filtered_batch

            batch_ids = [illust["id"] for illust in illusts_batch]
            illust_ids.extend(batch_ids)
            total_processed += len(illusts_batch)

            # Get the next max_bookmark_id for pagination
            next_url = json_result.get("next_url")
            if next_url:
                # Parse the max_bookmark_id from the URL
                parsed = urlparse(next_url)
                params = parse_qs(parsed.query)
                max_bookmark_id_str = params.get("max_bookmark_id", [None])[0]
                max_bookmark_id = (
                    int(max_bookmark_id_str) if max_bookmark_id_str else None
                )
            else:
                max_bookmark_id = None  # No more pages

            print(
                f"Retrieved {len(batch_ids)} private bookmarks matching criteria. Total processed: {total_processed}"
            )

            if not max_bookmark_id:  # No more pages for current restrict type
                break

            # Add delay to avoid rate limits
            time.sleep(1)

        except Exception as e:
            print(
                f"Error fetching private bookmarks at max_bookmark_id {max_bookmark_id}: {e}"
            )
            break

    return illust_ids


def change_bookmark_visibility_to_private(illust_ids):
    """Changes visibility of bookmarks to private for a list of illustration IDs."""
    api = AppPixivAPI()
    api.access_token = ACCESS_TOKEN

    success_count = 0
    fail_list = []
    total_illusts = len(illust_ids)

    print(
        f"\nStarting to change visibility to 'private' for {total_illusts} illustrations..."
    )

    for i, illust_id in enumerate(illust_ids):
        try:
            # Re-add bookmark with restrict='private' - this updates the existing one
            result = api.illust_bookmark_add(illust_id=illust_id, restrict="private")

            success_count += 1

        except Exception as e:
            fail_list.append(illust_id)
            print(f"  - Error changing visibility for ID {illust_id}: {e}")

        # Print progress every 10 items
        if (i + 1) % 10 == 0 or (i + 1) == total_illusts:
            print(
                f"  Progress: {i+1}/{total_illusts} ({success_count} success, {len(fail_list)} errors)"
            )

        # Rate limit safety
        time.sleep(1)

    print(f"\n--- Summary ---")
    print(f"Total illustrations processed: {total_illusts}")
    print(f"Successfully changed: {success_count}")
    print(f"Failed to change: {len(fail_list)}")
    if fail_list:
        print(f"Failed IDs: {fail_list[:10]}{'...' if len(fail_list) > 10 else ''}")


def change_bookmark_visibility_to_public(illust_ids):
    """Changes visibility of bookmarks to public for a list of illustration IDs."""
    api = AppPixivAPI()
    api.access_token = ACCESS_TOKEN

    success_count = 0
    fail_list = []
    total_illusts = len(illust_ids)

    print(
        f"\nStarting to change visibility to 'public' for {total_illusts} illustrations..."
    )

    for i, illust_id in enumerate(illust_ids):
        try:
            # Re-add bookmark with restrict='public' - this updates the existing one
            result = api.illust_bookmark_add(illust_id=illust_id, restrict="public")

            success_count += 1

        except Exception as e:
            fail_list.append(illust_id)
            print(f"  - Error changing visibility for ID {illust_id}: {e}")

        # Print progress every 10 items
        if (i + 1) % 10 == 0 or (i + 1) == total_illusts:
            print(
                f"  Progress: {i+1}/{total_illusts} ({success_count} success, {len(fail_list)} errors)"
            )

        # Rate limit safety
        time.sleep(1)

    print(f"\n--- Summary ---")
    print(f"Total illustrations processed: {total_illusts}")
    print(f"Successfully changed: {success_count}")
    print(f"Failed to change: {len(fail_list)}")
    if fail_list:
        print(f"Failed IDs: {fail_list[:10]}{'...' if len(fail_list) > 10 else ''}")


def get_refresh_token_interactive():
    """Prompts user for refresh token if settings are empty."""
    if REFRESH_TOKEN:
        print("Using refresh token from settings.")
        return REFRESH_TOKEN
    else:
        refresh_token = input("Enter your refresh_token: ").strip()
        if not refresh_token:
            print("Refresh token not provided. Exiting.")
            sys.exit(1)
        return refresh_token


def main():
    print("\n--- Pixiv Bookmark Manager  ---")

    refresh_token = get_refresh_token_interactive()

    if not authenticate_with_refresh_token(refresh_token):
        print("Failed to authenticate. Exiting.")
        sys.exit(1)

    scope_choice = input(
        "\nWork with bookmarks:\n1. All public -> private\n2. Public with tags -> private\n3. All private -> public\n4. Private with tags -> public\nEnter choice (1, 2, 3, or 4): "
    ).strip()

    target_tags = None
    illust_ids = []
    direction = ""

    if scope_choice == "1":
        print("Selected: All public bookmarks -> private.")
        illust_ids = get_all_illust_ids_public(target_tags=None)
        direction = "public_to_private"
    elif scope_choice == "2":
        target_tags = DEFAULT_TAGS
        print(f"Selected: Public bookmarks with tags -> private. Tags: {target_tags}")
        illust_ids = get_all_illust_ids_public(target_tags=target_tags)
        direction = "public_to_private"
    elif scope_choice == "3":
        print("Selected: All private bookmarks -> public.")
        illust_ids = get_all_illust_ids_private(target_tags=None)
        direction = "private_to_public"
    elif scope_choice == "4":
        target_tags = DEFAULT_TAGS
        print(f"Selected: Private bookmarks with tags -> public. Tags: {target_tags}")
        illust_ids = get_all_illust_ids_private(target_tags=target_tags)
        direction = "private_to_public"
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    if not illust_ids:
        print("\nNo illustrations found matching the criteria. Exiting.")
        return

    print(f"\nFound {len(illust_ids)} illustrations to move.")

    if direction == "public_to_private":
        change_bookmark_visibility_to_private(illust_ids)
    elif direction == "private_to_public":
        change_bookmark_visibility_to_public(illust_ids)
    else:
        print("Internal error: unknown movement direction.")


if __name__ == "__main__":
    main()
