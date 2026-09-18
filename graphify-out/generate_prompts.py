import json
from pathlib import Path

spec_text = Path('/home/hossein/.gemini/config/skills/graphify/references/extraction-spec.md').read_text(encoding='utf-8')
parts = spec_text.split('```')
prompt_template = parts[1].strip() if len(parts) > 1 else spec_text.strip()

chunks = json.loads(Path('graphify-out/.graphify_chunks.json').read_text(encoding='utf-8'))
cwd = Path('.').resolve()

subagent_prompts = []
for i, chunk in enumerate(chunks, 1):
    chunk_num = f"{i:02d}"
    chunk_path = str(cwd / 'graphify-out' / f".graphify_chunk_{chunk_num}.json")
    file_list = '\n'.join(chunk)
    
    # Replace exact placeholders
    prompt = prompt_template
    # Replace chunk header and file list line
    prompt = prompt.replace('Files (chunk CHUNK_NUM of TOTAL_CHUNKS):\nFILE_LIST', f'Files (chunk {i} of {len(chunks)}):\n{file_list}')
    prompt = prompt.replace('DEEP_MODE (if --mode deep was given)', 'DEEP_MODE: false')
    prompt = prompt.replace('CHUNK_PATH', chunk_path)
    prompt = prompt.replace('<FILE_LIST path verbatim>', '<path from file list verbatim>')
    
    subagent_prompts.append({'chunk_num': chunk_num, 'chunk_path': chunk_path, 'prompt': prompt})

Path('graphify-out/.graphify_subagent_prompts.json').write_text(json.dumps(subagent_prompts, indent=2, ensure_ascii=False), encoding='utf-8')
print('Regenerated prompts cleanly for', len(subagent_prompts), 'subagents')
