import os
from src import create_stream

env = os.environ.get("ASGARD_ENV") or "production"

stream = create_stream(
    environment= env,
    configs_path= os.path.abspath("./src/configs"),
    schemas_path= os.path.abspath("./src/schemas")
)

if __name__ == "__main__":
    stream()