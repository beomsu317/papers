from Patch_slicer import *
from PatchGraph_parser import *

if __name__ == '__main__':
    data_name = 'motivation_example'
    data_path = f'data/{data_name}'
    result_path = f'result/{data_name}'
    os.makedirs(f'{result_path}/graph', exist_ok=True)
    os.makedirs(f'{result_path}/segment', exist_ok=True)
    os.makedirs(f'{result_path}/patch', exist_ok=True)
    graph_meta_data_path = f'{result_path}/graph'
    pg_main(data_path, result_path)
    slicer_main(graph_meta_data_path, result_path)
