# Azure Models Test Commands

## Quick One-Liner Tests

### Test all models quickly
python quick_test.py

### Test specific model
python quick_test.py gpt-4.1
python quick_test.py grok-3 
python quick_test.py deepseek-r1

### Individual model tests
python -c "import azure_models; client = azure_models.get_model_client('gpt-4.1'); print('GPT-4.1:', client.create_chat_completion([{'role': 'user', 'content': 'Hello!'}]).choices[0].message.content)"

python -c "import azure_models; client = azure_models.get_model_client('grok-3'); print('Grok-3:', client.create_chat_completion([{'role': 'user', 'content': 'Hello!'}]).choices[0].message.content)"

python -c "import azure_models; client = azure_models.get_model_client('deepseek-r1'); print('DeepSeek R1:', client.create_chat_completion([{'role': 'user', 'content': 'Hello!'}]).choices[0].message.content)"

## Using the Test Scripts

### Test all models with comprehensive output
python test_models.py

### Test specific model
python test_models.py --model gpt-4.1
python test_models.py --model grok-3
python test_models.py --model deepseek-r1

### Test with streaming
python test_models.py --streaming
python test_models.py --model gpt-4.1 --streaming
python test_models.py --model grok-3 --streaming

### Test with custom prompt
python test_models.py --custom-prompt "Explain quantum computing in one sentence"
python test_models.py --model deepseek-r1 --custom-prompt "Write a haiku about AI"

### Performance comparison
python test_models.py --custom-prompt "Count to 10"

## Model Information Commands

### List available models
python test_models.py --list-models
python -c "import azure_models; print('Available models:', azure_models.get_available_models())"

### Check streaming support
python -c "import azure_models; print('Streaming models:', azure_models.get_streaming_models())"

### Get detailed model info
python -c "import azure_models; print('GPT-4.1 info:', azure_models.get_model_info('gpt-4.1'))"
python -c "import azure_models; print('Grok-3 info:', azure_models.get_model_info('grok-3'))"
python -c "import azure_models; print('DeepSeek R1 info:', azure_models.get_model_info('deepseek-r1'))"

## Streaming Tests

### Test streaming with GPT-4.1
python -c "import azure_models; client = azure_models.get_model_client('gpt-4.1'); response = client.create_chat_completion([{'role': 'user', 'content': 'Count to 5 slowly'}], stream=True); print('Streaming response:'); [print(chunk, end='', flush=True) for chunk in response]; print()"

### Test streaming with Grok-3
python -c "import azure_models; client = azure_models.get_model_client('grok-3'); response = client.create_chat_completion([{'role': 'user', 'content': 'Tell me a short joke'}], stream=True); print('Streaming response:'); [print(chunk, end='', flush=True) for chunk in response]; print()"

### Test streaming with DeepSeek R1
python -c "import azure_models; client = azure_models.get_model_client('deepseek-r1'); response = client.create_chat_completion([{'role': 'user', 'content': 'What is 2+2?'}], stream=True); print('Streaming response:'); [print(chunk, end='', flush=True) for chunk in response]; print()"

## Comparison Tests

### Compare responses to same prompt
python -c "
import azure_models
prompt = 'What is your favorite programming language and why?'
models = ['gpt-4.1', 'grok-3', 'deepseek-r1']
for model in models:
    client = azure_models.get_model_client(model)
    response = client.create_chat_completion([{'role': 'user', 'content': prompt}])
    print(f'{model}: {response.choices[0].message.content}')
    print('-' * 60)
"

### Speed comparison
python -c "
import azure_models
import time
prompt = 'Hello!'
models = ['gpt-4.1', 'grok-3', 'deepseek-r1']
results = []
for model in models:
    start = time.time()
    client = azure_models.get_model_client(model)
    response = client.create_chat_completion([{'role': 'user', 'content': prompt}])
    end = time.time()
    results.append((model, end - start))
    print(f'{model}: {end - start:.2f}s')

print('Speed ranking:')
for i, (model, speed) in enumerate(sorted(results, key=lambda x: x[1]), 1):
    print(f'{i}. {model}: {speed:.2f}s')
"

## Error Testing

### Test with invalid model
python -c "
try:
    import azure_models
    client = azure_models.get_model_client('invalid-model')
except Exception as e:
    print(f'Expected error: {e}')
"

### Test model capabilities
python -c "
import azure_models
models = ['gpt-4.1', 'grok-3', 'deepseek-r1']
for model in models:
    info = azure_models.get_model_info(model)
    print(f'{model}:')
    print(f'  Streaming: {info[\"supports_streaming\"]}')
    print(f'  Features: {info[\"supported_features\"]}')
    print(f'  Max tokens: {info[\"max_tokens_limit\"]}')
    print()
"
