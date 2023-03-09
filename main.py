def main():
    filename = 'm00.fa'
    accept_states, input_output_states, machine_type = read_machine_info(filename)
    print(f"Accept States: {accept_states}")
    print(f"Input and Output States:\n{input_output_states}")
    print(f"Machine Type: {machine_type}")
    print(f"Number of States: {len(input_output_states)}")
    # TODO: get all possible transition symbols.
    # print(f"Size of Alphabet: {len(input_output_states)}")
    # TODO: build function to pass strings in.
    # print(f"Number of Strings Accepted: {some number}")


def is_machine_valid(accept_states, input_output_states):
    """
    Returns a boolean if the machine can reach its end state from the start state.
    :param list accept_states:
    :param dict input_output_states:
    :return: Is there a path from start to end state?
    :rtype: bool
    """
    pass


def read_machine_info(filename):
    """
    Parse the machine file (.fa) into: accept states, start states,
    the inputs, and their output states, and then return them.
    :param str filename: name of m##.fa
    :returns: a list of accept states, a dict of input states
    containing a dict of input symbols and their output states,
    and the machine type (DFA or NFA)
    :rtype: (list, dict, str)
    """
    accept_states = []
    input_output_states = {}
    machine_type = 'DFA'

    file_dir = './'
    file_loc = file_dir + filename
    with open(file_loc, 'r') as file:
        # This will contain the accept state(s).
        header = file.readline()
        # Remove newline character then, split the string based on commas,
        # and remove the starting and closing brackets.
        accept_states = header.strip()[1:-1].split(',')
        for line in file:
            items = line.strip()
            # Must be an epsilon transition.
            if len(items) == 4:
                items = [items[0], 'epsilon', items[3]]
                machine_type = 'NFA'
            else:
                # Gets the input state, input symbol, and output state.
                # Allows for commas to be used as symbols too (doesn't use .split()).
                items = [items[0], items[2], items[4]]

            if items[0] not in input_output_states:
                # Initialize input state with another dict.
                input_output_states[items[0]] = {}
            if items[1] not in input_output_states[items[0]]:
                # Initialize the input symbol with output state.
                input_output_states[items[0]][items[1]] = items[2]
            # There is a same input state/symbol combination meaning, it's an NFA.
            else:
                machine_type = 'NFA'
                new_symbol = items[1]
                # A dict cannot have 2 of the same keys going to a different value.
                # We will append a * to the symbol name to differentiate it, and this
                # could happen multiple times.
                while new_symbol in input_output_states[items[0]]:
                    new_symbol += '*'
                input_output_states[items[0]][new_symbol] = items[2]

    return accept_states, input_output_states, machine_type


if __name__ == '__main__':
    main()
