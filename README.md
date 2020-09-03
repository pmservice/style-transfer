# Deprecation

This repository will be archived. Please navigate to: https://github.com/IBM/watson-machine-learning-samples

---

# Style Transfer Sample Application in Python

Merge the power of Watson Machine Learning with an image of your choice to see transfer of styles.

<img src="https://github.com/pmservice/style-transfer/raw/master/static/images/screen.jpg" width="500" />

## Requirements:
- python 3
- pip
- Cloud Foundry Command Line Interface (cf CLI)

User also should have account on IBM Cloud with active us-south region. In us-south region the following services should be prepared:
- IBM Watson Machine Learning (WML). Please note that `Lite` (free) plan is offered.
- IBM Cloud Object Storage (COS). `Lite` plan is offered. After you create COS instance:
   - go to your COS instance in [IBM Cloud Dashboard](https://console.bluemix.net/dashboard),
   - in `Service credentials` tab, click on `New Credential` and add inline configuration parameter: `{"HMAC":true}`,
   - and click `Add`.

   This configuration parameter will add section below to instance credentials which will be used later on,
   ``` 
        "cos_hmac_keys": {
              "access_key_id": "722432c254bc4eaa96e05897bf2779e2",
              "secret_access_key": "286965ac10ecd4de8b44306288c7f5a3e3cf81976a03075c"
         }
   ```
   
## Deployment 

### Initial configuration

1. Clone repository and enter cloned project directory:
   ```bash
   git clone https://github.com/pmservice/style-transfer.git
   cd style-transfer
   ```
2. Update with your services credentials the folowing files: 
 - `vcaps/wml.vcap` (WML)
 - `vcaps/cos.vcap` (COS).

### Deployment and run on local environment

Run:
```bash
pip install -r requirements.txt
python server.py
```

Application will be available at `127.0.0.1:8080`.


### Deployment and run on IBM Cloud (Bluemix)

1. Modify `bx_manifest.yml` by choosing unique name for your host and passing it in place of `<your host name>`.

**Important**: You should update `domain` regarding your region (It is set for US-South). For example for UK region value should be `eu-gb.mybluemix.net`.

2. Install CF command line interface: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html

3. Run:
   ```bash
   cf api https://api.ng.bluemix.net
   cf login
   cf push -f bx_manifest.yml
   ```
   
 **Important**: You should update API URL regarding your region (`https://api.ng.bluemix.net` for US-South). For example for UK region URL should be `https://api.eu-gb.bluemix.net/`.
   
Application will be available on IBM Cloud.
