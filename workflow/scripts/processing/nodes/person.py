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

FILE = get_source(meta_id,1)
META = get_source(meta_id,2)

def run():
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    df.rename(columns={'page':'url'},inplace=True)
    df['consent']=1
    df['email'] = df['email'].str.lower()
    df.drop_duplicates(subset=['email'],inplace=True)
    df.drop_duplicates(subset=['name'],inplace=True)


    # todo merge with meta data to get job description and orcid
    # 
    #exit()

    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (n:Person) ASSERT n.name IS UNIQUE",
        "CREATE CONSTRAINT ON (n:Person) ASSERT n.email IS UNIQUE",
        "CREATE INDEX ON :Output(consent);",
        "CREATE INDEX ON :Output(url);",
        
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    run()
