import os, json, time, requests, numpy as np

TNG_API_KEY = os.getenv('TNG_API_KEY', '').strip()
TNG_BASE = 'https://www.tng-project.org/api/'
STATE = 'tng_gas_state.json'
JSONL = 'tng_gas_records.jsonl'
FINAL = 'tng_gas_metallicity_cache.json'


def tng_get(path_or_url, params=None, timeout=120):
    if not TNG_API_KEY:
        raise RuntimeError('TNG_API_KEY not set')
    url = path_or_url if path_or_url.startswith('http') else TNG_BASE + path_or_url.lstrip('/')
    url = url.replace('http://', 'https://')
    r = requests.get(url, headers={'api-key': TNG_API_KEY}, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {
        'next_url': f'{TNG_BASE}TNG100-1/snapshots/99/subhalos/',
        'params': {'limit': 20, 'sfr__gt': 0.0, 'mass_stars__gt': 0.01},
        'pages_done': 0,
        'target_pages': 5,
        'sim': 'TNG100-1',
        'snapshot': 99,
        'field': 'gasmetallicity'
    }


def run_one_page():
    state = load_state()
    written = 0
    if state['next_url'] and state['pages_done'] < state['target_pages']:
        data = tng_get(state['next_url'], params=state['params'] if '?' not in state['next_url'] else None)
        with open(JSONL, 'a') as out:
            for row in data.get('results', []):
                d = tng_get(row['url'])
                zg = float(d.get('gasmetallicity', 0.0) or 0.0)
                zs = float(d.get('starmetallicity', 0.0) or 0.0)
                if zg > 0:
                    out.write(json.dumps({
                        'id': int(d['id']),
                        'gasmetallicity': zg,
                        'starmetallicity': zs,
                        'metallicity': zg,
                        'mass_stars': float(d.get('mass_stars', 0.0) or 0.0),
                        'sfr': float(d.get('sfr', 0.0) or 0.0),
                        'mass_log_msun': float(d.get('mass_log_msun', 0.0) or 0.0)
                    }) + '\n')
                    written += 1
        state['pages_done'] += 1
        state['next_url'] = data.get('next')
        state['params'] = None
        time.sleep(0.05)
    json.dump(state, open(STATE, 'w'))

    records = []
    if os.path.exists(JSONL):
        with open(JSONL) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    vals = np.array([r['metallicity'] for r in records], dtype=float) if records else np.array([])
    meta = {
        'sim': state['sim'],
        'snapshot': state['snapshot'],
        'field': state['field'],
        'pages_done': state['pages_done'],
        'target_pages': state['target_pages'],
        'records': len(records),
        'mean_metallicity': float(vals.mean()) if len(vals) else None,
        'median_metallicity': float(np.median(vals)) if len(vals) else None,
        'mean_Z_solar': float(vals.mean()/0.0127) if len(vals) else None,
        'median_Z_solar': float(np.median(vals)/0.0127) if len(vals) else None,
        'next_url_exists': bool(state['next_url'])
    }
    payload = {'meta': meta, 'records': records}
    with open(FINAL, 'w') as f:
        json.dump(payload, f, indent=2)
    return {'written_this_run': written, **meta}


if __name__ == '__main__':
    print(json.dumps(run_one_page(), indent=2))
