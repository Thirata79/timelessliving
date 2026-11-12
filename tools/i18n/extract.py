import re, sys, json, os

CJK = re.compile(r'[　-〿぀-ゟ゠-ヿ㐀-䶿一-鿿＀-￯]')
TAG = re.compile(r'<[^>]*>|<!--.*?-->', re.S)

def runs(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'(?is)<script\b.*?</script>', '', s)
    s = re.sub(r'(?is)<style\b.*?</style>', '', s)
    out = []
    # text nodes
    pos = 0
    for m in TAG.finditer(s):
        seg = s[pos:m.start()]
        pos = m.end()
        for piece in seg.split('\n'):
            t = piece.strip()
            if t and CJK.search(t):
                out.append(t)
    seg = s[pos:]
    for piece in seg.split('\n'):
        t = piece.strip()
        if t and CJK.search(t):
            out.append(t)
    # attributes
    for m in re.finditer(r'(?:alt|content|title)="([^"]*)"', s):
        if CJK.search(m.group(1)):
            out.append(m.group(1))
    for m in re.finditer(r'(?is)<title>(.*?)</title>', s):
        if CJK.search(m.group(1)):
            out.append(m.group(1).strip())
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t); uniq.append(t)
    return uniq

if __name__ == '__main__':
    common = set()
    if os.path.exists('tools/common.json'):
        common = set(json.load(open('tools/common.json')).keys())
    for p in sys.argv[1:]:
        rs = [r for r in runs(p) if r not in common]
        print('\n########## %s (%d new runs)' % (p, len(rs)))
        for r in rs:
            print('  |' + r)
