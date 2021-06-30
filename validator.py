from colorama.ansi import Style
from jsonschema import Draft7Validator
from icecream import ic
from json import load, loads
from colorama import Fore
import logging
import os 

logging.basicConfig(level=logging.ERROR, filename='logging.log')

root = os.path.join(os.getcwd(), 'task_folder')
path = os.path.join(root, 'event')
messages = list()
schemas = dict()

with os.scandir(path) as fileList:
    for entry in fileList:
        messages.append(entry.name) if entry.is_file() else None

path = os.path.join(root, 'schema')
with os.scandir(path) as fileList:
    for entry in fileList:
        schemas[entry.name[:-7]] = list() if entry.is_file() else None
ic(schemas)


for schema in schemas:
    with open(os.path.join(root, 'schema', schema + '.schema'), 'r') as schema_file:
        to_check = loads(schema_file.read())

    logging.error(f'Errors in {schema} shema:  {Draft7Validator.check_schema(to_check)}')

print(Style.RESET_ALL)
for num, msg in enumerate(messages):
    try:
        with open(os.path.join(root, 'event', msg), 'r') as msg_file:
            data = loads(msg_file.read())
        
        event = str(data.get('event'))
        form_event = event.strip().replace(' ','')
        if form_event != event:
            logging.error(f'{msg}: Invalidate event name for cheking by schema')
            continue
        if 'meditation' in form_event:
            key = 'workout_created'
        elif 'cmarker' in form_event:
            key = 'cmarker_created'
        else:
            key = form_event
        schemas.get(key).append(msg)

        with open(os.path.join(root, 'schema', key + '.schema')) as schema:
            template = load(schema)

        validator = Draft7Validator(template)
        for error in (list(validator.iter_errors(data))):
            logging.error(f'{msg}: {error.args[0]}')

    except TypeError as error:
        logging.error(f"{msg}: No verification schemes specified")
        continue
    except AttributeError as error:
        logging.error(f"{msg}: {error}")
        continue
    
