from gumo.storage.infrastructure import SignedURLFactory


def test_signed_url_factory():
    bucket_name = 'gumo-example'
    blob_path = '/LGTM_space.gif'
    url = SignedURLFactory(
        bucket_name=bucket_name,
        blob_path=blob_path
    ).build()

    assert url.startswith(f'https://storage.googleapis.com/{bucket_name}{blob_path}?')
    assert url.index('GoogleAccessId=') > 0
    assert url.index('Expires=') > 0
    assert url.index('Signature=') > 0
    # assert url == ''
