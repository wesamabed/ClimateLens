from etl.transformer.concurrent import ConcurrentTransformer

class DummyReader:
    def __init__(self, data): self._data = data
    def read(self, path): return [{"x": path.name}] if "good" in path.name else []

def test_transformer_parallel(tmp_path):
    # monkeypatch reader
    t = ConcurrentTransformer(max_workers=2)
    t.reader = DummyReader(data=None)
    good = tmp_path/"good1.csv"
    good.write_text("")
    bad  = tmp_path/"bad.csv"
    bad.write_text("")
    paths = [good, bad]
    results = t.transform(paths)
    assert {"x":"good1.csv"} in results
