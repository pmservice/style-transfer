import ibm_boto3
import os
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError


class COSHelper:
    def __init__(self, wml_vcap, cos_vcap, auth_endpoint, service_endpoint):
        api_key = cos_vcap['apikey']
        service_instance_id = cos_vcap['resource_instance_id']
        self.instance_id = wml_vcap['instance_id']

        self.cos = ibm_boto3.resource('s3',
                         ibm_api_key_id=api_key,
                         ibm_service_instance_id=service_instance_id,
                         ibm_auth_endpoint=auth_endpoint,
                         config=Config(signature_version='oauth'),
                         endpoint_url=service_endpoint)

        self.bucket_names = [self.instance_id + '-style-data', self.instance_id + '-style-results']
        for bucket in self.bucket_names:
            try:
                print('Creating bucket "{}"...'.format(bucket))
                self.cos.create_bucket(Bucket=bucket)
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'BucketAlreadyExists':
                    print('Already exists.')
                else:
                    raise ex

        self.data_bucket = self.cos.Bucket(self.bucket_names[0])
        self.results_bucket = self.cos.Bucket(self.bucket_names[1])

    def _get_bucket(self, image_type):
        bucket_name = self.instance_id + '-style-' + image_type
        if not bucket_name in self.bucket_names:
            raise Exception('Forbidden image_type passed.')

        return self.cos.Bucket(bucket_name)

    def key_exists(self, bucket, key):
        objs = list(bucket.objects.filter(Prefix=key))
        return len(objs) > 0 and objs[0].key == key

    def save_local_file(self, filename, image_type, prefix=""):
        bucket = self._get_bucket(image_type)
        if not self.key_exists(bucket, filename):
            file = open("./vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5", "rb")
            bytes = file.read()
            file.close()
            tmp_file_name = 'tmp'
            file = open(tmp_file_name, "wb")
            file.write(bytes)
            file.close()
            bucket.upload_file(tmp_file_name, prefix + filename)
            os.remove(tmp_file_name)
            print('{} is uploaded to cos.'.format(prefix + filename))

    def save_image(self, file, filename, image_type, prefix=""):
        bucket = self._get_bucket(image_type)
        tmp_file_name = 'tmp'
        file.save(tmp_file_name)
        bucket.upload_file(tmp_file_name, prefix + filename)
        os.remove(tmp_file_name)
        print('{} is uploaded to cos.'.format(prefix + filename))

    def get_image(self, filename, image_type, prefix=""):
        bucket = self._get_bucket(image_type)
        tmp_file_name = 'tmp'
        bucket.download_file(prefix + filename, tmp_file_name)

        file = open(tmp_file_name, "rb")
        data = file.read()
        file.close()

        os.remove(tmp_file_name)
        print('{} got from cos.'.format(filename))
        return data

    def delete_image(self, filename, image_type, prefix=""):
        bucket = self._get_bucket(image_type)
        bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': prefix + filename
                    }
                ]
            }
        )
        print('{} is deleted from cos.'.format(prefix + filename))