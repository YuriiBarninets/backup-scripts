import json
import argparse

# load configuration file
cmdArgParser = argparse.ArgumentParser()
cmdArgParser.add_argument(
    "--config_path", default="configuration.json", help="Path to JSON configuration file")
cmdArgs = cmdArgParser.parse_args()

with open(cmdArgs.config_path, 'r') as jsonConfigFile:
    configData = json.load(jsonConfigFile)

serverConfig = configData["server"]
localConfig = configData["local"]
