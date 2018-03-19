from watson_machine_learning_client import WatsonMachineLearningAPIClient

class WMLHelper:
    def __init__(self, wml_vcap, cos_vcap, auth_endpoint, service_endpoint):
        self.client = WatsonMachineLearningAPIClient(wml_vcap.copy())
        self.cos_vcap = cos_vcap
        self.auth_endpoint = auth_endpoint
        self.service_endpoint = service_endpoint
        self.instance_id = wml_vcap["instance_id"]

    def _store_definition(self, style_image, base_image, iteration=1):
        print('Storing definition: {} {} {}'.format(style_image, base_image, iteration))
        definition_metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "Style transfer between {} and {}".format(style_image, base_image),
            self.client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "test@pl.ibm.com",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.5",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python style_transfer.py {} {} {}_ --iter {}".format(base_image, style_image, base_image.split(".")[0], iteration)
        }

        filename_definition = 'data/STYLE.zip'

        return self.client.repository.store_definition(filename_definition, definition_metadata)

    def delete_definition(self, definition_uid):
        print('Deleting definition: {}'.format(definition_uid))
        self.client.repository.delete(definition_uid)

    def _store_experiment(self, definition_url):
        print('Storing experiment: {}'.format(definition_url))
        experiment_metadata = {
            self.client.repository.ExperimentMetaNames.NAME: "Experimental style transfer",
            self.client.repository.ExperimentMetaNames.AUTHOR_EMAIL: "test@pl.ibm.com",
            self.client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: {
                "connection": {
                    "endpoint_url": self.service_endpoint,
                    "aws_access_key_id": self.cos_vcap['cos_hmac_keys']['access_key_id'],
                    "aws_secret_access_key": self.cos_vcap['cos_hmac_keys']['secret_access_key']
                },
                "source": {
                    "bucket": self.instance_id + "-style-data",
                },
                "type": "s3"
            },
            self.client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: {
                "connection": {
                    "endpoint_url": self.service_endpoint,
                    "aws_access_key_id": self.cos_vcap['cos_hmac_keys']['access_key_id'],
                    "aws_secret_access_key": self.cos_vcap['cos_hmac_keys']['secret_access_key']
                },
                "target": {
                    "bucket": self.instance_id + "-style-results",
                },
                "type": "s3"
            },
            self.client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
                {
                    "name": "style transfer",
                    "training_definition_url": definition_url,
                    "compute_configuration": {"name": "p100"}
                }
            ]
        }

        return self.client.repository.store_experiment(meta_props=experiment_metadata)

    def delete_experiment(self, experiment_uid):
        print('Deleting experiment: {}'.format(experiment_uid))
        self.client.repository.delete(experiment_uid)

    def delete_run(self, run_uid):
        print('Deleting run: {}'.format(run_uid))
        self.client.training.delete(run_uid)