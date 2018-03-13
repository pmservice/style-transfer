# Transfer Style - Sample App in Python

Requirements:
- python 3.5
- pip
- Cloud Foundry Command Line Interface (cf CLI)

User also should have account on Bluemix with active us-south region. In us-south region the following services should be prepared:
- IBM Watson Machine Learning (wml). Please note that `Lite` (free) plan is offered.
- IBM Cloud Object Storage (cos). `Lite` plan is offered. After you create COS instance:
   - go to your COS dashboard,
   - in `Service credentials` tab, click on `New Credential` and add inline configuration parameter: `{"HMAC":true}`,
   - and click `Add`.

   This configuration parameter will add section below to instance credentials which will be used later on,
   ``` 
        "cos_hmac_keys": {
              "access_key_id": "722432c254bc4eaa96e05897bf2779e2",
              "secret_access_key": "286965ac10ecd4de8b44306288c7f5a3e3cf81976a03075c"
         }
   ```
   
## Deploy2Bluemix - Fast track to working application

1. Create application using following button:

   [![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/pmservice/style-transfer&appName=style-transfer&branch=master)
2. Choose name for application, region and organization. Configure integration tools. Click `Deploy`.
3. Open github repository by clicking `Git` tile in `CODE` section.
4. In github edit `vcaps/cos.vcap` with COS credentials.
5. Go to your Bluemix account and restart your application.
6. Click `View app` to go to your application.

## Initial configuration

1. Clone repository and enter cloned project directory:
   ```bash
   git clone https://github.com/pmservice/style-transfer.git
   cd style-transfer
   ```
2. Update with your services credentials the folowing files: 
 - `vcaps/wml.vcap` (wml)
 - `vcaps/cos.vcap` (cos).

### Local run configuration

Run:
```bash
pip install -r requirements.txt
python server.py
```

Application will be available at `127.0.0.1:8080`.


### Bluemix run configuration

1. Modify `manifest.yml` by choosing unique name for your host and passing it in place of `<your host name>`.
2. Run:
   ```bash
   cf api https://api.ng.bluemix.net
   cf login
   cf push -f bx_manifest.yml
   ```
   
Application will be available on bluemix.
