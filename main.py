import logging

INV = 'INV'
DFA = 'DFA'
NFA = 'NFA'
EPSILON = 'epsilon'


def main():
    is_test = False
    if is_test:
        machine_filename = 'machine_example.fa'
        strings_filename = 'strings_example.txt'
        accept_states, input_output_states, machine_type, alphabet, states \
            = read_machine_info(machine_filename)

        if accept_states is None:
            return

        read_write_strings(strings_filename, machine_filename, accept_states,
                           input_output_states, machine_type, len(states), len(alphabet))
        print(f"Accept States: {accept_states}")
        print(f"Input and Output States:\n{input_output_states}")
        print(f"Machine Type: {machine_type}")
        print(f"Alphabet: {alphabet}")
        print(f"States: {states}")
    else:
        strings_filename = 'machines/strings.txt'
        folder_dir = 'machines/'
        low_range, high_range = 0, 36
        for i in range(low_range, high_range):
            machine_filename = folder_dir + 'm' + ('%02d' % i) + '.fa'
            print(f"Machine Name: {machine_filename}")
            accept_states, input_output_states, machine_type, alphabet, states \
                = read_machine_info(machine_filename)

            if accept_states is None:
                return

            read_write_strings(strings_filename, machine_filename, accept_states,
                               input_output_states, machine_type, len(states), len(alphabet))
            print(f"Accept States: {accept_states}")
            print(f"Input and Output States:\n{input_output_states}")
            print(f"Machine Type: {machine_type}")
            print(f"Alphabet: {alphabet}")
            print(f"States: {states}")
            print('\n')


def run_machine(accept_states, input_output_states, machine_type, input_string):
    """
    Runs the machine with the inputted string with either DFA or NFA logic.
    Then return a true or false, depending on if the string ended in an accept state.
    :param list accept_states:
    :param dict input_output_states:
    :param str machine_type:
    :param str input_string:
    :return: was the string accepted?
    :rtype: bool
    """
    current_state = '0'
    if machine_type == DFA:
        # If epsilon, skip it.
        if input_string != EPSILON:
            # Go through each symbol in the inputted string.
            for symbol in input_string:
                # If the current state is 255, make a new entry for it.
                if current_state not in input_output_states:
                    input_output_states[current_state] = {}

                # Say a state doesn't explicitly say where a symbol will go,
                # infer that it will go to state 255.
                if symbol not in input_output_states[current_state]:
                    input_output_states[current_state][symbol] = '255'
                else:
                    current_state = input_output_states[current_state][symbol]
    else:
        # With NFAs, for every state, branch off into all possible transitions.
        # Contains transition state, symbol, and remaining string (using an index).
        possible_routes = [(current_state, 0)]
        found_path = False
        while possible_routes and not found_path:
            route_state, route_index = possible_routes.pop()  # Pop like a stack.
            route_symbol = input_string
            if input_string != EPSILON:
                route_symbol = input_string[route_index]

            # If the current state is 255, make a new entry for it.
            if route_symbol != EPSILON and route_state not in input_output_states:
                input_output_states[route_state] = {}

            # If epsilon value but no set paths.
            if route_symbol == EPSILON and route_symbol not in input_output_states[route_state]:
                input_output_states[route_state][route_symbol] = route_state

            # Say a state doesn't explicitly say where a symbol will go,
            # infer that it will go to state 255.
            if route_symbol != EPSILON and route_symbol not in input_output_states[route_state]:
                input_output_states[route_state][route_symbol] = '255'

            # Otherwise, this is a valid state and symbol.
            # If alphabet for this route isn't finished
            if route_index + 1 < len(input_string):
                # Add the basic transition for this state and its symbol.
                new_state = input_output_states[route_state][route_symbol]
                possible_routes.append((new_state, route_index + 1))

                # Add any epsilon transitions at this state as long as it doesn't loop.
                if EPSILON in input_output_states[route_state]:
                    new_state = input_output_states[route_state][EPSILON]
                    if route_state != new_state:
                        possible_routes.append((new_state, route_index))

                # Check for same state/symbol transitions, and add them.
                # Recall that we did this by continuously adding stars (*).
                # Ex: Multiple transitions of 'a' in state 0 will be: 'a', 'a*', 'a**', etc.
                # Same with epsilon, Ex: epsilon, epsilon*, etc.
                symbol_loop = epsilon_loop = True
                symbol_counter = epsilon_counter = 1
                while symbol_loop or epsilon_loop:
                    new_symbol = route_symbol + ('*' * symbol_counter)
                    if symbol_loop and new_symbol in input_output_states[route_state]:
                        symbol_counter += 1
                        # Increment index because it reads a character.
                        new_state = input_output_states[route_state][new_symbol]
                        possible_routes.append((new_state, route_index + 1))
                    else:
                        symbol_loop = False
                    # Clone *'s for epsilon if a possibility of transitioning.
                    new_epsilon = EPSILON + ('*' * epsilon_counter)
                    if epsilon_loop and EPSILON in input_output_states[route_state] \
                            and new_epsilon in input_output_states[route_state]:
                        epsilon_counter += 1
                        new_state = input_output_states[route_state][new_epsilon]
                        possible_routes.append((new_state, route_index))
                    else:
                        epsilon_loop = False
            else:
                # Alphabet is finished, and it ends in an accept state.
                new_state = input_output_states[route_state][route_symbol]
                if new_state in accept_states:
                    current_state = new_state
                    found_path = True
                    break

    # If the last state is in one of the accept states, it's a valid string.
    return True if current_state in accept_states else False


def read_write_strings(strings_filename, machine_filename, accept_states,
                       input_output_states, machine_type, num_states, size_alphabet):
    """
    Reads strings line by line, while running the machine. And, simultaneously write
    valid strings into an output file.
    :param str strings_filename:
    :param str machine_filename:
    :param list accept_states:
    :param dict input_output_states:
    :param str machine_type:
    """
    num_valid_strings = 0
    output_file = machine_filename[:-3]  # Removes the .fa extension.
    output_file += '.txt'

    if machine_type == 'INV':
        log_file(machine_filename, machine_type, num_states, size_alphabet, num_valid_strings)
    else:
        try:
            with open(strings_filename, 'r') as infile, open(output_file, 'w') as outfile:
                for line in infile.readlines():
                    input_string = line  # Can't strip, new to keep spaces.
                    # Remove any newline character.
                    if '\n' in input_string:
                        input_string = input_string[:-1]

                    # If line is empty, the input is epsilon.
                    if len(input_string) == 0:
                        input_string = EPSILON
                    # Runs the machine, return a true or false.
                    is_valid = run_machine(accept_states, input_output_states, machine_type, input_string)
                    if is_valid:
                        num_valid_strings += 1
                        outfile.write(input_string + '\n')

                log_file(machine_filename, machine_type, num_states, size_alphabet, num_valid_strings)
        except FileNotFoundError:
            logging.exception("The strings file does not exist!")
        except KeyError:
            logging.exception(f"The dict: {input_output_states} \ndoes not have a key used by the string: {line}")

        print(f"Valid Strings: {num_valid_strings}")


def log_file(machine_filename, machine_type, num_states, size_alphabet, num_valid_strings):
    output_file = machine_filename[:-3]
    output_file += '.log'
    with open(output_file, 'w') as file:
        new_name = output_file
        if '/' in new_name:
            new_name = new_name.split('/')[1]
        file.write(f"{new_name[:-4]},{machine_type},{num_states},{size_alphabet},{num_valid_strings}")


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
        if not input_str == EPSILON:
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
    machine_type = DFA
    alphabet = []
    states = []

    try:
        with open(filename, 'r') as file:
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
                # Non-empty line.
                if line != '\n':
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
                            items[1] = EPSILON
                            if machine_type != INV:
                                machine_type = NFA

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
                        if machine_type != INV:
                            machine_type = NFA
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
                            machine_type = INV
    except FileNotFoundError:
        logging.exception(f"The machine file does not exist! Filename: {filename}")

    return accept_states, input_output_states, machine_type, alphabet, states


if __name__ == '__main__':
    main()
