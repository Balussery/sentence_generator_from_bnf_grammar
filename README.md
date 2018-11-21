# Sentence generator (from bnf grammar)
This script generates and saves all possible sentences from a given bnf grammar. Sample grammar is given in the repository.

# Usage
~~~
 1. python3 sentence_generator.py <grammar_file.bnf> "<root_token>" 
                                or
 2. ./sentence_generator.py <grammar_file.bnf> "<root_token>"
 ~~~

The root token is usually "\<main>" (MUST BE IN STRING FORMAT), which is the Main Rule in the grammar. See the sample.bnf grammar for template.
