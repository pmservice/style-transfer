# Transfer Style - Sample App in Python

## Getting started

### Local run

1. Modify files in `vcaps` to contain vcaps of your services.

2. Run:
   ```bash
   python server.py
   ```

Application will be available at `127.0.0.1:8080`.


### Bluemix run

1. Modify files in `vcaps` and `manifest.yml`.
2. Run:
   ```bash
   cf api <API-endpoint>
   cf login
   cf push
   ```
   
Application will be available on bluemix.