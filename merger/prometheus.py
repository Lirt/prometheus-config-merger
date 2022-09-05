import requests
import logging
import yaml


def reload_prometheus(url):
    '''Do post on Prometheus endpoint to reload it'''
    logger = logging.getLogger(__name__)
    try:
        requests.post(url=url)
    except Exception as e:
        logger.warning("POST to prometheus url failed with exception `%s`", e)


def save_config(path, config):
    '''Save prometheus config to file'''
    logger = logging.getLogger(__name__)
    try:
        with open(path, 'w', encoding='utf8') as f:
            f.write(yaml.dump(config))
    except Exception as e:
        logger.error(e)
