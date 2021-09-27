"""
Utility to upload objects to s3.

Dependencies:
    * boto3

Requires AWS key/secret to be set, for details please see
http://boto3.readthedocs.io/en/latest/guide/configuration.html
"""
import six
if six.PY2:
    from cStringIO import InputType, OutputType, StringIO
    from StringIO import StringIO as StringIOType

    already_stringio = (InputType, OutputType, StringIOType)
else:
    from io import StringIO, BytesIO
    already_stringio = (StringIO,)

from gzip import GzipFile
from io import SEEK_SET

try:
    import ujson as json
except ImportError:
    import json


from link.utils import pd


class S3Writer(object):

    _transfer_config = None
    S3_CHUNK_SIZE_BYTES = 16 * 1024 * 1024
    
    @classmethod
    def _get_transfer_config(cls):
        if cls._transfer_config is None:
            import boto3.s3.transfer as transfer
            cls._transfer_config = transfer.TransferConfig(
                    multipart_threshold=cls.S3_CHUNK_SIZE_BYTES,
                    multipart_chunksize=cls.S3_CHUNK_SIZE_BYTES
                    )
        return cls._transfer_config

    @classmethod
    def _serialize_data(cls, data, gzip=False, df_column_names=False,
            gzip_compression_level=6):

        # easy, it's already in a stringio ready to go
        if any([isinstance(data, c) for c in already_stringio]):
            # make sure we reset to beginning, just in case, in preparation of read()
            # must be compatible with StringIO and cStringIO, so can't use reset()
            data.seek(SEEK_SET)
            return data
        
        if six.PY2:
            data_io = StringIO()
        else:
            data_io = BytesIO()

        if gzip:
            io = GzipFile(fileobj=data_io, mode='w', compresslevel=gzip_compression_level)
        else:
            io = data_io

        if any([isinstance(data, c) for c in (dict, list, str)]):
            if six.PY2:
                io.write(json.dumps(data))
            else:
                io.write(str.encode(json.dumps(data)))

        elif (pd is not None) and (isinstance(data, pd.DataFrame) or isinstance(data, pd.Series)):
            if six.PY2:
                data.to_csv(io, index=False, header=df_column_names)
            else:
                io.write(str.encode(data.to_csv(index=False, header=df_column_names)))
                
        else:
            io.write(str(data))

        if gzip:
            io.close()

        data_io.seek(SEEK_SET)
        return data_io

    @classmethod
    def upload(cls, data, bucket_name, key_name, aws_access_key_id=None, aws_secret_access_key=None,
            gzip=False, df_column_names=False, gzip_compression_level=6):
        # in here so as not to create a dependency on boto3 for the entire link package
        import boto3
        s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        transfer_config = cls._get_transfer_config()

        io = cls._serialize_data(data, gzip=gzip, df_column_names=df_column_names,
                gzip_compression_level=gzip_compression_level)
        s3_client.upload_fileobj(io, Bucket=bucket_name, Key=key_name, Config=transfer_config)

