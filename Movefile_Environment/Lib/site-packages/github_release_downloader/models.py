import dataclasses


@dataclasses.dataclass
class GitHubRepo:
    user: str
    repo: str
    token: str = ""


@dataclasses.dataclass
class ReleaseAsset:
    name: str
    url: str
    size: int

    @property
    def is_valid(self):
        return not (
            self.name is None
            or not self.name.strip(" ")
            or self.url is None
            or not self.url.strip(" ")
            or self.size is None
            or self.size <= 0
        )
