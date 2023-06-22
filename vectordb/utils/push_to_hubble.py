import uuid
import os
from tempfile import mktemp
import shutil
import sys
import secrets
from shutil import copytree

from pathlib import Path

__resources_path__ = os.path.join(
    Path(os.path.dirname(sys.modules['vectordb'].__file__)).parent.absolute(), 'resources'
)


class EnvironmentVarCtxtManager:
    """a class to wrap env vars"""

    def __init__(self, envs):
        """
        :param envs: a dictionary of environment variables
        """
        self._env_keys_added = envs
        self._env_keys_old = {}

    def __enter__(self):
        for key, val in self._env_keys_added.items():
            # Store the old value, if it exists
            if key in os.environ:
                self._env_keys_old[key] = os.environ[key]
            # Update the environment variable with the new value
            os.environ[key] = str(val)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore the old values of updated environment variables
        for key, val in self._env_keys_old.items():
            os.environ[key] = str(val)
        # Remove any newly added environment variables
        for key in self._env_keys_added.keys():
            os.unsetenv(key)


def get_uri(id: str, tag: str):
    import requests
    from hubble import Auth

    r = requests.get(
        f"https://apihubble.jina.ai/v2/executor/getMeta?id={id}&tag={tag}",
        headers={"Authorization": f"token {Auth.get_auth_token()}"},
    )
    _json = r.json()
    if _json is None:
        print(f'Could not find image with id {id} and tag {tag}')
        return
    _image_name = _json['data']['name']
    _user_name = _json['meta']['owner']['name']
    return f'jinaai+docker://{_user_name}/{_image_name}:{tag}'


def get_random_tag():
    return 't-' + uuid.uuid4().hex[:5]


def get_random_name():
    return 'n-' + uuid.uuid4().hex[:5]


def _push_to_hubble(
        tmpdir: str, name: str, tag: str, verbose: bool, public: bool
) -> str:
    from hubble.executor.hubio import HubIO
    from hubble.executor.parsers import set_hub_push_parser

    secret = secrets.token_hex(8)
    args_list = [
        tmpdir,
        '--tag',
        tag,
        '--no-usage',
        '--no-cache',
    ]
    if verbose:
        args_list.remove('--no-usage')
        args_list.append('--verbose')
    if not public:
        args_list.append('--secret')
        args_list.append(secret)
        args_list.append('--private')

    args = set_hub_push_parser().parse_args(args_list)

    push_envs = (
        {'JINA_HUBBLE_HIDE_EXECUTOR_PUSH_SUCCESS_MSG': 'true'} if not verbose else {}
    )
    # return 'a' + ':' + tag

    with EnvironmentVarCtxtManager(push_envs):
        executor_id = HubIO(args).push().get('id')
        return executor_id + ':' + tag


def push_vectordb_to_hubble(
        vectordb_name,
        definition_file_path,
) -> str:
    tmpdir = mktemp()
    image_name = get_random_name()
    tag = get_random_name()
    copytree(os.path.join(__resources_path__, 'jcloud_exec_template'), tmpdir)
    shutil.copy(definition_file_path, os.path.join(tmpdir, 'vectordb_app.py'))
    # replace `vectordb_name` in `vectordb_app`
    with open(os.path.join(tmpdir, 'executor.py'), encoding='utf-8') as f:
        content = f.read()

    content = content.replace('from vectordb_app import db', f'from vectordb_app import {vectordb_name}')
    content = content.replace('class VectorDBExecutor(db._executor_cls):',
                              f'class VectorDBExecutor({vectordb_name}._executor_cls):')

    with open(os.path.join(tmpdir, 'executor.py'), mode='w', encoding='utf-8') as f:
        f.write(content)

    with open(os.path.join(tmpdir, 'config.yml'), encoding='utf-8') as f:
        content = f.read()

    content = content.replace('vectordb_executor', f'vectordb_executor-{image_name}')

    with open(os.path.join(tmpdir, 'config.yml'), mode='w', encoding='utf-8') as f:
        f.write(content)

    executor_id = _push_to_hubble(tmpdir, image_name, tag, True, False)
    id, tag = executor_id.split(':')
    return get_uri(id, tag)
