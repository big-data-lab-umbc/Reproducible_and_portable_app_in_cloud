import logging
import azure.functions as func


# The input binding field inputblob can either be 'bytes' or 'str' depends
# on dataType in function.json, 'binary' or 'string'.
def main(queuemsg: func.QueueMessage, inputblob: bytes) -> bytes:
    try:
        event_string = queuemsg.get_body().decode('utf-8')
        logging.info(f"Event is {event_string}")
    except:
        pass
    logging.info(f'Python Queue trigger function processed {len(inputblob)} bytes')
    return inputblob