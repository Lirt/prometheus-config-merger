# Prometheus Config Merger

Sidecar to merge Prometheus configuration from multiple ConfigMaps and save it to file.

It is supposed to run as sidecar for Prometheus.

## How does it work

1. Watch the changes to configmaps with specific label.
1. On any change get the contents from all watched ConfigMaps.
1. Merge the content together as yaml.
1. Write the yaml content to file.
1. Hit Prometheus reload API to reload the file.

## How to run

Setup Python environment the standard way:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the program:

```bash
python3 -m merger \
        --prometheus-config-file-path 'my-test-config.yaml' \
        --label-selector='prometheus-merge-config=1' \
        --namespace 'monitoring' \
        --reload-url 'http://localhost:9090/-/reload'
```

## Integrating with Prometheus Community helm chart

If you want to use this sidecar with [prometheus-community helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus), you need to add this container as a sidecar, create common volume and mount it.

Here is example:

```yaml
server:
  sidecarContainers:
    prometheus-config-merger:
      image: lirt/prometheus-config-merger:0.1.0
      imagePullPolicy: IfNotPresent
      args:
      - --prometheus-config-file-path=/etc/config-prometheus/prometheus.yml
      - --label-selector='my-org.io/prometheus-merge-config=1' \
      - --namespace 'monitoring' \
      - --reload-url 'http://localhost:9090/-/reload'
      volumeMounts:
      - name: prometheus-merged-config
        mountPath: /etc/config-prometheus/

  extraVolumeMounts:
  - name: prometheus-merged-config
    mountPath: /etc/config-prometheus/

  extraVolumes:
  - name: prometheus-merged-config
    emptyDir: {}

  configPath: /etc/config-prometheus/prometheus.yml
```
