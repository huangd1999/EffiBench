from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
from tqdm import tqdm

batch_size = 8

def construct_prompt_template(inputs, model, tokenizer):
    tokenizer.pad_token = tokenizer.eos_token
    input_tokens = tokenizer.batch_encode_plus(
        inputs,
        padding=True,
        return_tensors="pt",
    ).to(model.device)
    for t in input_tokens:
        if torch.is_tensor(input_tokens[t]):
            input_tokens[t] = input_tokens[t].to(model.device)

    try:
        sequences = model.generate(
            **input_tokens, max_new_tokens=512, do_sample=True
        )
        generated_texts = tokenizer.batch_decode(sequences, skip_special_tokens=True)
        for i in range(len(generated_texts)):
            if inputs[i] in generated_texts[i]:
                generated_texts[i] = generated_texts[i].replace(inputs[i], "")
    except:
        generated_texts = ["" for i in range(len(inputs))]

    return generated_texts

with open("../prompts/prompt.txt", "r") as f:
    text = f.read()


# Function to fetch completion
def fetch_completion(data_entry_lists, model, tokenizer):
    global text
    inputs_batchs = []
    for data_entry in data_entry_lists:
        test_case = data_entry["small_test_cases"]
        inputs_batchs.append(
                        f"{text}\n"
                        f"# Task description:\n```python\n{data_entry['markdown_description']}\n```\n"
                        f"# Test case:\n```python\n{test_case}\n```"
        )

    completion_lists = construct_prompt_template(inputs_batchs, model, tokenizer)
    for i in range(len(data_entry_lists)):
        data_entry_lists[i]["completion"] = completion_lists[i]

    return data_entry_lists

if __name__ == "__main__":
    checkpoint = "codellama/CodeLlama-70b-Instruct-hf"
    with open("../data/dataset.json", "r") as f:
        dataset = json.load(f)

    model = AutoModelForCausalLM.from_pretrained(
        checkpoint, device_map="auto", trust_remote_code=True, torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)

    for i in tqdm(range(0, len(dataset), batch_size)):
        dataset[i : i + batch_size] = fetch_completion(
            dataset[i : i + batch_size], model, tokenizer
        )

    end_name = checkpoint.split("/")[-1]
    with open(f"./results/{end_name}.json", "w") as f:
        json.dump(dataset, f, indent=4)