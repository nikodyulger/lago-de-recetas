import os

SCRAPING_DIRECTORY = "../scraping"

websites = list(
    filter(
        os.path.isdir,
        [
            os.path.join(SCRAPING_DIRECTORY, f)
            for f in os.listdir(SCRAPING_DIRECTORY)
            if f not in ["common", "init_data"]
        ],
    )
)

scripts_subdirectories = list(
    filter(
        os.path.isdir,
        [
            os.path.join(SCRAPING_DIRECTORY, f)
            for f in os.listdir(SCRAPING_DIRECTORY)
            if f not in ["init_data"]
        ],
    )
)
