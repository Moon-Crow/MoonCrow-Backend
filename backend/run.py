if __name__ == "__main__":
    import yaml
    import uvicorn
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        reload=True,
        ssl_certfile=config["ssl_certfile"],
        ssl_keyfile=config["ssl_keyfile"],
    )
