from setuptools import setup

setup(
    name="navvy",
    version="1.0.0",
    author="Rofly António",
    python_requires='>=3.6',
    install_requires=[
        'annotated-types==0.7.0',
        'anyio==4.6.2.post1',
        'certifi==2024.8.30',
        'distro==1.9.0',
        'gitdb==4.0.11',
        'GitPython==3.1.43',
        'h11==0.14.0',
        'httpcore==1.0.7',
        'httpx==0.27.2',
        'idna==3.10',
        'jiter==0.7.1',
        'openai==1.54.5',
        'pydantic==2.9.2',
        'pydantic_core==2.23.4',
        'smmap==5.0.1',
        'sniffio==1.3.1',
        'tqdm==4.67.0',
        'typing_extensions==4.12.2',
    ],
)