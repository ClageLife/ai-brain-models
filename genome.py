# Import libraries

from calendar import c
from enum import Enum
from random import random, choice


# Init a global counter


class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return self.count

    def reset(self):
        self.count = 0


counter = Counter()


# Rank 1 Schemas


class NodeType(Enum):
    INPUT = "Input"
    OUTPUT = "Output"
    HIDDEN = "Hidden"


class Node:
    def __init__(self, ntype: NodeType, idx: int = counter()):
        self.idx = idx
        self.ntype = ntype

    def __repr__(self):
        return f"Node(id={self.idx}, type={self.ntype})"

    def copy(self):
        return Node(self.ntype, self.idx)


class Connection:
    def __init__(
        self,
        in_node: int,
        out_node: int,
        weight: float = 1.0,
        idx: int = counter(),
        enabled: bool = True,
    ):
        self.idx = idx
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = enabled

    def __repr__(self):
        return (
            (f"Conn(from={self.in_node}, to={self.out_node}, weight={self.weight})")
            if self.enabled
            else (
                f"DisabledConn(from={self.in_node}, to={self.out_node}, weight={self.weight})"
            )
        )

    def toggle(self):
        self.enabled = not self.enabled

    def forward(self, input_value: float) -> float:
        if self.enabled:
            return input_value * self.weight
        return 0.0

    def copy(self):
        return Connection(
            self.in_node, self.out_node, self.weight, self.idx, self.enabled
        )


# Rank 2 Schemas


class Genome:
    def __init__(self, nodes: list[Node], connections: list[Connection]):
        self.nodes = nodes
        self.connections = connections

    def __repr__(self):
        return f"Genome(nodes={self.nodes}, connections={self.connections})"

    def mutate_weight(self, prob: float):
        for conn in self.connections:
            if random() < prob:
                conn.weight += (random() - 0.5) * 0.1
                break

    def mutate_link(self, prob: float):
        removed: list[int] = []

        for conn in self.connections:
            if random() < prob:
                new_node = Node(NodeType.HIDDEN)
                self.nodes.append(new_node)

                conn1 = Connection(conn.in_node, new_node.idx)
                self.connections.append(conn1)
                conn2 = Connection(new_node.idx, conn.out_node, conn.weight)
                self.connections.append(conn2)

                removed.append(conn.idx)

                break

        self.connections = [
            conn for conn in self.connections if conn.idx not in removed
        ]

    def mutate_toggle(self, prob: float):
        for conn in self.connections:
            if random() < prob:
                conn.toggle()

    def mutate_weight_random(self, prob: float):
        for conn in self.connections:
            if random() < prob:
                conn.weight = (random() - 0.5) * 2.0
                break

    def mutate_conn(self, prob: float):
        if random() < prob:
            in_node = choice(self.nodes).idx
            out_node = choice([node.idx for node in self.nodes if node.idx != in_node])

            if any(
                conn
                for conn in self.connections
                if conn.in_node == in_node and conn.out_node == out_node
            ):
                return

            new_conn = Connection(in_node, out_node, random())
            self.connections.append(new_conn)

    def crossover(self, partner: "Genome") -> "Genome":
        combined_nodes = {}
        combined_connections = {}

        for node in self.nodes + partner.nodes:
            if node.idx not in combined_nodes:
                combined_nodes[node.idx] = node.copy()
            else:
                new_idx = counter()
                combined_nodes[new_idx] = Node(node.ntype, new_idx)

        for conn in self.connections + partner.connections:
            if conn.idx not in combined_connections:
                combined_connections[conn.idx] = conn.copy()

        new_genome = Genome(
            nodes=list(combined_nodes.values()),
            connections=list(combined_connections.values()),
        )

        return new_genome


class Model:
    def __init__(self, input_size: int, output_size: int, init: bool = False):
        self.input_nodes = [
            Node(NodeType.INPUT, idx=counter()) for _ in range(input_size)
        ]
        self.output_nodes = [
            Node(NodeType.OUTPUT, idx=counter()) for _ in range(output_size)
        ]

        self.genome = Genome(nodes=self.input_nodes + self.output_nodes, connections=[])

        if init:
            counter.reset()
