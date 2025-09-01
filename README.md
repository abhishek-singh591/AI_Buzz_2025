# AI Buzz Submission

## Idea Details
- Team Name: DocuGenie
- Idea Title: AI-Enabled Automatic Documentation System for Internal Qualcomm Repositories.​
- Idea url: [Click here](https://aibuzz.qualcomm.com/idea/4507)
- Team Members
  - Abhishek Kumar Singh (sabhis)
  - Sharvari Medhe (smedhe)
  - Tanisha Chawada (tchawada)
- Programming language used: 
- AI Hub Model links
  - https://huggingface.co/Qwen/Qwen3-14B
  - https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
- Target device
  - [x] PC
  - [ ] Mobile
  - [ ] Others: <!-- Specify the device --> 


## Implementation Summary
- This application aims to automate the documentation process for internal repositories in Qualcomm. It utilizes AI-powered tools, specifically the Llama 3.1 and Qwen-3-14B models, to generate comprehensive documentation based on the existing content of the repositories.
- The application collects data from the internal repositories and leverages the AI models to analyze and generate relevant documentation. It then organizes and presents the generated documentation in a structured format, making it easy for users to access and understand.
- It also has the capability to enrich the documentation with relevant images and visualizations. This integration allows the application to provide a more comprehensive and visually appealing documentation experience.
- Additionally, the application can perform semantic search on the generated documentation, enabling users to quickly find specific pieces of information based on their queries. Overall, this AI-powered application aims to streamline the documentation process, improve accessibility, and enhance the overall user experience.

### Models Used:
1. Qwen-3-14B: A large language model developed by Tencent AI Lab, specifically designed for Chinese text generation tasks, including semantic search and question-answering. The model has a 3.14-billion parameter size and is capable of generating human-like text.
2. Llama-3.1-8B-Instruct: A large language model for instruction tuning developed by Meta AI, specifically designed for various tasks, including semantic search and question-answering. The model has an 8-billion parameter size and is capable of generating human-like text based on given instructions.
3. ImagineChat: The Imagine Chat model is a pre-trained large language model (LLM) specifically designed for text generation tasks. This model is useful for tasks such as chatbots, question answering, and text summarization. It is a powerful tool for generating human-like text and can be integrated into various applications that require natural language processing capabilities.




## Installation & Setup steps

## 📋 Prerequisites

- Python 3.10 installed
- GPU needed (Developing for AIC 100)
- Git installed
- API Key and Endpoint from [Cirrascale Inference Cloud](https://aisuite.cirrascale.com/account/api-keys)

---

## ⚙️ Setup Instructions
### 1️⃣ Install Python 3.10 

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv
```
### Create and Activate Virtual Environment
```bash
python3.10 -m venv <env_name>
source <env_name>/bin/activate
```
### 3️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo>.git
```

### 🔐 API Configuration
Create your Imagine API Key and Endpoint from Cirrascale.

Then, create a .env file in the root directory:
```bash
IMAGINE_API_KEY=your_api_key_here
IMAGINE_API_ENDPOINT=https://your_endpoint_here
```
### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 🚀 Run the Documentation Generator
We are using Qwen3-14B : https://huggingface.co/Qwen/Qwen3-14B model as default model.
```bash
bash run.sh --repo https://github.com/<your-username>/<your-repo> --model <huggingface-model-path>
```

### 🌐 View the Streamlit App
Once the app launches, open the URL provided in your terminal:

```bash
http://localhost:8501
```


## Expected output / behaviour
Upon execution, the system scans the specified repository directory, identifies supported source files (e.g., .py, .js, .md, etc.), and loads their contents. These files are then split into context-aware chunks using a recursive text splitter, preserving metadata such as relative file paths for traceability. The final output is a list of structured Document objects, each representing a meaningful segment of code or text, ready for embedding and retrieval. This enables accurate and context-grounded responses in downstream applications like chatbots or semantic search.


## Future Goals

1. Enhance the User Interface for Improved Experience Refactor the current UI layout to prioritize clarity, responsiveness, and accessibility. This includes optimizing component placement, improving visual hierarchy, and ensuring intuitive navigation across all features.

2. Resolve Firewall Restrictions Affecting Image Rendering API Access Investigate and address network-level constraints that are preventing successful communication with the image rendering API. 


## Submission Checklist
- [x] Recorded video
- [x] Readme updated with required fields
- [x] Dependency installation scripts added
- [x] Startup script added
- [x] Idea url updated in Readme