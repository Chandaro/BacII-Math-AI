# Gemma notice

`finetune/adapters/run8-step2400-half/` is a LoRA adapter trained on top of **Gemma 3 12B** (`mlx-community/gemma-3-12b-it-qat-4bit`, a 4-bit MLX conversion of Google's `gemma-3-12b-it-qat`). The base model is not included here; it is downloaded from Hugging Face when you run the scripts.

Gemma is provided under and subject to the Gemma Terms of Use found at https://ai.google.dev/gemma/terms

The adapter is a Model Derivative of Gemma. Use of the adapter, alone or with Gemma, is subject to the Gemma Terms of Use and the Gemma Prohibited Use Policy (https://ai.google.dev/gemma/prohibited_use_policy). Anyone who redistributes it must pass on these terms.

Change made: LoRA fine-tuning (rank 8, last 8 layers, 2,400 steps) on 2,410 Khmer BacII math solutions from `finetune/run8_data/`. The adapter is meant to be used at half strength (`"scale": 10.0` in `adapter_config.json`, already set).
