import os
import re
import gzip
import json
import sys
import pandas as pd

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup, get_source

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup
args, dataDir = setup()
meta_id = args.name

# args = the argparse arguments (name and data)
# dataDir = the path to the working directory for this node/rel

#######################################################################

FILE = get_source(meta_id, 1)


def run():
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    df.drop(columns=["name"], inplace=True)
    df.rename(
        columns={"org-url": "id", "org-name": "name", "org-type": "type"}, inplace=True
    )
    df = df[["id", "name", "type"]]
    df.drop_duplicates(subset=["id"], inplace=True)
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (n:Org) ASSERT n.id IS UNIQUE",
        "CREATE CONSTRAINT ON (n:Org) ASSERT n.name IS UNIQUE",
        "CREATE INDEX ON :Org(type);",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    run()
