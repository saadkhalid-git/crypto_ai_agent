from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_dataset

def fine_tune():
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
    model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")

    dataset = load_dataset("text", data_files={"train": "data/crypto_banter_content.txt"})
    tokenized_dataset = dataset.map(lambda x: tokenizer(x["text"], truncation=True, padding="max_length"), batched=True)

    training_args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=4,
        num_train_epochs=3,
        save_steps=10_000,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
    )

    trainer.train()
    trainer.save_model("models/fine_tuned_llama3")