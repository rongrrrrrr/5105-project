import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import List, Dict
import logging
import yaml
import os
import time
import concurrent.futures
import json
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from tqdm import tqdm

@dataclass
class AnnotationConfig:
    api_keys: List[str]
    model_name: str
    max_retries: int = 2
    retry_delay: int = 3
    safety_settings: Dict = None

    def __post_init__(self):
        if not self.safety_settings:
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

class GeminiAnnotator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.current_api_key_index = 0
        self.prompts = self._load_prompts()
        self._setup_logging()

    def _load_config(self, config_path: str) -> AnnotationConfig:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return AnnotationConfig(
            api_keys=config_data['google']['api_keys'],
            model_name=config_data['google']['model']
        )

    def _load_prompts(self) -> Dict[str, str]:
        prompts = {}
        prompt_files = {
            'default': '../data/prompt/annotation/user_prompt.txt',
            'system': '../data/prompt/annotation/system_prompt.txt'
        }
        for key, path in prompt_files.items():
            with open(path, 'r', encoding='utf-8') as f:
                prompts[key] = f.read()
        return prompts

    def _setup_logging(self):
        log_dir = Path('src/log/llm_label')
        log_dir.mkdir(parents=True, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f'llm_label_{current_time}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )

    def _configure_model(self) -> genai.GenerativeModel:
        genai.configure(api_key=self.config.api_keys[self.current_api_key_index])
        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        return genai.GenerativeModel(
            self.config.model_name,
            safety_settings=self.config.safety_settings,
            system_instruction=self.prompts['system'],
            generation_config=generation_config
        )

    def _rotate_api_key(self):
        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.config.api_keys)
        logging.info(f"Rotating API key to: {self.config.api_keys[self.current_api_key_index]}")

    def _convert_to_json(self, text_content: str) -> str:
        lines = []
        for line in text_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                word = ' '.join(parts[:-1])
                label = parts[-1]
                lines.append((word, label))

        if not lines:
            raise ValueError("No valid labeled lines found in the response")

        current_text = []
        entity_spans = []
        current_position = 0

        for word, label in lines:
            if current_text:
                current_position += 1  # Account for space
            current_text.append(word)
            entity_spans.append({
                "start": current_position,
                "end": current_position + len(word),
                "text": word,
                "labels": [label]
            })
            current_position += len(word)

        return json.dumps({
            "text": ' '.join(current_text),
            "entity": entity_spans
        }, ensure_ascii=False, indent=2)

    def _process_single_text(self, text: str, index: int, model: genai.GenerativeModel) -> tuple:
        for attempt in range(self.config.max_retries):
            try:
                chat = model.start_chat(history=[{"role": "user", "parts": self.prompts['default']}])
                response = chat.send_message(text)
                content = response.candidates[0].content.parts[0].text if response.candidates else ''
                content = content.replace('```', '')
                return index, self._convert_to_json(content)
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed for text {index}: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    self._rotate_api_key()
                    model = self._configure_model()
                    time.sleep(self.config.retry_delay)
                else:
                    return index, json.dumps({"error": f"Failed to process text {index}"})

    def process_texts(self, texts: List[str], output_dir: str, filename: str, max_workers: int = 2):
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        model = self._configure_model()
        results = [None] * len(texts)
        logging.info(f"Processing file: {filename}")

        with tqdm(total=len(texts), desc=f"Annotating {filename}") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._process_single_text, text, idx, model): idx
                    for idx, text in enumerate(texts)
                }
                for future in concurrent.futures.as_completed(futures):
                    idx, content = future.result()
                    results[idx] = content
                    pbar.update(1)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('[\n' + ',\n'.join(r for r in results if r) + '\n]')
        logging.info(f"[✅] Annotation complete → {output_path}")
