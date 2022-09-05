# Prometheus Config Merger

Sidecar to merge Prometheus from multiple ConfigMaps and save to file.

It is supposed to run as sidecar for Prometheus.

## How does it work

1. Watch the changes to configmaps with specific label
1. On any change get the contents from all watched ConfigMaps
1. Merge the content together as yaml
1. Write the yaml content to file
1. Hit Prometheus reload API to reload the file

## How to run

Setup Python environment the standard way:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the program:

```bash
python3 -m merger --prometheus-config-file-path 'my-test-config.yaml'
```