# Transfer Style - Sample App in Python

Requirements:
- python 3.5
- pip
- Cloud Foundry Command Line Interface (cf CLI)

User also should have account on Bluemix with active us-south region. In us-south region should be prepared following services:
- IBM Watson Machine Learning (wml)
- IBM Cloud Object Storage (cos)

## Initial configuration

1. Clone repository and enter cloned repo:
   ```bash
   git clone https://github.com/pmservice/style-transfer.git
   cd style-transfer
   ```
2. Get wml and cos vcaps. Update with your services vcaps folowing files: `vcaps/wml.vcap` and `vcaps/cos.vcap`.

### Local run configuration

Run:
```bash
pip install requirements.txt
python server.py
```

Application will be available at `127.0.0.1:8080`.


### Bluemix run configuration

1. Modify `manifest.yml` by choosing unique name for your host and passing it in place of `<your host name>`.
2. Run:
   ```bash
   cf api https://api.ng.bluemix.net
   cf login
   cf push
   ```
   
Application will be available on bluemix.