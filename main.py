#!/usr/bin/env python3
#
import typer
import csv
from typing import IO, Optional
import graphviz

app = typer.Typer()


def generate_map(f: IO) -> dict:
    lookup = {}
    csv_reader = csv.reader(f, delimiter=",")
    for row in csv_reader:
        if row[0] not in lookup:
            lookup[row[0]] = {}
        lookup[row[0]][row[1]] = (row[2], row[3])
    return lookup


def visualise(lookup: dict, name: str):
    graph = graphviz.Digraph(
        graph_attr={"label": name, "nodesep": "1", "rankdir": "LR"},
        format="png",
    )

    # Add starting arrow
    graph.node("", shape="none")
    graph.edge("", "q0")

    graph.attr("node", shape="doublecircle")
    graph.node("h")

    graph.attr("node", shape="circle")

    for node in lookup:
        graph.node(node)
        for transition in lookup[node]:
            action = lookup[node][transition]
            graph.edge(node, action[1], f"{transition}/{action[0]}")

    graph.render(filename=name, cleanup=True)


def compute(tape: list, control: dict, head: int) -> tuple:

    current_state: str = "q0"

    while current_state != "h":
        if head >= len(tape):
            tape += "#"
        symbol = tape[head]
        if current_state in control:
            if symbol in control[current_state]:
                transition = control[current_state][symbol]  # (action,new_state)
                current_state = transition[1]
                if transition[0] == "L":
                    head -= 1
                    if head < 0:
                        return (False, f"Error: turing machine tape ran out")
                elif transition[0] == "R":
                    head += 1
                else:
                    tape[head] = transition[0]
            else:
                return (
                    False,
                    f"Error: no transition was defined from state {current_state} given {head}",
                )
        else:
            return (
                False,
                f"Error: no transitions were defined from state {current_state}",
            )
    return (True, "".join(tape))


@app.command()
def main(
    machine: str = typer.Argument(
        ...,
        help="CSV File containing the rules of the turing machine: <state>,<head>,<action>,<new_state>. To move the tape left or right the action is (L,R), otherwise the assumption will be replacement.",
    ),
    tape: str = typer.Option(
        None,
        help="The input string to the turing machine, this string should always start and end with ##.",
    ),
    tests: str = typer.Option(
        None, help="CSV File containing a list of test inputs to the automaton"
    ),
    render: bool = typer.Option(False, help="Render the turing machine with graphviz"),
):
    """
    CPS3239 Turing Machine Emulator
    """
    control: dict = generate_map(open(machine))

    if render:
        visualise(control, machine.split(".")[0])

    if tape is not None:
        _tape: list = list(tape)
        ret = compute(_tape, control, 0)
        print(ret[1])

    counter: int = 1
    if tests is not None:
        csv_reader = csv.reader(open(tests), delimiter=",")
        for row in csv_reader:
            ret = compute(list(row[0]), control, 0)
            if ret[0]:
                if ret[1] == row[1]:
                    print(f"#{counter} Passed")
                else:
                    print(f"#{counter} Failed -> Expected {row[1]}, Found {ret[1]}")
            else:
                print(f"#{counter} {ret[1]}")
            counter += 1


if __name__ == "__main__":
    typer.run(main)
