import argparse


def parse_args():
    '''Parse arguments'''
    parser = argparse.ArgumentParser(
        description='Watch for ConfigMaps containing prometheus configuration with specific label and read their contents and merge into final yaml file on disk.')
    parser.add_argument(
        '--label-selector',
        dest='label_selector',
        action='store',
        default="prometheus-merge-config=1",
        help='Label selector applied to list ConfigMaps')
    parser.add_argument(
        '--prometheus-config-file-path',
        dest='prometheus_config_file_path',
        action='store',
        default="/etc/config/prometheus.yml",
        help='Path where to store Prometheus config')
    parser.add_argument(
        '--logging-level',
        dest='logging_level',
        action='store',
        default="INFO",
        help='Logging level')
    parser.add_argument('--reload-url', dest='prometheus_reload_url', action='store',
                        default="http://localhost:9090/-/reload",
                        help='URL where to call for Prometheus reload.')
    parser.add_argument('--namespace', dest='namespace', action='store',
                        default="kube-system",
                        help='Namespace in which to look for ConfigMaps')
    args = parser.parse_args()
    return args
