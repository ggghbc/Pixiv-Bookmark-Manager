# Pixiv Bookmark Manager

A Python script to manage Pixiv bookmarks by changing their visibility between public and private. Supports moving all bookmarks or filtering by specific tags.

## Features

- **Change bookmark visibility** from public to private or vice versa.
- **Filter bookmarks** by a predefined list of tags (e.g., NSFW tags).
- **Process all public bookmarks** or **all private bookmarks**.
- **Automate repetitive tasks** related to bookmark privacy on Pixiv.

## Requirements

- Python 3.9+ (developed on 3.12)
- `pixivpy3` library

## Installation

1. Clone or download this repository.
2. Install the required library:

```bash
pip install pixivpy3
```

## Usage

1.  **Obtain a Refresh Token**: You need a `refresh_token` to interact with the Pixiv API. You can obtain this using tools like [get-pixivpy-token](https://github.com/eggplants/get-pixivpy-token). Follow the instructions in that repository to get your token.

2.  **Configure the Script** (Optional but Recommended):
    - Open `pixiv_bookmark_manager.py`.
    - Locate the line `REFRESH_TOKEN = ""`.
    - Replace the empty string `""` with your obtained `refresh_token` between the quotes. For example:
        ```python
        REFRESH_TOKEN = "your_actual_refresh_token_here"
        ```

3.  **Run the Script**:
    Execute the script from your terminal:

    ```bash
    python pixiv_bookmark_manager.py
    ```

    - If you configured the `REFRESH_TOKEN` variable, the script will use it automatically.
    - If `REFRESH_TOKEN` is left empty, the script will prompt you to enter the token when it starts.

4.  **Follow the On-Screen Prompts**:
    - Choose the operation:
        - `1`: Move all public bookmarks to private.
        - `2`: Move public bookmarks with specific tags to private.
        - `3`: Move all private bookmarks to public.
        - `4`: Move private bookmarks with specific tags to public.
    - The script will fetch the bookmarks based on your selection and apply the visibility change.

## Configuration

- **Tags**: The list of tags used for filtering is defined in the `DEFAULT_TAGS` variable at the beginning of the script. Modify this list to suit your needs.

## Disclaimer

This script interacts with the Pixiv API. Use it responsibly and in accordance with Pixiv's Terms of Service. Excessive or improper use might lead to temporary restrictions on your account. The author is not responsible for any consequences arising from the use of this script.

## License

This project is released under [The Unlicense](./LICENSE.txt).
