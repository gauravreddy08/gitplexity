import os
from pathlib import Path
from collections import deque
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import mimetypes
import json

class Tree():
    def __init__(self, root='root'):
        self.root = Path(root)
        self.nodes = []
        self.edges = []

        self.repoTree = ""

        self._build()
        self._getData()

    def _build(self):
        queue = deque([self.root])
        self.files = []

        nodeMap = dict()
        x, y = 0, 0

        while queue:
            nodePath = queue.popleft()
            if nodePath not in nodeMap:
                nodeMap[nodePath] = StreamlitFlowNode(str(nodePath), (x, y), 
                                                      {'content': f"{nodePath.name}"}, 
                                                      'default', 'right', 'right', 
                                                      draggable=True)
                x+=1
            node = nodeMap[nodePath]
            self.nodes.append(node)

            for childPath in os.listdir(nodePath):
                if childPath.startswith('.'): continue

                childPath = Path(os.path.join(nodePath, childPath))
                self.repoTree += f'\n{childPath}'

                if childPath.is_file():
                    nodeMap[childPath] = StreamlitFlowNode(str(childPath), (x, y), 
                                                           {'content': f"{childPath.name}"}, 
                                                           'default', 'left', 'left', 
                                                           draggable=True)
                else:
                    nodeMap[childPath] = StreamlitFlowNode(str(childPath), (x, y), 
                                                           {'content': f"{childPath.name}"}, 
                                                           'default', 'right', 'left',
                                                           draggable=True)
                self.nodes.append(nodeMap[childPath])
                edge = StreamlitFlowEdge("", 
                                         str(nodePath), 
                                         str(childPath), 
                                         animated=True, 
                                         marker_end={'type': 'arrow'})
                self.edges.append(edge)
                
                if childPath.is_dir():
                    queue.append(childPath)
                else:
                    self.files.append(childPath)
                x+=1

    def _getData(self):
        self.content = dict()
        for file in self.files:
            mime_type, _ = mimetypes.guess_type(file)
            if mime_type is None and str(file).endswith('.ipynb'):
                mime_type = 'application/json'
            try:
                if mime_type and mime_type.startswith('text') or mime_type == 'application/json':
                    with open(file, 'r') as f:
                        if mime_type == 'application/json':
                            json_content = json.load(f)
                            file_content = json.dumps(json_content, indent=4)
                        else:
                            file_content = f.read()
                        self.content[str(file)] = file_content
                else:
                    print(f'Skipping {file} {mime_type}')
            except Exception as e:
                pass

    
    def get(self, filepath):
        print(f"[INFO] Trying to fetch {filepath}")
        if filepath in self.content:
            return self.content[filepath]
        print(f'[ERROR] File not found. ({filepath})')
        print(self.content.keys())
        return "File Not Found. Try Again."

if __name__ == '__main__':
    tree = Tree()
    temp = 'root/folder3/code.py'
    print(tree.repoTree)
    print(tree.content)


    
    

        