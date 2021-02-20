# Digiterra Task

Digiterra Task is a made to use the Connio API' s with Python and to connect with `mqtt` and write data to devices..

## Installation

Install `python3-venv` to create virtual environment.

```bash
sudo apt-get install python3-venv
```

Create a virtual environment with `python3-venv` after active this.

```bash
python3 -m venv <venv_name>
source venv/bin/activate
```

Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install `requirements.txt`.

```bash
pip3 install -r requirements.txt
```

Create a `.env` file and enter.

```bash
API_KEY_ID = "<API-KEY-ID>"
API_KEY_SECRET = "<API-KEY-SECRET>"
BROKER_IP = "<BROKER-IP>"
BROKER_PORT = "<BROKER-PORT>"
```

## Usage

```bash
python run.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
