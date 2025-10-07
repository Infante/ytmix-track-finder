from setuptools import setup, find_packages

setup(
    name="ytmix-track-finder",
    version="0.1.0",
    author="Roberto Infante",
    author_email="hello@robertoinfante.com",
    description="Identifies songs from a YouTube video using Shazam",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Infante/ytmix-track-finder",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "yt-dlp>=2023.3.4",
        "shazamio>=0.4.0",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "yt-mix=ytmix_track_finder.cli:main",
        ],
    },
)