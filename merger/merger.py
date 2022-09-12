from argparse import Namespace
from logging import Logger

import yaml
import sys
import signal

from kubernetes import client, config, watch
from mergedeep import Strategy, merge

from merger.log import setup_logger
from merger.args import parse_args
from merger import prometheus


class Merger():
    logger: Logger
    w_configmaps: watch.Watch
    prometheus_config: dict
    args: Namespace
    stopped: bool

    def __init__(self, ):
        self.prometheus_config = {}
        self.args = parse_args()
        self.logger = setup_logger(self.args.logging_level)
        self.w_configmaps = watch.Watch()
        self.stop = False

    def cleanup(self, sig, frame):
        self.logger.info("Cleaning up watcher streams")
        self.w_configmaps.stop()
        self.stop = True
        raise Exception('Cleanup Finished')

    def start(self, ):
        self.load_kube_config()
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        # The watcher stream tends to break a lot
        # because of that we need to recreate the task in loop
        while True:
            self.logger.info("Watching config maps")

            try:
                self.watch_config_maps()
                self.logger.info("Watching done")
            except Exception as e:
                self.logger.warning("Exception: `%s`", e)

            if self.stop:
                break

    def load_kube_config(self, ):
        try:
            config.load_incluster_config()
            self.logger.info("Incluster kubeconfig loaded")
        except Exception as e:
            self.logger.info(
                "Cannot load incluster kubeconfig, trying local kubeconfigs: `%s`", e)
            try:
                config.load_kube_config()
                self.logger.info("Kubeconfig loaded")
            except Exception as e:
                self.logger.critical("Cannot load kubeconfig")
                sys.exit(1)

    def load_and_merge_config(self, ):
        '''Runs over all ConfigMaps to produce final Prometheus config and saves it'''
        v1 = client.CoreV1Api()
        try:
            config_maps: client.V1ConfigMapList = v1.list_namespaced_config_map(
                namespace=self.args.namespace, label_selector=self.args.label_selector, )
        except Exception as e:
            self.logger.error(e)
        config_map: client.V1ConfigMap
        for config_map in config_maps.items:
            # Merge data inside the ConfigMap into the final configuration
            # dictionary
            for key in config_map.data:
                data = config_map.data[key]
                data_yaml = yaml.safe_load(data)
                if isinstance(data_yaml, dict):
                    self.logger.info(
                        "Key `%s` in ConfigMap `%s` is a dictionary - merging",
                        key,
                        config_map.metadata.name)
                    merge(
                        self.prometheus_config,
                        data_yaml,
                        strategy=Strategy.ADDITIVE)
                else:
                    self.logger.info(
                        "Key `%s` in ConfigMap `%s` is not a dictionary - skipping merge",
                        key,
                        config_map.metadata.name)

        prometheus.save_config(
            self.args.prometheus_config_file_path,
            self.prometheus_config)
        prometheus.reload_prometheus(self.args.prometheus_reload_url)
        self.prometheus_config = {}

    def watch_config_maps(self, ):
        '''Watch events on ConfigMaps with specific label and reload prometheus configuration on event'''
        v1 = client.CoreV1Api()
        event: client.CoreV1Event

        try:
            for event in self.w_configmaps.stream(func=v1.list_namespaced_config_map, namespace=self.args.namespace,
                                                  label_selector=self.args.label_selector):
                self.logger.info(
                    'Registered ConfigMap event `%s` on resource `%s` in namespace `%s`',
                    event['type'],
                    event['object'].metadata.name,
                    event['object'].metadata.namespace)
                self.load_and_merge_config()
        except Exception as e:
            self.logger.warn("Config map watcher exception: %s", e)
