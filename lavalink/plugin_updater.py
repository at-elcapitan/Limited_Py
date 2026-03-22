import requests
from ruamel.yaml import YAML

APPLICATION_YAML = "application.yml"
API_BASE = "https://api.github.com/repos"
LATEST_RELEASE_PATH = "/releases/latest"
PLUGINS = [
    {
        "repo": "lavalink-devs/youtube-source",
        "dependency_prefix": "dev.lavalink.youtube:youtube-plugin",
    },
]


def get_latest_version(repo: str) -> str | None:
    url = f"{API_BASE}/{repo}{LATEST_RELEASE_PATH}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.HTTPError as e:
        print(f"[ERROR] Failed to fetch {repo}: {e}")
        return None

    data = r.json()
    return data["tag_name"].lstrip("v")


def update_yaml(plugins: list) -> None:
    yaml = YAML()

    try:
        with open(APPLICATION_YAML) as f:
            data = yaml.load(f)
    except Exception as e:
        print(f"[ERROR] Cannot read YAML: {e}")
        return

    updated = False

    for plugin in data.get("lavalink", {}).get("plugins", []):
        if "dependency" not in plugin:
            continue

        for conf in plugins:
            prefix = conf["dependency_prefix"]

            if prefix not in plugin["dependency"]:
                continue

            repo = conf["repo"]
            latest = get_latest_version(repo)

            if latest is None:
                print(f"Unable to get latest for {repo}, skipping")
                continue

            current_version = plugin["dependency"].split(":")[-1]

            if current_version != latest:
                new_dependency = f"{prefix}:{latest}"
                plugin["dependency"] = new_dependency
                updated = True

                print(f"Updating {prefix}: {current_version} -> {latest}")
                continue
            
            print(f"Skipping {prefix}: already at {latest}")

    if not updated:
        return
    
    try:
        with open(APPLICATION_YAML, "w") as f:
            yaml.dump(data, f)

        print(f"{APPLICATION_YAML} updated")
    except Exception as e:
        print(f"Cannot write {APPLICATION_YAML}: {e}")


if __name__ == "__main__":
    print("Starting update")

    update_yaml(PLUGINS)

    print("Done!")