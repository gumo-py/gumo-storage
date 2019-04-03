import datetime
import base64
from gumo.core import get_google_oauth_credential


class SignedURLFactory:
    _credential = None

    @classmethod
    def get_credential(cls):
        if cls._credential is None:
            cls._credential = get_google_oauth_credential()

        return cls._credential

    def __init__(
            self,
            bucket_name: str,
            blob_path: str,
            http_verb: str = 'GET',
            md5_digest: str = '',
            content_type: str = '',
            expiration_seconds: int = 3600,
    ):
        self._bucket_name = bucket_name
        self._blob_path = blob_path if blob_path.startswith('/') else f'/{blob_path}'
        self._http_verb = http_verb
        self._md5_digest = md5_digest
        self._content_type = content_type

        now = datetime.datetime.now().replace(microsecond=0)
        self._current_timestamp = int(now.timestamp())
        self._expiration = self._current_timestamp + expiration_seconds

    def _string_to_sign(self) -> str:
        info = [
            self._http_verb,
            self._md5_digest,
            self._content_type,
            str(self._expiration),
            f'/{self._bucket_name}{self._blob_path}'
        ]

        return '\n'.join(info)

    def build(self):
        credential = self.get_credential()

        signer_email = credential.signer_email
        signature = credential.sign_bytes(self._string_to_sign().encode('ascii'))
        encoded_signature = base64.b64encode(signature).decode('ascii')
        escaped_signature = encoded_signature.replace('+', '%2B').replace('/', '%2F')

        base_url = f'https://storage.googleapis.com/{self._bucket_name}{self._blob_path}'
        params = '&'.join([
            f'GoogleAccessId={signer_email}',
            f'Expires={self._expiration}',
            f'Signature={escaped_signature}',
        ])

        return f'{base_url}?{params}'


def build_signed_url(
        bucket_name: str,
        blob_path: str,
        http_verb: str = 'GET',
        md5_digest: str = '',
        content_type: str = '',
        expiration_seconds: int = 3600,
):
    return SignedURLFactory(
        bucket_name=bucket_name,
        blob_path=blob_path,
        http_verb=http_verb,
        md5_digest=md5_digest,
        content_type=content_type,
        expiration_seconds=expiration_seconds,
    ).build()
