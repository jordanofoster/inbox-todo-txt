# inbox-todo-txt

Tool that automatically adds files within a directory to a given [todo.txt](https://github.com/todotxt/todo.txt) format file, assigning projects and contexts according to a provided YAML config.

## Commandline Args

`python inbox-todo.txt.py [YAMLDIR] [OPTIONS...]`

`-td`/`--todo` - Override YAML config by providing your own todo.txt path.

`-i-`/`--inbox` - Override YAML config by providing own inbox path.

`-exp`/`--expression-type` - Choose how the script interprets expressions (`regex`/`glob`).

`--debug` - Logs debug level messages.

## YAML file format

The script expects, at minimum, the following sections:

- The `ignore`, `projects` and `contexts` fields to be defined.
  - These need not be populated; but the script expects their existence for now and throws an exception without.

Optionally:

- Within `ignore`:
  - a list ('`-`') of any of the following:
    - exact filenames
      - A Regular OR Glob expression (not both)

- Within `projects`/`contexts`:
  - A set of subfields that contain a list ('`-`') of any of the following:
    - exact filename
    - A Regular OR Glob expression (not both)
  
```yaml
---
ignore:
  - ignore-this-file.please

projects:
  example-project:
    - project-file-1.txt
    - 'project-file-?.txt'
    - 'project-*.txt'
    - '^[a-z]*-[a-z]*-[0-9]*.txt$'

contexts:
  example-context:
    - normal-context.txt
    - 'example-glob-*.txt'
    - '^[a-z]*-example-regex.txt$'
```

## How the script adds tasks

1. If the given todo.txt directory exists, read its contents (to prevent duplicate entries). Otherwise, create a new one.
2. For each file in the given directory that is NOT:

    - The todo.txt file itself, according to given filepath
    - The YAML config, according to given filepath
    - The script itself (`__file__`)

    1. Check if it has been ignored. If so, skip.
    2. For each project listed in the YAML config:

       - Check each expression according to `--exp`.
         - Log invalid regexp (`re.error`) to stdout.
         - If the current file matches any patterns listed, add `+[project]` to the constructed string and go to the next project listed.
    3. Do the same for each context listed in the YAML config.
    4. Write a line to the todo file in the following format:

       `[current date, YYYY-MM-DD] filename [projects] [contexts]`

## Further work

- Find some way to allow Regex/Glob patterns to coexist in the same YAML file.
- Allow the definition of priorities:

```yaml
priorities:
  A:
    - really-important-file.docx
  B:
    - less-important-file.tex
  F:
    - sunday-reading.pdf
```
  
- Allow for 'catchall' entries that are other priorities/contexts/projects through prefixes; for example:

```yaml
priorities:
  A:
    - (B)

projects:
  really-cool-project:
    - +another-sub-project

contexts:
  new-context:
    - @existing-context

  #And a mix:
  mixed-context:
    - (A)
    - +really-cool-project
    - @new-context
```

- Significant refactoring
- Other features...?
