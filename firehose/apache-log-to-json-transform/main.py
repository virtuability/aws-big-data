""" Apache Log to Json transform example
"""

from __future__ import print_function

import base64

import logging.config
import json
import yaml

from datetime import datetime

with open('resources/logging.yaml', 'r') as log_config_file:
    logging.config.dictConfig(yaml.safe_load(log_config_file))

from context_log import ContextLog

print('Loading function')

def lambda_handler(event, context):

    log = ContextLog.get_logger('lambda_handler', True)
    ContextLog.put_start_time()
    ContextLog.put_request_id(context.aws_request_id)
    log.info('start')

    output = []

    try:

        for record in event['records']:

            payload = base64.b64decode(record['data']).decode()

            log.info('Processing request id: %s', record['recordId'])

            # Transform time to isoformat and add to record
            d = json.loads(payload)
            t = datetime.strptime(d['datetime'], "%d/%b/%Y:%H:%M:%S %z")
            d['datetimeiso'] = t.isoformat()
            
            payload = json.dumps(d) + '\n'

            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(payload.encode()).decode()
            }
            output.append(output_record)

        log.info('Successfully processed records: %d', len(event['records']))

    except:
        log.exception('Unexpected error')
        raise
    finally:
        ContextLog.put_end_time()
        log.info('Request: end')

    return {'records': output}
