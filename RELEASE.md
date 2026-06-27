# Release Notes

## Helm Environment Sources

This release adds Helm chart support for Kubernetes `envFrom` entries. Deployments can now import environment variables from ConfigMaps and Secrets while keeping the existing direct `env` map for individual variables.

Example values:

```yaml
env:
  APP22_ENV: production

envFrom:
  - configMapRef:
      name: app22-config
  - secretRef:
      name: app22-secret
```

The Deployment template now renders `env` and `envFrom` only when values are provided, avoiding empty environment blocks in generated manifests.
