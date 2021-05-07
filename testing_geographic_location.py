import pandas as pd
import numpy as np
import json
from pprint import pprint
import glob
from Tweet import Tweet

input_path = "../../data/external/tweet_json_200/"
file_list = glob.glob(input_path+"*.json")


screen_name = "BusinessRecord"

json_path =f"../../data/external/tweet_json_200/{screen_name}_200.json"
out_path = f"../../data/external/tweet_text_TEST/"
text_path =f"../../data/external/tweets/tweet_text_TEST/{screen_name}_200.json"


## an example of a tweet that has geographic location: https://twitter.com/theolafmess/status/1188501857825673217


for file in file_list:
    with open(file) as f:
        data = json.load(f)
    for x in data:
        if x['geo']:
            print(file)
            pprint(x)
            print("\n\n---\n")
            break

