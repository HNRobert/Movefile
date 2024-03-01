import json
import logging
from pathlib import Path

from semantic_version import Version

from github_release_downloader.models import GitHubRepo


class AuthSession:
    header = dict()

    @classmethod
    def init(cls, repo: GitHubRepo):
        if cls.header or not repo.token:
            return
        cls.header = dict(Authorization=f'Bearer {repo.token}')


class Cache:
    def __init__(self, filename: str = "version.cache"):
        self._filename = Path(filename)
        self._cache = None

    @property
    def version(self):
        if self._cache is None:
            self._load()
        value = self._cache.get("version")
        return Version(value) if value else None

    @version.setter
    def version(self, value: Version):
        if self._cache is None:
            self._cache = {}
        self._cache["version"] = str(value)
        self._save()

    def _load(self):
        if not self._filename.exists() or not self._filename.is_file():
            self._save()
        try:
            with open(self._filename, "r") as file:
                self._cache = json.load(file)
        except Exception as e:
            logging.exception("Unable to load cache:", exc_info=e)
            self._save()

    def _save(self):
        with open(self._filename, "w") as file:
            json.dump(self._cache or {'version': None}, file)
