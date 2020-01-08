import yaml


def extract_metadata(tar):
    metadata = None
    for member in tar.getmembers():
        if member.name.lower() == "metadata.yaml" or member.name.lower() == "metadata.yml":
            metadata = tar.extractfile(member.name)
    if metadata is None:
        return None
    return yaml.load(metadata.read())

def extract_play(tar):
    play = None
    for member in tar.getmembers():
        if member.name.lower() == "play.yaml" or member.name.lower() == "play.yml":
            play = tar.extractfile(member.name)
    if play is None:
        return None
    return play.read()


