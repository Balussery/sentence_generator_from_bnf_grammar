#!/usr/bin/env python3

import itertools
import sys

class SentenceGeneratorFromGrammar(object):
    """This class holds methods to generate unique sentences from a bnf type grammar.
    USAGE: python sentence_gen_frm_grammar.py <grammar_file> <root_token>
    PS: usually the root token is "<main>", which is the /*Main Rule*/ in the grammar.
    """

    def __init__(self, grammar, arg):
        super(SentenceGeneratorFromGrammar, self).__init__()

        # The generator only considers the grammar from root till the EOF
        self.root = arg
        self.grammar = grammar

        # grammar char definitions
        self.OR = '|'
        self.OPTIONAL_START = '['
        self.OPTIONAL_STOP = ']'
        self.VARIABLE = '<>'
        self.START = ':'
        self.STOP = ';'

    def clear_comments(self):

        # read lines
        content = open(grammar, 'r').readlines()

        # rm extra chars
        content = [item.strip('\n') for item in content]
        content = [item for item in content
                   if '#' not in item
                   and '!' not in item
                   and item is not '']

        # rm one line comments
        content = [item for item in content
                   if not item.startswith('/*')
                   or not item.endswith('*/')]
        content = [item for item in content if not item.startswith('//')]

        # rm multi line comments
        # get comment index
        comment_index = [0]
        start_flag = False
        stop_flag = False
        for i, item in enumerate(content):
            if '/*' in item:
                temp_start = i
                start_flag = True
            elif '*/' in item:
                temp_stop = i
                stop_flag = True
            else:
                pass

            if start_flag and stop_flag:
                comment_index = comment_index + [temp_start, temp_stop]
                start_flag = False
                stop_flag = False

        # add length
        comment_index.append(len(content))

        # rm items bw comment index
        new_content = []
        zipped = zip(comment_index[::2], comment_index[1::2])
        first = True
        for item in zipped:
            if first:
                new_content = new_content + content[item[0]:item[1]]
                first = False
            else:
                new_content = new_content + content[item[0] + 1:item[1]]

        return new_content

    def extract_variables(self, content):
        dictionary = {}
        for i, item in enumerate(content):
            if self.START in item:
                v_name = item.replace(':', '')
                start_idx = i
                continue
            elif self.STOP in item:
                # join until the stop char
                v_value = ' '.join(content[start_idx + 1:i + 1])
                # rm stop char and split at OR
                v_value = v_value.replace(self.STOP, '').split(self.OR)
                # strip of end spaces
                v_value = [item.strip() for item in v_value]
            else:
                continue

            dictionary[v_name] = v_value

        return dictionary

    def dump_to_text(self, content):
        file = open('sentences.txt', 'w')
        content = sorted(content)
        for item in content:
            file.write(item + '\n')
        file.close()

    def recursive(self, variables_dic):

        ######################################
        # HANDLING OPTIONAL VARIABLES (Example: "Something [<variable>]")
        ######################################

        # check if parent has optional items
        def has_optional(parent):
            for item in parent:
                if self.OPTIONAL_START in item:
                    return True

        # find possible combinations of 0 and 1 given the number of optional items
        def index_combinations(item):
            # get total number of optional items and corresponding indices
            optional_num = 0
            optional_idx = []
            split_items = item.split()
            for i, value in enumerate(split_items):
                if self.OPTIONAL_START in value:
                    optional_num += 1
                    optional_idx.append(i)

            # generate possible combinations given the optional characters
            idx_combinations = []
            optional_idx_temp = []
            complete_idx = list(range(len(split_items)))
            for item in itertools.product([0, 1], repeat=optional_num):
                bin_item_list = list(item)
                for i, item in enumerate(bin_item_list):
                    if item != 0:
                        optional_idx_temp.append(optional_idx[i])
                if len(optional_idx_temp) > 0:
                    idx_combinations.append([item for item in complete_idx if item not in optional_idx_temp])
                    optional_idx_temp = []
                else:
                    idx_combinations.append(complete_idx)

            return idx_combinations

        # handle the optional variables in the grammar. Returns list with all possible combinations of the optional
        def handle_optional(parent):
            new_parent = []
            for item in parent:
                if self.OPTIONAL_START in item:
                    # rm "optional" characters from the item
                    item_wo_optional_chars = item.replace(self.OPTIONAL_START, "").replace(self.OPTIONAL_STOP, "").split()
                    idx_combinations = index_combinations(item)
                    for idx in idx_combinations:
                        new_parent.append(" ".join([item_wo_optional_chars[i] for i in idx]))
                else:
                    new_parent.append(item)

            return new_parent

        ######################################
        # HANDLING VARIABLE REPLACEMENT
        ######################################

        # find the children given parent
        def find_children_of_parent(parent_item):
            children = {}
            split_items = parent_item.split()
            for var in split_items:
                if "<" in var and var in variables_dic and var not in children:
                    children[var] = variables_dic[var]
                else:
                    continue

            return children

        # given parent return a new list with replacement
        def return_replaced(parent, temp_destination_list):

            # modify parent if it has optional items
            if has_optional(parent):
                parent = handle_optional(parent)

            # replace the variables
            destination_list = set()
            for item in parent:
                children_list = find_children_of_parent(item)
                for key, children in children_list.items():
                    for child in children:
                        destination_list.add(item.replace(key, child))

            # save completed sentences to temp set
            temp_destination_list = temp_destination_list.union({item for item in destination_list if '<' not in item})
            destination_list = {item for item in destination_list if item not in temp_destination_list}

            # status checks for recursive
            status = 'stop'
            if len(destination_list) > 0:
                status = 'recursive'

            # limit memory for big grammars
            if len(temp_destination_list) > 1000000: status = 'stop'

            # recursive on condition
            if status == 'recursive':
                return_replaced(parent=destination_list, temp_destination_list=temp_destination_list)
            else:
                self.dump_to_text(temp_destination_list)

        # start the recursion from root
        return_replaced(parent=variables_dic[self.root], temp_destination_list=set())
        print('SUCCESSFUL. PLS CHECK THE FILE: sentences.txt')

    def generate(self):
        content = self.clear_comments()
        variables_dic = self.extract_variables(content)
        self.recursive(variables_dic)

if __name__ == '__main__':

    grammar, root = None, None

    try:
        grammar = str(sys.argv[1])
    except IndexError:
        print("\n====GRAMMAR ERROR====\n"
              'USAGE: python3 sentence_gen_frm_grammar.py <grammar_file> "<root>"'
              '\nPS: usually the root token is "<main>" (MUST BE IN STRING FORMAT), which is the /*Main Rule*/ in the grammar')
    try:
        root = str(sys.argv[2])
    except IndexError:
        print("\n====ROOT ERROR====\n"
             'USAGE: python3 sentence_gen_frm_grammar.py <grammar_file> "<root>"'
              '\nPS: usually the root token is "<main>" (MUST BE IN STRING FORMAT), which is the /*Main Rule*/ in the grammar')

    if grammar is not None and root is not None:
        instance = SentenceGeneratorFromGrammar(grammar, root)
        instance.generate()