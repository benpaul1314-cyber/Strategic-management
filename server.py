"""Journal search using public Crossref metadata; Python 3.10+, no dependencies."""
import concurrent.futures
import json
import os
import re
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit, quote
from urllib.request import Request, urlopen

JOURNALS = {
    'asq': ('Administrative Science Quarterly', '0001-8392'),
    'mnsc': ('Management Science', '0025-1909'),
    'orsc': ('Organization Science', '1047-7039'),
    'smj': ('Strategic Management Journal', '0143-2095'),
}

def plain(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', value or '')).split())

def normalize(item, journal):
    date = next((item.get(k, {}).get('date-parts', [[]])[0] for k in
                 ('published', 'published-print', 'published-online', 'issued')
                 if item.get(k, {}).get('date-parts', [[]])[0]), [])
    doi = item.get('DOI', '')
    return {'title': plain((item.get('title') or ['无标题'])[0]),
            'authors': ', '.join(' '.join(filter(None, [a.get('given'), a.get('family')]))
                                 or a.get('name', '') for a in item.get('author', [])),
            'year': date[0] if date else None, 'journal': journal,
            'abstract': plain(item.get('abstract')), 'doi': doi,
            'url': 'https://doi.org/' + quote(doi, safe='/') if doi else '',
            'score': item.get('score', 0)}

def fetch_journal(key, query, start, end, sort, page):
    name, issn = JOURNALS[key]
    filters = ['type:journal-article']
    if start: filters.append('from-pub-date:' + start + '-01-01')
    if end: filters.append('until-pub-date:' + end + '-12-31')
    params = {'query': query, 'rows': 10, 'offset': (page - 1) * 10,
              'filter': ','.join(filters), 'sort': 'published' if sort == 'newest' else 'relevance',
              'order': 'desc'}
    req = Request('https://api.crossref.org/journals/' + issn + '/works?' + urlencode(params),
                  headers={'User-Agent': 'StrategicJournalSearch/1.0', 'Accept': 'application/json'})
    with urlopen(req, timeout=20) as response:
        data = json.load(response)['message']
    return {'items': [normalize(i, name) for i in data.get('items', [])],
            'total': data.get('total-results', 0)}

def search(params, fetch=fetch_journal):
    query = params.get('q', [''])[0].strip()
    if not query or len(query) > 500: raise ValueError('请输入 1–500 个字符的关键词。')
    keys = list(dict.fromkeys(params.get('journal', list(JOURNALS))))
    if not keys or any(k not in JOURNALS for k in keys): raise ValueError('期刊选择无效。')
    start, end = (params.get(k, [''])[0] for k in ('from', 'to'))
    for year in (start, end):
        if year and (not re.fullmatch(r'\d{4}', year) or not 1600 <= int(year) <= 2200):
            raise ValueError('年份须为 1600–2200 之间的四位数字。')
    if start and end and start > end: raise ValueError('起始年份不能晚于结束年份。')
    sort = params.get('sort', ['relevance'])[0]
    if sort not in ('relevance', 'newest'): raise ValueError('排序方式无效。')
    try: page = int(params.get('page', ['1'])[0])
    except ValueError: raise ValueError('页码无效。') from None
    if not 1 <= page <= 100: raise ValueError('页码须为 1–100。')
    items, errors, total, more = [], [], 0, False
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch, k, query, start, end, sort, page): k for k in keys}
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                items.extend(result['items'])
                total += result['total']
                more = more or page * 10 < result['total']
            except Exception:
                errors.append(JOURNALS[key][0] + '：元数据服务暂时无法访问，请稍后重试或使用期刊入口。')
    unique = {}
    for item in items: unique.setdefault(item['doi'] or (item['title'], item['journal']), item)
    items = sorted(unique.values(), key=lambda i: (i['year'] or 0) if sort == 'newest' else i['score'], reverse=True)
    return {'items': items, 'total': total, 'errors': errors, 'page': page,
            'hasMore': bool(items) and more and page < 100}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / 'web'), **kwargs)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path != '/api/search': return super().do_GET()
        try:
            result = search(parse_qs(parsed.query, keep_blank_values=True))
            status = 502 if result['errors'] and not result['items'] else 200
        except ValueError as exc:
            result, status = {'error': str(exc)}, 400
        payload = json.dumps(result, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    print(f'Journal search listening on port {port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
