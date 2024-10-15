from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow requests from your frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Set allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class Edge(BaseModel):
    source: str  # Add source field to the Edge class
    target: str

class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Edge]

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

def is_dag(edges: List[Edge]) -> bool:
    # Construct adjacency list
    adj_list = {}
    in_degree = {}

    for edge in edges:
        if edge.source not in adj_list:
            adj_list[edge.source] = []
        adj_list[edge.source].append(edge.target)
        
        in_degree[edge.target] = in_degree.get(edge.target, 0) + 1
        if edge.source not in in_degree:
            in_degree[edge.source] = 0

    # Perform Kahn's algorithm for cycle detection (topological sort)
    zero_in_degree = [node for node in in_degree if in_degree[node] == 0]
    sorted_nodes = []

    while zero_in_degree:
        node = zero_in_degree.pop(0)
        sorted_nodes.append(node)
        for neighbor in adj_list.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree.append(neighbor)

    return len(sorted_nodes) == len(in_degree)

@app.post('/pipelines/parse')
def parse_pipeline(data: GraphData):
    nodes_count = len(data.nodes)
    edges_count = len(data.edges)
    is_dag_graph = is_dag(data.edges)

    return {
        'nodes': nodes_count,
        'edges': edges_count,
        'is_dag': is_dag_graph
    }
