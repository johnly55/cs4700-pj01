import logging


def main():
    is_test = True
    if is_test:
        machine_filename = 'machine_example.fa'
        strings_filename = 'strings_example.txt'
        accept_states, input_output_states, machine_type, alphabet, states \
            = read_machine_info(machine_filename)

        if accept_states is None:
            return

        print(f"Accept States: {accept_states}")
        print(f"Input and Output States:\n{input_output_states}")
        print(f"Machine Type: {machine_type}")
        print(f"Alphabet: {alphabet}")
        print(f"States: {states}")
        # TODO: build function to pass strings in.
        # print(f"Number of Strings Accepted: {some number}")
        read_strings(strings_filename, accept_states, input_output_states, machine_type)
    else:
        pass


def run_machine(accept_states, input_output_states, machine_type, input_string):
    return 0


def read_strings(filename, accept_states, input_output_states, machine_type):
    """
    Reads strings line by line, while running the machine.
    :param filename:
    :param accept_states:
    :param input_output_states:
    :param machine_type:
    :return:
    """
    file_dir = './'
    file_loc = file_dir + filename
    valid_strings = 0

    try:
        with open(filename, 'r') as file:
            for line in file.readlines():
                input_string = line.strip()
                # If line is empty, the input is epsilon.
                if len(input_string) == 0:
                    input_string = 'epsilon'
                valid_strings += run_machine(accept_states, input_output_states, machine_type, input_string)
    except FileNotFoundError:
        logging.exception(f"ERROR: The strings file does not exist! Filename: {filename}")


def is_input_valid(input_str, is_state):
    """
    Returns a boolean if the machine has states over 255, or has ASCII values
    out of the range of 32 - 126.
    :param str input_str:
    :param bool is_state:
    :return: is the machine state or symbol valid?
    :rtype: bool
    """
    is_valid = True

    if is_state:
        # Convert to state number to int and set not valid if more than 255.
        state_num = int(input_str)
        if state_num > 255:
            is_valid = False
    else:
        # Check if the input symbol is within the ASCII range 32 - 126.
        if not input_str == 'epsilon':
            ord_num = ord(input_str)
            if ord_num < 32 or ord_num > 126:
                is_valid = False

    return is_valid


def read_machine_info(filename):
    """
    Parse the machine file (.fa) into: accept states, start states,
    the inputs, and their output states, and then return them.
    :param str filename: name of m##.fa
    :returns: a list of accept states, a dict of input states
    containing a dict of input symbols and their output states,
    the machine type (DFA or NFA), list of the alphabet, and list of the states.
    :rtype: (list, dict, str, list, list)
    """
    accept_states = None
    input_output_states = {}
    machine_type = 'DFA'
    alphabet = []
    states = []

    file_dir = './'
    file_loc = file_dir + filename

    try:
        with open(file_loc, 'r') as file:
            # This will contain the accept state(s).
            header = file.readline()
            # Remove newline character then, split the string based on commas,
            # and remove the starting and closing brackets.
            accept_states = header.strip()[1:-1].split(',')
            # Check if accept state is empty.
            if len(accept_states[0]) == 0:
                accept_states = []

            # Start reading the rest of the file.
            for line in file:
                items = line.strip().split(',')
                # Because the last line of code may include empty values, we must remove them.
                while '' in items:
                    items.remove('')

                # If length of items is not 3, check for other exceptions.
                if len(items) < 3:
                    items.append(items[-1])
                    # Check if a comma was used as a symbol.
                    if line.strip().count(',') == 3:
                        items[1] = ','
                    # The other exception must be an epsilon.
                    else:
                        items[1] = 'epsilon'

                # Add each item to their respective category.
                if items[0] not in states:
                    states.append(items[0])

                if items[1] not in alphabet:
                    alphabet.append(items[1])

                if items[2] not in states:
                    states.append(items[2])

                if items[0] not in input_output_states:
                    # Initialize input state with another dict.
                    input_output_states[items[0]] = {}

                if items[1] not in input_output_states[items[0]]:
                    # Initialize the input symbol with output state.
                    input_output_states[items[0]][items[1]] = items[2]
                # There is a same input state/symbol combination meaning, it's an NFA.
                else:
                    if machine_type != 'INV':
                        machine_type = 'NFA'
                    new_symbol = items[1]
                    # A dict cannot have 2 of the same keys going to a different value.
                    # We will append a * to the symbol name to differentiate it, and this
                    # could happen multiple times.
                    while new_symbol in input_output_states[items[0]]:
                        new_symbol += '*'
                    input_output_states[items[0]][new_symbol] = items[2]

                # Check all values in items, if valid or not
                for i in range(len(items)):
                    is_state = True if i % 2 == 0 else False  # Is a state is in 0th or 2nd index.
                    if not is_input_valid(items[i], is_state):
                        machine_type = 'INV'
    except FileNotFoundError:
        logging.exception(f"The machine file does not exist! Filename: {filename}")

    return accept_states, input_output_states, machine_type, alphabet, states


if __name__ == '__main__':
    main()
