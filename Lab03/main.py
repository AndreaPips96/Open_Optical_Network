import json
import pandas as pd

f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
print(nodes_dict)

nodes_frame = pd.DataFrame.from_dict(nodes_dict)
# print('\n', nodes_frame)

# for key in nodes_dict:

