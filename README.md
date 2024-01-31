# Setting up Developer Environment

## Creating Developer Environment
For Mac(Intel)

### Steps

1. Start Docker daemon, install anaconda3

2. Create an environment for Feast, selecting python 3.9. Activate the environment: 
```
conda create --name feast python=3.9
conda activate feast
```

3. Install dependencies:
```
pip install pip-tools
brew install mysql@8.0 (latest - mysql@8.3 version fails the dev env)
brew install xz protobuf openssl zlib
pip install cryptography -U
conda install protobuf
conda install pymssql
pip install -e ".[dev]"
make install-protoc-dependencies 
make install-python-ci-dependencies PYTHON=3.9
```

4. Run unit tests:
```
make test-python
```


