# GitHub Q&A Chatbot

Helping you understand and navigate GitHub repositories with ease.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [TODO](#todo)

## Overview

The GitHub Q&A Chatbot is designed to assist users in understanding the content, structure, and other details of a GitHub repository. By leveraging natural language processing, this chatbot answers questions related to the repo, aiding both newcomers and seasoned developers.

## Features

- **Natural Language Understanding**: Ask questions in plain English.
- **Repo Navigation**: Get guidance on where specific files or sections are located.
- **Issue Information**: Fetch details about open, closed, and specific issues.

## Installation

1. Clone this repository:
```bash
git clone git@github.com:mmathew23/github-QA.git
```

2. Change directory
```bash
cd github-QA
```

3. Install requirements
```bash
pip install -r requirements.txt
```

4. Edit .env file
```bash
mv .env.template .env
```
Add your Github token and OpenAI API keys. If not using OpenAI model will default to llama cpp.

## Usage

```python
python qa.py
```

## License
Distributed under the MIT License. See LICENSE for more information.


## TODO
- [x] Basic Functionality
- [ ] Add Github Discussions
- [ ] Choice of API
- [ ] Choice of Indexes
