from collections import defaultdict
import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def packPath(path):
    output = []
    x = 0
    while x < len(path):
        if(path[x] == "_"):
            output.append(path[x+3:len(path)])
            break
        
        output.append(path[x])
        x += 1
    return output

class buildTrie:
    trie = nx.DiGraph()
    
    
    def __init__(self, filename):
        paths = self.readPathsFromFile(filename)
        self.trie = self.prefix_tree(paths)
    
    
    def getTrie(self):
        return self.trie
    
    
    def readPathsFromFile(self,filename = ""):
        """The method reads from a file, the content of which is all the paths of a trie. Appends all those paths into a list and returns the list.
        
        Returns:
            pathList (list): List of all possible paths
        """
        f = open(self.textExtensionCheck(filename), "r")
        pathList = []  
        for i in f:
            tempPath = ""
            index = 1
            if(len(i.strip()) == 0):
                continue
            
            while(i[index] != "]"):
                if(i[index] == ','):
                    index += 1
                tempPath += i[index]
                index += 1
                
            tempPath = tempPath + i[index+1:len(i)-1]
            tempPath = tempPath.replace(" ", "")
            pathList.append(tempPath)
        return pathList


    def textExtensionCheck(self, filename):
        if (filename.__contains__(".txt")):
            return filename
        else:
            return filename+".txt"
        
    # Taken from networkx prefix_tree source code.
    def prefix_tree(self, paths):
        """Creates a directed prefix tree from a list of paths.

        Usually the paths are described as strings or lists of integers.

        A "prefix tree" represents the prefix structure of the strings.
        Each node represents a prefix of some string. The root represents
        the empty prefix with children for the single letter prefixes which
        in turn have children for each double letter prefix starting with
        the single letter corresponding to the parent node, and so on.

        More generally the prefixes do not need to be strings. A prefix refers
        to the start of a sequence. The root has children for each one element
        prefix and they have children for each two element prefix that starts
        with the one element sequence of the parent, and so on.

        Note that this implementation uses integer nodes with an attribute.
        Each node has an attribute "source" whose value is the original element
        of the path to which this node corresponds. For example, suppose `paths`
        consists of one path: "can". Then the nodes `[1, 2, 3]` which represent
        this path have "source" values "c", "a" and "n".

        All the descendants of a node have a common prefix in the sequence/path
        associated with that node. From the returned tree, the prefix for each
        node can be constructed by traversing the tree up to the root and
        accumulating the "source" values along the way.

        The root node is always `0` and has "source" attribute `None`.
        The root is the only node with in-degree zero.
        The nil node is always `-1` and has "source" attribute `"NIL"`.
        The nil node is the only node with out-degree zero.


        Parameters
        ----------
        paths: iterable of paths
            An iterable of paths which are themselves sequences.
            Matching prefixes among these sequences are identified with
            nodes of the prefix tree. One leaf of the tree is associated
            with each path. (Identical paths are associated with the same
            leaf of the tree.)


        Returns
        -------
        tree: DiGraph
            A directed graph representing an arborescence consisting of the
            prefix tree generated by `paths`. Nodes are directed "downward",
            from parent to child. A special "synthetic" root node is added
            to be the parent of the first node in each path. A special
            "synthetic" leaf node, the "nil" node `-1`, is added to be the child
            of all nodes representing the last element in a path. (The
            addition of this nil node technically makes this not an
            arborescence but a directed acyclic graph; removing the nil node
            makes it an arborescence.)


        Notes
        -----
        The prefix tree is also known as a *trie*.


        Examples
        --------
        Create a prefix tree from a list of strings with common prefixes::

            >>> paths = ["ab", "abs", "ad"]
            >>> T = nx.prefix_tree(paths)
            >>> list(T.edges)
            [(0, 1), (1, 2), (1, 4), (2, -1), (2, 3), (3, -1), (4, -1)]

        The leaf nodes can be obtained as predecessors of the nil node::

            >>> root, NIL = 0, -1
            >>> list(T.predecessors(NIL))
            [2, 3, 4]

        To recover the original paths that generated the prefix tree,
        traverse up the tree from the node `-1` to the node `0`::

            >>> recovered = []
            >>> for v in T.predecessors(NIL):
            ...     prefix = ""
            ...     while v != root:
            ...         prefix = str(T.nodes[v]["source"]) + prefix
            ...         v = next(T.predecessors(v))  # only one predecessor
            ...     recovered.append(prefix)
            >>> sorted(recovered)
            ['ab', 'abs', 'ad']
        """
        def get_children(parent, paths):
            children = defaultdict(list)
            # Populate dictionary with key(s) as the child/children of the root and
            # value(s) as the remaining paths of the corresponding child/children
            count = 0
            while(count < len(paths)):
                path = paths[count]
                # If path is empty, we add an edge to the NIL node.
                if not path:
                    tree.add_edge(parent, NIL)
                    count += 1
                    continue
                child = path[0]
                rest = packPath(path[1:])
                # `child` may exist as the head of more than one path in `paths`.
                children[child].append(rest) 
                count += 1
            return children

        # Initialize the prefix tree with a root node and a nil node.
        tree = nx.DiGraph()
        root = 0
        tree.add_node(root, source="Null")
        NIL = -1
        tree.add_node(NIL, source="NIL")
        children = get_children(root, paths)   
        stack = [(root, iter(children.items()))]
        while stack:
            count = 0
            parent, remaining_children = stack[-1]
            try:
                child, remaining_paths = next(remaining_children)
            # Pop item off stack if there are no remaining children
            except StopIteration:
                stack.pop()
                continue
            # We relabel each child with an unused name.
            new_name = len(tree) - 1
            # The "source" node attribute stores the original node name.
            
            tree.add_node(new_name, source=child)
            tree.add_edge(parent, new_name)
            children = get_children(new_name, remaining_paths)
            stack.append((new_name, iter(children.items())))
            count += 1
        return tree



class displayTrie():    
    def __init__(self, trie):
        self.traceFigure(trie)
        
        
    def hierarchy_pos(self, G, root, width = 1, vert_gap = 0.2, vert_loc = 0, xcenter = 0.5 ):
        '''If there is a cycle that is reachable from root, then result will not be a hierarchy.

        G: the graph
        root: the root node of current branch
        width: horizontal space allocated for this branch - avoids overlap with other branches
        vert_gap: gap between levels of hierarchy
        vert_loc: vertical location of root
        xcenter: horizontal location of root
        '''
        def h_recur(G, root, width, vert_gap, vert_loc, xcenter, pos = None, parent = None, parsed = []):      
            if(root not in parsed):
                parsed.append(root)
                if pos == None:
                    pos = {root:(xcenter,vert_loc)}
                else:
                    pos[root] = (xcenter, vert_loc)
                neighbors = list(G.neighbors(root))
                if len(neighbors)!=0:
                    dx = width/len(list(neighbors))
                    nextx = xcenter - width/2 - dx/2
                    for neighbor in neighbors:
                        nextx += dx
                        pos = h_recur(G,neighbor, width = dx, vert_gap = vert_gap,
                                            vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos,
                                            parent = root, parsed = parsed)
            return pos
        return h_recur(G, root, width, vert_gap, vert_loc, xcenter)


    def makeAnnotations(self, G, pos, text=None, color='black', size=15):
            """Goes through each vertex and label them accordingly. text (array) parameter needs to be in preorder.
            
            Args:
                pos (dict): A dictionary containing the xy-coordinates of each Vertex in the graph.  
                text (list): An array of lables as strings. Array length is equal to the number of vertices. Defaults to None.
                color (string): A hex string (e.g. '#ff0000') or\n       
                                        - An rgb/rgba string (e.g. 'rgb(255,0,0)')           
                                        - An hsl/hsla string (e.g. 'hsl(0,100%,50%)')     
                                        - An hsv/hsva string (e.g. 'hsv(0,100%,100%)')     
                                        - A named CSS color: Defaults to 'white'.\n
                size (int): Size of font. Defaults to 15.

            Returns:
                annotations (list): Array of string, which represents annotations.
            """
            annotations = []
            for k in G.nodes:
                annotations.append(dict(
                text=self.switchLabelling(G, k, text),
                x=pos[k][0], y=pos[k][1],
                xref='x1', yref='y1',
                font=dict(color=color, size=size),
                showarrow=False
            ))
            return annotations


    def switchLabelling(self, G, label, labelArray):
        """Helper function to handle logic to switch between different labels.
        \nArgs:
            label (any): String or integer.
            labelArray (list): Array of labels.

        Returns:
            Any: return either an element in G.nodes or an element in the array of labels.
        """          
        if labelArray == G.nodes or labelArray == None:
            return label
        else:
            return labelArray[label]


    def extractLabels(self ,G = nx.DiGraph()):
        list = []
        for i in range(G.order()):
            list.append(G.nodes[i]['source'])
            
        return list


    def adjustNodeSize(nodeCount):
        size = 30
        if(nodeCount <= 16):
            return size
        
        if(nodeCount >= 200):
            size = 5
            return size
        
        size = nodeCount * 0.0257
        return size


    def traceFigure(self, G):
        G.remove_node(-1)
        trieLabels = self.extractLabels(G)

        pos = self.hierarchy_pos(G, 0, width=10, vert_gap=0.1)
        nx.draw_networkx(G, pos, with_labels=True, node_size = 500, arrows=False, width=3)
                
        ##################################
        #--------EDGE INFORMATION--------#
        ##################################
        edge_x = []
        for (n0, n1) in G.edges:
            for x in (pos[n0][0], pos[n1][0], None):
                edge_x.append(x)

        edge_y = []
        for (n0, n1) in G.edges:
            for y in (pos[n0][1], pos[n1][1], None):
                edge_y.append(y)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='rgb(0,0,0)'),
            hoverinfo='none',
            mode='lines')

        ##################################
        #--------NODE INFORMATION--------#
        ##################################
        node_x = []
        node_y = []

        for node in G.nodes():
            x,y = pos[node]

            node_x.append(x)
            node_y.append(y)
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(color='rgb(0,0,0)',
                size=35),
                line_width=2)

        #############################
        #--------DRAW FIGURE--------#
        #############################
        fig = go.Figure(
                    data=[edge_trace, node_trace],
                    layout=go.Layout(annotations=self.makeAnnotations(G, pos, trieLabels, 'white', 15),
                                    showlegend = False,
                                    xaxis=dict(showgrid=True, zeroline=True, showticklabels=False),
                                    yaxis=dict(showgrid=True, zeroline=True, showticklabels=False,))
                )

        config = {'scrollZoom': True, 
                        'displaylogo': False,
                        'modeBarButtonsToRemove':['lasso2d']}
        
        fig.show(renderer="browser", config=config)


#####################################################################################################
##-------------------------------------------CLIENT CODE-------------------------------------------##
#####################################################################################################

trie = buildTrie("somePaths").getTrie()
displayTrie(trie)
