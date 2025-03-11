# Custom GPT chatbot

## Overview
This project is designed to provide a robust and scalable application leveraging OpenAI and a vector store. It includes infrastructure provisioning using Terraform (optional) and automated testing with pytest.

## Project Structure
```
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── src                      # Source code
│   ├── __init.py__          # Package initialization
│   ├── app.py               # Main application logic
│   ├── config.toml          # Configuration file
│   └── vector_store.py      # Vector store implementation
├── terraform                # Infrastructure as Code (IaC) with Terraform
│   ├── openai.tf            # OpenAI-related infrastructure
│   ├── provider.tf          # Terraform provider configuration
│   ├── readme.md            # Terraform module documentation
│   └── variables.tf         # Variable definitions
└── tests                    # Unit tests
    ├── __init.py__          # Test package initialization
    ├── test_app.py          # Tests for app.py
    └── test_vector_store.py # Tests for vector_store.py
```

## Prerequisites
- Python 3.x
- Terraform
- OpenAI Or Azure API key 

## Installation
1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd <project_directory>
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Deploying with Terraform (optional)
1. Navigate to the `terraform` directory:
   ```sh
   cd terraform
   ```
2. Initialize Terraform:
   ```sh
   terraform init
   ```
3. Apply the Terraform configuration:
   ```sh
   terraform apply
   ```
## App onfiguration
Modify `src/config.toml` to fit your environment settings.

## Running the Application
To start the application, run:
```sh
streamlit run src/app.py
```

## Running Tests
Execute the test suite with:
```sh
pytest tests/
```

## TODO
- Upgrade OpenAI library: https://github.com/openai/openai-python/discussions/742
- Improve the RAG functionality
- Remove hard coded references to models

## Contributing
Feel free to open an issue or submit a pull request.

## License
[MIT License](LICENSE)

