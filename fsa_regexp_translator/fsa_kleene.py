import re
from collections import defaultdict


def dfs(graph, start):
    visited, stack = set(), [(start, None)]
    while stack:
        vertex = stack.pop()[0]
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited


def log_error(message):
    with open('result.txt', 'w') as output_file:
        output_file.write('\n'.join(["Error:", message]))
    exit()


INPUT_FILE_FORMAT = {
    0: ('states=[', ']'),
    1: ('alpha=[', ']'),
    2: ('init.st=[', ']'),
    3: ('fin.st=[', ']'),
    4: ('trans=[', ']')
}


def main():
    with open('fsa.txt', 'r') as input_file:
        lines = map(lambda item: item.replace('\n', ''), input_file.readlines())

    fsa = dict()

    for i, line in enumerate(lines):
        if i > 4 or not line.startswith(INPUT_FILE_FORMAT[i][0]) or not line.endswith(INPUT_FILE_FORMAT[i][1]):
            log_error("E5: Input file is malformed")

        key, value = line.split('=')
        value = value[1: -1]  # Get rid of '{' and '}'

        regex = r''
        if i in [0, 2, 3]:  # States, Initial of Final state
            regex = r'[\da-zA-Z,]*'
        elif i == 1:  # Alpha
            regex = r'[\da-zA-Z_,]*'
        elif i == 4:  # Transitions
            regex = r'[\da-zA-Z_,>]*'

        matched = re.match(regex, value).group()
        if matched != value:
            log_error("E5: Input file is malformed")

        value = value.split(',')
        for i in range(len(value)):  # Think of an empty string case
            if not value[i]:
                del value[i]

        fsa[key] = value

    directed_graph = defaultdict(lambda: set())  # The representation of the FSA
    undirected_graph = defaultdict(lambda: set())  # Used for checking the connectivity
    trans_checker = defaultdict(lambda: defaultdict(lambda: False))  # Used for checking the determinism

    if not fsa['init.st']:
        log_error("E4: Initial state is not defined")

    if fsa['init.st'][0] not in fsa['states']:
        log_error("E1: A state '{0}' is not in the set of states".format(fsa['init.st'][0]))
    for fin in fsa['fin.st']:
        if fin not in fsa['states']:
            log_error("E1: A state '{0}' is not in the set of states".format(fin))

    for tran in fsa['trans']:
        start, alpha, end = tran.split('>')

        if start not in fsa['states']:
            log_error("E1: A state '{0}' is not in the set of states".format(start))
        if end not in fsa['states']:
            log_error("E1: A state '{0}' is not in the set of states".format(end))
        if alpha not in fsa['alpha']:
            log_error("E3: A transition '{0}' is not represented in the alphabet".format(alpha))

        if trans_checker[start][alpha]:
            log_error("E6: FSA is nondeterministic")
        else:
            trans_checker[start][alpha] = True

        directed_graph[start].add((end, alpha))
        undirected_graph[start].add((end, alpha))
        undirected_graph[end].add((start, alpha))

    if dfs(undirected_graph, fsa['init.st'][0]) != set(fsa['states']):
        log_error("E2: Some states are disjoint")

    # Check whether complete or incomplete
    is_complete = True
    for state in fsa['states']:
        trans = []
        for (dest, tran) in directed_graph[state]:
            trans.append(tran)
        if sorted(trans) != sorted(fsa['alpha']):
            is_complete = False

    # Check whether there is a transition between two states
    def check_transition(s, a, e):
        for (dest, tran) in directed_graph[str(s)]:
            if dest == str(e) and tran == str(a):
                return True
        return False

    # Initial step. k = -1
    n = len(fsa['states'])
    R = [[['{}'] * (n+1) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            for a in fsa['alpha']:
                if check_transition(fsa['states'][i], a, fsa['states'][j]):
                    if R[i][j][0] != '{}':
                        R[i][j][0] = "{0}|{1}".format(R[i][j][0], a)
                    else:
                        R[i][j][0] = a
            if i == j:
                if R[i][j][0] != '{}':
                    R[i][j][0] = "{0}|eps".format(R[i][j][0])
                else:
                    R[i][j][0] = "eps"

    # Inductive steps
    for k in range(1, n+1):
        for i in range(n):
            for j in range(n):
                R[i][j][k] = "({0})({1})*({2})|({3})".format(R[i][k-1][k-1], R[k-1][k-1][k-1], R[k-1][j][k-1], R[i][j][k-1])

    # Determining the initial state
    start = fsa['init.st'][0]
    for i in range(n):
        if start == fsa['states'][i]:
            start = i
            break

    # Determining the answer
    answer = '{}'
    for i in range(n):
        if fsa['states'][i] in fsa['fin.st']:
            if answer == '{}':
                answer = R[start][i][n]
            else:
                answer = "{0}|{1}".format(answer, R[start][i][n])

    with open('result.txt', 'w') as output_file:
        output_file.write(answer)


if __name__ == '__main__':
    main()
