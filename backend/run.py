from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--https", action="store_true")
arg = parser.parse_args()

if __name__ == "__main__":
    import yaml
    import uvicorn
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    if arg.https:
        uvicorn.run(
            "main:app",
            host=config["host"],
            port=config["port"],
            reload=True,
            ssl_certfile=config["ssl_certfile"],
            ssl_keyfile=config["ssl_keyfile"],
        )
    else:
        uvicorn.run(
            "main:app",
            host=config["host"],
            port=config["port"],
            reload=True,
        )