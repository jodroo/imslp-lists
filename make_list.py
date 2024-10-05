"""Convert CSV to IMSLP Composer Composition List"""

import re
import sys
from typing import Union
import pandas as pd
import strictyaml  # type: ignore


TABLE_ROW_TEMPLATE = """
| {id}
| {title}
| {key}
| {date}
| {genre}
| {notes}
"""

PAGE_FOOTER = """\
|}
"""


def format_catalogue_number(n: Union[int, str]) -> str:
    """Formats the catalogue number with leading zeros."""
    lit = ""
    if isinstance(n, str):
        m = re.match(r"([0-9]+)(.?)", n)
        if m is None:
            raise ValueError("Wrong catalogue number format.")
        n = int(m[1])
        lit = m[2]
    if n < 10:
        return f"{{{{Hs|00}}}}{n}{lit}"
    if n < 100:
        return f"{{{{Hs|0}}}}{n}{lit}"
    return f"{n}{lit}"


def format_title(title_imslp: str,
                 title: str,
                 composer_imslp: str,
                 default_composer_imslp: str) -> str:
    """Adds a link to the work page (if available)."""
    if pd.isna(composer_imslp):
        composer_imslp = default_composer_imslp
    if pd.isna(title_imslp):
        return title
    return f"{{{{LinkWorkN|{title_imslp}||{composer_imslp}|0}}}}"


def format_key(key: str) -> str:
    """Converts sharps and flats."""
    key = re.sub(r"-flat", "{{flat}}", key)
    key = re.sub(r"-sharp", "{{sharp}}", key)
    return key

def format_date(date: Union[str, pd.Timestamp]) -> str:
    """Formats the date in ISO 8601 format."""
    if isinstance(date, pd.Timestamp):
        return date.strftime("%Y-%m-%d")
    return date

def main() -> None:
    """Main function."""
    list_name = sys.argv[1]

    try:
        works = pd.read_csv(f"data/{list_name}.csv")
        with open(f"config/{list_name}.yaml", encoding="utf8") as f:
            config = strictyaml.load(f.read()).data
    except IndexError:
        print("Error: No list specified.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Unknown list '{list_name}'.")
        sys.exit(1)

    table_rows = [
        TABLE_ROW_TEMPLATE.format(
            id=format_catalogue_number(work.id),  # type: ignore[attr-defined]
            title=format_title(
                work.title_imslp,  # type: ignore[attr-defined]
                work.title,  # type: ignore[attr-defined]
                work.composer_imslp,  # type: ignore[attr-defined]
                config["composer_imslp"]
            ),
            key=format_key(work.key),  # type: ignore[attr-defined]
            date=format_date(work.date),  # type: ignore[attr-defined]
            genre=work.genre,  # type: ignore[attr-defined]
            notes="" if pd.isna(work.notes) else work.notes  # type: ignore[attr-defined]
        )
        for work in works.itertuples()
    ]

    with open(f"output/{list_name}.txt", "w", encoding="utf8") as f:
        f.write(config["page_header"].rstrip("\n"))
        f.write("|-".join(table_rows))
        f.write(PAGE_FOOTER)
        print(f"Successfully wrote IMSLP list for '{list_name}'.")

if __name__ == "__main__":
    main()
