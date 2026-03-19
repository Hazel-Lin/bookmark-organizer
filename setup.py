from setuptools import find_packages, setup


setup(
    name="bookmark-organizer",
    version="0.1.0",
    description="Analyze and reorganize browser bookmarks with safe plans and dry runs.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
            "bookmark-organizer=bookmark_organizer.cli:main",
        ]
    },
)
