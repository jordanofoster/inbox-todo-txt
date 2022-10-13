import os, argparse, glob, yaml, re, logging
from datetime import datetime

parser = argparse.ArgumentParser(description="Program that populates a todo.txt file based on reading contents.")
parser.add_argument('yaml', type=str)
parser.add_argument('-td', '--todo', type=str)
parser.add_argument('-i', '--inbox', type=str)
parser.add_argument('-exp', '--expression-type', choices=('regex','glob'), required=True, type=str)
parser.add_argument('-ncd', '--no-created-date', action='store_true')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

def isMatch(exp, str, expType=args.expression_type):
  if expType == 'regex':
    try:
      pattern = re.compile(r'{}'.format(exp))
      if re.match(pattern, str):
        return True
    except re.error:
      logging.warning(f"Regexp - {exp} considered invalid expression")
  elif expType == 'glob':
      for globdir in glob.glob(exp):
        if os.path.samefile(str, globdir):
            return True

  if args.debug:
    logging.debug(f"Match not found in {str} with expression {exp} (type: {expType})")
  return False

try:
  with open(args.yaml, 'r') as yamlFile:
    yamlContents = yaml.safe_load(yamlFile)
    yamlFields = yamlContents.keys()
except yaml.YAMLError as yamlE:
  logging.critical(yamlE)
  exit(1)
except FileNotFoundError as fnfE:
  logging.critical(fnfE)
  exit(1)

if args.todo == None:
  try:
    todo_dir = yamlContents['todo_dir']
  except KeyError as ke:
    logging.critical(ke)
    exit(1)
else:
  todo_dir = args.todo

if args.inbox == None:
  try:
    inbox_dir = yamlContents['inbox_dir']
  except KeyError as ke:
    logging.critical(ke)
    exit(1)
else:
  inbox_dir = args.todo

try:
  with open(todo_dir, "rt") as todoDump:
    todoInitialContents = todoDump.read()
except FileNotFoundError:
  todoInitialContents = ""

with open(todo_dir, "at") as todoAppend:
  for filedir in glob.glob(inbox_dir + "*"):
      filename = os.path.basename(filedir)
      if isMatch(todo_dir,filedir,'glob') or isMatch(args.yaml,filename,'glob') or isMatch(__file__,filedir,'glob') or not os.path.isfile(filedir):
        continue
      if filename not in todoInitialContents:
        ignored = False
          
        for exp in yamlContents['ignore']:
              if isMatch(exp,filename):           
                ignored = True
                break

        if ignored == False:

          outputStr = ""
          
          priorityStr = ""
          for priority,expList in yamlContents['priorities'].items():
            if not isMatch(r'[A-Z]',priority,expType='regex'):
              logging.warning(f"Priority - invalid value {priority} (expected A-Z)")
              continue
            else:
              for exp in expList:
                if isMatch(exp,filename):
                  if (priorityStr == "") or (ascii(priority) < ascii(priorityStr[1])):
                    #If we have a higher character (descending)
                    priorityStr = f"({priority})"
                  break

          projectsStr = ""
          for project,expList in yamlContents['projects'].items():
            for exp in expList:
              if isMatch(exp,filename):     
                if projectsStr != "":
                  projectsStr += " "
                projectsStr += f"+{project}"
                break
                    
          contextsStr = ""
          for context,expList in yamlContents['contexts'].items():
            for exp in expList:
              if isMatch(exp,filename):
                if contextsStr != "":
                  contextsStr += " "
                contextsStr += f"@{context}"
                break
          
          if priorityStr != "":
            outputStr = priorityStr + " "
          
          if not args.no_created_date:
            outputStr += f"{datetime.now().strftime('%G-%m-%d')}" + " "

          outputStr += filename

          if projectsStr != "":
            outputStr += " " + projectsStr
          
          if contextsStr != "":
            outputStr += " " + contextsStr

          todoAppend.write(f"{outputStr}\n")
