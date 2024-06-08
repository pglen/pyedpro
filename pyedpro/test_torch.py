# Copy/Paste the contents to a new file demo.py
import torch
from ipex_llm.transformers import AutoModelForCausalLM
from transformers import AutoTokenizer, GenerationConfig
generation_config = GenerationConfig(use_cache = True)

tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b", trust_remote_code=True)
# load Model using ipex-llm and load it to GPU
model = AutoModelForCausalLM.from_pretrained(
    "tiiuae/falcon-7b", load_in_4bit=True, cpu_embedding=True, trust_remote_code=True)
model = model.to('xpu')

# Format the prompt
question = "What is AI?"
prompt = " Question:{prompt}\n\n Answer:".format(prompt=question)
# Generate predicted tokens
with torch.inference_mode():
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to('xpu')
    # warm up one more time before the actual generation task for the first run, see details in `Tips & Troubleshooting`
    # output = model.generate(input_ids, do_sample=False, max_new_tokens=32, generation_config = generation_config)
    output = model.generate(input_ids, do_sample=False, max_new_tokens=32, generation_config = generation_config).cpu()
    output_str = tokenizer.decode(output[0], skip_special_tokens=True)
    print(output_str)
