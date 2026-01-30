#!/usr/bin/env python3
"""Generate async version of client.py and request.py."""
import subprocess
import os

DISCLAIMER = "# THIS IS AUTO GENERATED COPY. DON'T EDIT BY HANDS #"
DISCLAIMER = f'{"#" * len(DISCLAIMER)}\n{DISCLAIMER}\n{"#" * len(DISCLAIMER)}\n\n'

REQUEST_METHODS = ('_request_wrapper', 'get', 'post', 'retrieve', 'download', 'graphql')


def gen_request(output_request_filename: str) -> None:
    """Generate async version of request.py."""
    with open('zvuk_music/utils/request.py', 'r', encoding='UTF-8') as f:
        code = f.read()

    code = code.replace('import requests', 'import asyncio\nimport aiohttp\nimport aiofiles')

    # order make sense
    code = code.replace('resp.content', 'content')
    code = code.replace(
        'resp = requests.request(*args, **kwargs)',
        f'async with aiohttp.request(*args, **kwargs) as _resp:\n{" " * 16}resp = _resp\n{" " * 16}content = await resp.read()',
    )

    code = code.replace('except requests.Timeout', 'except asyncio.TimeoutError')
    code = code.replace('except requests.RequestException', 'except aiohttp.ClientError')
    code = code.replace('resp.status_code', 'resp.status')

    for method in REQUEST_METHODS:
        code = code.replace(f'def {method}', f'async def {method}')
        code = code.replace(f'self.{method}(', f'await self.{method}(')

    code = code.replace('proxies=self.proxies', 'proxy=self.proxy_url')
    # Handle timeout conversion for aiohttp (both single and double quotes)
    code = code.replace(
        'kwargs["timeout"] = self._timeout',
        f'kwargs["timeout"] = aiohttp.ClientTimeout(total=self._timeout)\n{" " * 8}else:\n{" " * 12}kwargs["timeout"] = aiohttp.ClientTimeout(total=kwargs["timeout"])',
    )
    code = code.replace(
        "kwargs['timeout'] = self._timeout",
        f"kwargs['timeout'] = aiohttp.ClientTimeout(total=self._timeout)\n{' ' * 8}else:\n{' ' * 12}kwargs['timeout'] = aiohttp.ClientTimeout(total=kwargs['timeout'])",
    )

    # download method
    code = code.replace('with open', 'async with aiofiles.open')
    code = code.replace('f.write', 'await f.write')

    # docs
    code = code.replace('`requests`', '`aiohttp`')
    code = code.replace('requests.request', 'aiohttp.request')

    code = DISCLAIMER + code
    with open(output_request_filename, 'w', encoding='UTF-8') as f:
        f.write(code)


def gen_client(output_client_filename: str) -> None:
    """Generate async version of client.py."""
    with open('zvuk_music/client.py', 'r', encoding='UTF-8') as f:
        code = f.read()

    code = code.replace('class Client:', 'class ClientAsync:')
    code = code.replace(
        'from zvuk_music.utils.request import', 'from zvuk_music.utils.request_async import'
    )

    # Make all public methods async
    lines = code.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        # Skip static methods and __init__
        if '    def ' in line and '__init__' not in line and '@staticmethod' not in lines[max(0, i-1)]:
            new_lines.append(line.replace('def ', 'async def '))
        else:
            new_lines.append(line)
    code = '\n'.join(new_lines)

    for method in REQUEST_METHODS:
        code = code.replace(f'self._request.{method}', f'await self._request.{method}')

    # Internal method calls that need await
    internal_methods = [
        'get_profile', 'get_tracks', 'get_stream_urls', 'get_releases',
        'get_artists', 'get_playlists', 'get_podcasts', 'get_episodes',
        'add_to_collection', 'remove_from_collection',
        'add_to_hidden', 'remove_from_hidden',
    ]
    for method in internal_methods:
        # Handle assignment, return, and standalone call patterns
        code = code.replace(f' = self.{method}(', f' = await self.{method}(')
        code = code.replace(f'return self.{method}(', f'return await self.{method}(')
        # Standalone calls (line starts with whitespace + self.method)
        code = code.replace(f'        self.{method}(', f'        await self.{method}(')

    # Add asyncio import at the top
    code = code.replace(
        '"""Асинхронный клиент Zvuk Music API."""',
        '"""Асинхронный клиент Zvuk Music API."""\n\nimport asyncio'
    )

    # Fix docstring
    code = code.replace('Синхронный клиент', 'Асинхронный клиент')
    code = code.replace('"Client"', '"ClientAsync"')

    code = DISCLAIMER + code
    with open(output_client_filename, 'w', encoding='UTF-8') as f:
        f.write(code)


if __name__ == '__main__':
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    request_filename = 'zvuk_music/utils/request_async.py'
    client_filename = 'zvuk_music/client_async.py'

    print(f"Generating {request_filename}...")
    gen_request(request_filename)

    print(f"Generating {client_filename}...")
    gen_client(client_filename)

    # Try to format with ruff if available (skip auto-fix which can break imports)
    try:
        for file in (request_filename, client_filename):
            subprocess.run(['ruff', 'format', '--quiet', file], check=False)
        print("Files formatted with ruff.")
    except FileNotFoundError:
        print("ruff not found, skipping formatting.")

    print("Done!")
