# SecureEdge — OTA candidate provisioning

## Requirements

- [ ] ROOTFS_B can access required persistent device identity
- [ ] Device private keys are not included in the OTA bundle
- [ ] Persistent DATA is mounted before dependent services
- [ ] MQTT CA and device credentials remain accessible
- [ ] Network configuration survives the slot switch
- [ ] secureedge-agent starts successfully on B
- [ ] MQTT mutual TLS authentication succeeds on B
- [ ] Expected telemetry is actually received by the broker
- [ ] Runtime watchdog remains enabled
- [ ] Trial health checks complete before B is confirmed

## Security

OTA packages must not embed production private keys.

Device-specific credentials must be provisioned through an
explicitly secured mechanism.

## Status

Candidate provisioning on real B: NOT YET VERIFIED.
